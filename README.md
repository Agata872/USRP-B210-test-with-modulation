# USRP B210 QPSK / 64-QAM Modem (GNU Radio 3.10 + UHD 4.8)

This repository provides a GNU Radio–based implementation of **QPSK** and **64-QAM** modulation and demodulation using **USRP B210**.  
The project is adapted and extended from the original URSI 2020 repository:

👉 Original repository: https://github.com/alvpr/URSI_2020.git

Compared with the original implementation, this version has been **updated to support newer GNU Radio and UHD releases**, and includes a **fully functional QPSK transceiver**, with **64-QAM currently under testing**.

---

## 📌 Features

- ✅ USRP B210–based SDR implementation
- ✅ GNU Radio **3.10** compatible
- ✅ UHD **4.8** compatible
- ✅ End-to-end **QPSK modulation and demodulation**
- 🚧 **64-QAM modulation/demodulation (work in progress)**
- ✅ GNU Radio Companion (`.grc`) flowgraphs
- ✅ Python control scripts for TX/RX

---
## 📂 Project Structure
```
├── Updated_config/                # GNU Radio Companion flowgraphs
│   ├── QPSK/                       # QPSK modulation and demodulation
│   ├── QAM64/                      # Under testing
├── README.md
```
---
## 🔧 Environment & Requirements

### Hardware
- USRP B210
- Suitable RF front-end (antennas, cables, etc.)

---

### Software
- Ubuntu (tested on recent LTS versions)
- GNU Radio **3.10**
- UHD **4.8**
- Python 3.x
- USRP Hardware Driver properly installed and detected

---
### Pre-requisites
For installation of the out-of-tree firs remove the build folder:
```
cd gr-TFMv5
rm -r build
mkdir build
cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

## 🔍 QPSK Modulation and Decoding Process

---

### 📤 Transmitter Chain (TX)

1. **Random Bit Generation**
   - A pseudo-random byte stream is generated using `vector_source_b`.
   - Bytes are unpacked into bits (`packed_to_unpacked_bb`).

2. **Differential Encoding**
   - Differential encoding (`diff_encoder_bb`) is applied to mitigate phase ambiguity at the receiver.

3. **Symbol Mapping**
   - Bits are mapped to QPSK constellation symbols using `chunks_to_symbols_bc`.
   - Gray-coded QPSK constellation is defined explicitly.

4. **Pulse Shaping & Upsampling**
   - Root Raised Cosine (RRC) filtering is applied using a **polyphase filter bank (PFB) arbitrary resampler**.
   - Samples-per-symbol (SPS) = 4, excess bandwidth = 0.35.

5. **Optional Channel Impairments**
   - A configurable channel model introduces:
     - AWGN
     - Frequency offset
   - This is mainly used for testing and visualization.

6. **USRP Transmission**
   - The shaped baseband signal is transmitted using `uhd_usrp_sink`.
   - Center frequency, sample rate, and TX gain are configurable via GUI.

---

### 📥 Receiver and Decoding Chain (RX)

The receiver performs **timing recovery → equalization → carrier recovery → symbol decoding → bit recovery** in sequence.

#### 1. RF Reception
- Baseband IQ samples are captured using `uhd_usrp_source` from USRP B210.
- RX gain and center frequency match the transmitter.

#### 2. Symbol Timing Recovery
- `digital.symbol_sync_cc` is used for **symbol timing synchronization**.
- A PFB-based matched filter with RRC taps is employed.
- Timing error detector (TED): *Maximum Likelihood (ML)*.
- Loop bandwidth is adjustable in real time via GUI.

#### 3. Adaptive Equalization
- A linear adaptive equalizer (`digital.linear_equalizer`) is applied to combat channel distortion.
- Constant Modulus Algorithm (CMA) is used:
  - Particularly suitable for QPSK signals.
- Equalizer step size is configurable.

#### 4. Carrier Phase Recovery
- A Costas loop (`digital.costas_loop_cc`) performs carrier phase and frequency recovery.
- Loop bandwidth is adjustable to trade off between convergence speed and stability.

#### 5. Constellation Decoding
- The corrected symbols are mapped back to symbol indices using `constellation_decoder_cb`.

#### 6. Differential Decoding
- Differential decoding (`diff_decoder_bb`) resolves residual phase ambiguity (e.g., π/2 rotations).

#### 7. Bit Unpacking & Alignment
- Decoded symbols are unpacked into bits.
- A configurable delay block aligns transmitted and received bit streams for comparison.

---

### 📊 Monitoring and Visualization

Several Qt GUI sinks are used for real-time monitoring:

- **Constellation Plot**
  - Displays post-Costas-loop constellation points.
- **Time-Domain Bit Comparison**
  - TX vs RX bit streams are visualized for correctness checking.
- **Spectrum / Waterfall**
  - TX and RX signals are shown in frequency and time-frequency domains.
- **Signal Power Estimation**
  - Magnitude-squared and moving average blocks estimate received signal power.

---

### 🧠 Design Notes

- Differential QPSK is used to simplify carrier recovery.
- PFB-based symbol synchronization improves robustness against timing errors.
- CMA equalization enables blind adaptation without training sequences.
- The receiver chain is modular and can be extended to higher-order modulations (e.g., 64-QAM).

---

### 📖 References
- Official QPSK Mod and Demod tutorial from the GNURadio wiki:
[link](https://wiki.gnuradio.org/index.php?title=QPSK_Mod_and_Demod)
