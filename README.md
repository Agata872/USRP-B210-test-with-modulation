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

## 🔧 Environment & Requirements

### Hardware
- USRP B210
- Suitable RF front-end (antennas, cables, etc.)

### Software
- Ubuntu (tested on recent LTS versions)
- GNU Radio **3.10**
- UHD **4.8**
- Python 3.x
- USRP Hardware Driver properly installed and detected

To verify your USRP:
```bash
uhd_find_devices
