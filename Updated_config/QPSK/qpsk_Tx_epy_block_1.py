import numpy as np
import pmt
from gnuradio import gr

class bfp_decompress(gr.basic_block):
    """
    Block Floating-Point (BFP) Decompressor (strict dual of bfp_compress)

    Inputs:
        - int16 stream (port 0): I mantissas
        - int16 stream (port 1): Q mantissas

    Output:
        - complex64 stream: x_hat[n] = (I_m[n] + j Q_m[n]) * 2^{e_block}

    Tags:
        - Reads exponent tag at the first item of each block:
            key = tag_key (default "bfp_exp")
            value = exponent (PMT integer)
          This exponent applies to the following 'block_len' mantissa samples.

    Parameters:
        block_len: number of samples per BFP block
        tag_key:   exponent tag key (must match compressor)
        default_exp: exponent to use if tag is missing at a block boundary
    """

    def __init__(self,
                 block_len=12,
                 tag_key="bfp_exp",
                 default_exp=0):

        gr.basic_block.__init__(
            self,
            name="bfp_decompress",
            in_sig=[np.int16, np.int16],
            out_sig=[np.complex64],
        )

        self.block_len = int(block_len)
        if self.block_len <= 0:
            raise ValueError("block_len must be > 0")

        self.tag_key = pmt.intern(tag_key)
        self.default_exp = int(default_exp)

        # Prefer block-aligned scheduling
        self.set_output_multiple(self.block_len)

        # Buffer for input mantissas (since GNU Radio may call us with arbitrary chunk sizes)
        self._buf_I = np.empty(0, dtype=np.int16)
        self._buf_Q = np.empty(0, dtype=np.int16)

        # Keep track of the current exponent for the current block
        self._cur_exp = self.default_exp

    def forecast(self, noutput_items, ninput_items_required):
        # We need the same number of I/Q mantissa samples as output items
        ninput_items_required[0] = noutput_items
        ninput_items_required[1] = noutput_items

    def _read_exp_tag_at_offset(self, abs_in_offset: int) -> int:
        """
        Look for exponent tag at an absolute input offset.
        We check port 0 tags (I stream). In the compressor we tagged both ports,
        but reading from one port is sufficient and avoids duplicate/conflict issues.
        """
        tags = []
        self.get_tags_in_range(tags, 0, abs_in_offset, abs_in_offset + 1, self.tag_key)
        if len(tags) == 0:
            return self.default_exp

        # If multiple tags exist (shouldn't happen), take the last one
        t = tags[-1]
        try:
            return int(pmt.to_long(t.value))
        except Exception:
            # Fallback if tag value isn't a PMT integer
            return self.default_exp

    def general_work(self, input_items, output_items):
        I_in = input_items[0]
        Q_in = input_items[1]
        y = output_items[0]

        # Append to internal buffers
        if I_in.size > 0:
            self._buf_I = np.concatenate([self._buf_I, I_in.astype(np.int16, copy=False)])
        if Q_in.size > 0:
            self._buf_Q = np.concatenate([self._buf_Q, Q_in.astype(np.int16, copy=False)])

        # Keep I/Q aligned: only process what we have in both buffers
        n_avail = min(self._buf_I.size, self._buf_Q.size)
        if n_avail < self.block_len:
            # Not enough for one full block
            self.consume(0, I_in.size)
            self.consume(1, Q_in.size)
            return 0

        # Number of full blocks available in buffers
        n_blocks_available = n_avail // self.block_len
        if n_blocks_available <= 0:
            self.consume(0, I_in.size)
            self.consume(1, Q_in.size)
            return 0

        # Output capacity
        max_blocks_by_out = y.size // self.block_len
        n_blocks = min(n_blocks_available, max_blocks_by_out)
        if n_blocks <= 0:
            self.consume(0, I_in.size)
            self.consume(1, Q_in.size)
            return 0

        n_items = n_blocks * self.block_len

        # Absolute input start offset for port 0 (I stream)
        abs_in_start = self.nitems_read(0)

        # Process per block
        for b in range(n_blocks):
            s = b * self.block_len

            # Read exponent tag at block boundary (absolute offset in input stream)
            e = self._read_exp_tag_at_offset(abs_in_start + s)
            self._cur_exp = e  # store for debug if needed

            # Reconstruct float values: x_hat = mantissa * 2^{e}
            scale = 2.0 ** (e)

            I_blk = self._buf_I[s:s + self.block_len].astype(np.float32) * scale
            Q_blk = self._buf_Q[s:s + self.block_len].astype(np.float32) * scale

            y[s:s + self.block_len] = (I_blk + 1j * Q_blk).astype(np.complex64)

        # Drop processed items from buffers
        self._buf_I = self._buf_I[n_items:]
        self._buf_Q = self._buf_Q[n_items:]

        # Consume all newly arrived items (we buffered them already)
        self.consume(0, I_in.size)
        self.consume(1, Q_in.size)

        return n_items
