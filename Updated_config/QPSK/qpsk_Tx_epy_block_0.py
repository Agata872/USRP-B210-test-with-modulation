import numpy as np
import pmt
from gnuradio import gr

class bfp_compress(gr.basic_block):
    """
    Block Floating-Point (BFP) Compressor (theory-aligned)

    Input:
        - complex64 stream: x[n] = I[n] + j Q[n]

    Output:
        - int16 stream (port 0): I mantissas
        - int16 stream (port 1): Q mantissas

    Tags:
        - At the first output item of each block, add tag:
            key = tag_key (default "bfp_exp")
            value = exponent (PMT integer)
          This exponent applies to the following 'block_len' mantissa samples.

    Theory (per block):
        Let maxValue = max over samples in the block of max(|I|, |Q|).
        exponent e chosen so that after scaling, mantissa fits in signed m-bit range.

        We quantize mantissa as:
            mI = round(I * 2^{-e})
            mQ = round(Q * 2^{-e})
        then clip to representable range:
            m ∈ [-(2^{m-1}), 2^{m-1}-1]

    Parameters:
        block_len:         number of complex samples per BFP block
        mantissa_bits:     signed mantissa bit width (including sign), e.g., 8
        exponent_bits:     exponent bit width (typ. 4 in O-RAN udCompParam low nibble)
        tag_key:           PMT tag key to store exponent at block boundaries
        eps:               small positive floor to avoid log2(0)
    """

    def __init__(self,
                 block_len=12,
                 mantissa_bits=8,
                 exponent_bits=4,
                 tag_key="bfp_exp",
                 eps=1e-12):

        gr.basic_block.__init__(
            self,
            name="bfp_compress",
            in_sig=[np.complex64],
            out_sig=[np.int16, np.int16],
        )

        # Parameters
        self.block_len = int(block_len)
        self.mantissa_bits = int(mantissa_bits)
        self.exponent_bits = int(exponent_bits)
        self.eps = float(eps)

        if self.block_len <= 0:
            raise ValueError("block_len must be > 0")
        if self.mantissa_bits < 2:
            raise ValueError("mantissa_bits must be >= 2 (needs sign + magnitude)")
        if self.exponent_bits <= 0:
            raise ValueError("exponent_bits must be > 0")

        # mantissa representable range for signed m-bit integer
        self.m_min = -(2 ** (self.mantissa_bits - 1))
        self.m_max =  (2 ** (self.mantissa_bits - 1)) - 1

        # exponent range (e.g., 0..15 for 4-bit exponent)
        self.e_min = 0
        self.e_max = (2 ** self.exponent_bits) - 1

        # tag key
        self.tag_key = pmt.intern(tag_key)

        # Scheduler hints: we prefer operating on full blocks
        self.set_output_multiple(self.block_len)

        # Internal buffer for blockwise processing (input samples not yet emitted)
        self._buf = np.empty(0, dtype=np.complex64)

    def forecast(self, noutput_items, ninput_items_required):
        """
        To produce noutput_items, we need at least noutput_items input samples
        (1:1 mapping). We will only actually produce multiples of block_len.
        """
        ninput_items_required[0] = noutput_items

    def _compute_exponent(self, block: np.ndarray) -> int:
        """
        Compute exponent e for the block, theory-aligned:

        We want |I| * 2^{-e} <= m_max and |Q| * 2^{-e} <= m_max
        for all samples in the block.

        Equivalent:
            2^{-e} <= m_max / maxValue
            e >= log2(maxValue / m_max)

        Choose:
            e = ceil(log2(maxValue / m_max)), clipped to [e_min, e_max]
        Also if maxValue ~ 0, pick e=0.
        """
        I = np.abs(block.real)
        Q = np.abs(block.imag)
        maxValue = float(np.max(np.maximum(I, Q)))

        if maxValue <= self.eps:
            return 0

        # e = ceil(log2(maxValue / m_max))
        e = int(np.ceil(np.log2(maxValue / float(self.m_max))))

        # clamp exponent into allowed range
        if e < self.e_min:
            e = self.e_min
        if e > self.e_max:
            e = self.e_max
        return e

    def general_work(self, input_items, output_items):
        x_in = input_items[0]
        yI = output_items[0]
        yQ = output_items[1]

        # Append new input to buffer
        if x_in.size > 0:
            self._buf = np.concatenate([self._buf, x_in.astype(np.complex64, copy=False)])

        # We only output full blocks
        n_blocks_available = self._buf.size // self.block_len
        if n_blocks_available <= 0:
            # Need more input before producing output
            self.consume(0, x_in.size)
            return 0

        # How many blocks can we actually output this call (limited by output buffers)
        max_blocks_by_out = min(
            yI.size // self.block_len,
            yQ.size // self.block_len
        )
        n_blocks = min(n_blocks_available, max_blocks_by_out)

        if n_blocks <= 0:
            self.consume(0, x_in.size)
            return 0

        n_items = n_blocks * self.block_len

        # Take blocks to process
        buf_use = self._buf[:n_items]
        buf_remain = self._buf[n_items:]  # keep leftover for next call

        # Process each block: exponent + mantissa quantization
        # Tagging: one exponent tag at each block start
        # Compute absolute output item offset for tagging
        abs_out_start = self.nitems_written(0)

        for b in range(n_blocks):
            s = b * self.block_len
            e = self._compute_exponent(buf_use[s:s + self.block_len])

            # scale factor for mantissa quantization: m = round(x * 2^{-e})
            scale = 2.0 ** (-e)

            I_scaled = np.round(buf_use[s:s + self.block_len].real * scale)
            Q_scaled = np.round(buf_use[s:s + self.block_len].imag * scale)

            # clip to mantissa range and cast to int16
            I_m = np.clip(I_scaled, self.m_min, self.m_max).astype(np.int16, copy=False)
            Q_m = np.clip(Q_scaled, self.m_min, self.m_max).astype(np.int16, copy=False)

            yI[s:s + self.block_len] = I_m
            yQ[s:s + self.block_len] = Q_m

            # Add exponent tag at block boundary on BOTH output ports
            tag_offset = abs_out_start + s
            tag_val = pmt.from_long(int(e))
            self.add_item_tag(0, tag_offset, self.tag_key, tag_val)
            self.add_item_tag(1, tag_offset, self.tag_key, tag_val)

        # Update buffer (remove processed)
        self._buf = buf_remain

        # Consume exactly n_items from input stream
        # But we already appended ALL x_in to buffer, so consume x_in fully
        # and rely on buffer to handle leftovers.
        self.consume(0, x_in.size)

        # Produced n_items per output
        return n_items
