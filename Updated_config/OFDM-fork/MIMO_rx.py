#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: MIMO_rx
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import sip
import threading



class MIMO_rx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "MIMO_rx", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("MIMO_rx")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "MIMO_rx")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.pilot_symbols = pilot_symbols = ((1, 1, 1, -1,),)
        self.pilot_carriers = pilot_carriers = ((-21, -7, 7, 21,),)
        self.payload_mod = payload_mod = digital.constellation_qpsk()
        self.packet_length_tag_key = packet_length_tag_key = "packet_len"
        self.occupied_carriers = occupied_carriers = (list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0)) + list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)),)
        self.length_tag_key1 = length_tag_key1 = "frame_len"
        self.length_tag_key = length_tag_key = "packet_len"
        self.header_mod = header_mod = digital.constellation_bpsk()
        self.fft_len = fft_len = 64
        self.sync_word5 = sync_word5 = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, -1, 1, 1, -1, 1, 0, -1, 1, -1, -1, -1, 1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        self.sync_word4 = sync_word4 = [0, 0, 0, 0, 0, 0, -1, -1, -1, -1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, -1, 0, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, 1, -1, -1, -1, -1, 0, 0, 0, 0, 0]
        self.sync_word3 = sync_word3 = [0, 0, 0, 0, 0, 0, -1, -1, -1, -1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, -1, 0, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, 1, -1, -1, -1, -1, 0, 0, 0, 0, 0]
        self.sync_word2 = sync_word2 = [0, 0, 0, 0, 0, 0, -1, -1, -1, -1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, -1, 0, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, 1, -1, -1, -1, -1, 0, 0, 0, 0, 0]
        self.sync_word1 = sync_word1 = [0., 0., 0., 0., 0., 0., 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., -1.41421356, 0., -1.41421356, 0., -1.41421356, 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., -1.41421356, 0., -1.41421356, 0., -1.41421356, 0., -1.41421356, 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., 1.41421356, 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., 1.41421356, 0., 1.41421356, 0., -1.41421356, 0., 1.41421356, 0., 1.41421356, 0., 1.41421356, 0., 0., 0., 0., 0., 0.]
        self.samp_rate = samp_rate = 1000000
        self.rolloff = rolloff = 0
        self.payload_equalizer = payload_equalizer = digital.ofdm_equalizer_simpledfe(fft_len, payload_mod.base(), occupied_carriers, pilot_carriers, pilot_symbols, 1)
        self.packet_len = packet_len = 96
        self.header_formatter = header_formatter = digital.packet_header_ofdm(occupied_carriers, n_syms=1, len_tag_key=packet_length_tag_key, frame_len_tag_key=length_tag_key1, bits_per_header_sym=header_mod.bits_per_symbol(), bits_per_payload_sym=payload_mod.bits_per_symbol(), scramble_header=False)
        self.header_equalizer = header_equalizer = digital.ofdm_equalizer_simpledfe(fft_len, header_mod.base(), occupied_carriers, pilot_carriers, pilot_symbols)
        self.hdr_format = hdr_format = digital.header_format_ofdm(occupied_carriers, 1, length_tag_key,)
        self.gain = gain = 50
        self.centre_fre = centre_fre = 920e6
        self.center_freq = center_freq = 5e8

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0_0 = uhd.usrp_source(
            ",".join(("serial=31D4A23", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_source_0_0.set_center_freq(centre_fre, 0)
        self.uhd_usrp_source_0_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_source_0_0.set_gain(gain, 0)
        self.uhd_usrp_source_0_0.set_auto_dc_offset(False, 0)
        self.uhd_usrp_source_0_0.set_auto_iq_balance(False, 0)
        self.qtgui_time_sink_x_0_1_2 = qtgui.time_sink_c(
            1024, #size
            samp_rate, #samp_rate
            'Scope Plot', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_1_2.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1_2.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1_2.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_1_2.enable_tags(True)
        self.qtgui_time_sink_x_0_1_2.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_1_2.enable_autoscale(True)
        self.qtgui_time_sink_x_0_1_2.enable_grid(False)
        self.qtgui_time_sink_x_0_1_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1_2.enable_control_panel(False)
        self.qtgui_time_sink_x_0_1_2.enable_stem_plot(False)


        labels = ['Scope Plot', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_1_2.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_1_2.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_1_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_2_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1_2.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_1_2_win)
        self.qtgui_time_sink_x_0_1_0_1 = qtgui.time_sink_c(
            1024, #size
            samp_rate, #samp_rate
            'Scope Plot', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_1_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_1_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_1_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_1_0_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_1_0_1.enable_grid(False)
        self.qtgui_time_sink_x_0_1_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_1_0_1.enable_stem_plot(False)


        labels = ['Scope Plot', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_1_0_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_1_0_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_1_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1_0_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_1_0_1_win)
        self.qtgui_const_sink_x_0_0_0_2_1_0_0 = qtgui.const_sink_c(
            256, #size
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_y_axis((-1.5), 1.5)
        self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_x_axis((-1.5), 1.5)
        self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0_0_0_2_1_0_0.enable_autoscale(True)
        self.qtgui_const_sink_x_0_0_0_2_1_0_0.enable_grid(False)
        self.qtgui_const_sink_x_0_0_0_2_1_0_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0_0_0_2_1_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_0_0_2_1_0_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0_0_0_2_1_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_0_0_2_1_0_0_win)
        self.qtgui_const_sink_x_0_0_0_2_0 = qtgui.const_sink_c(
            256, #size
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0_0_0_2_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0_0_0_2_0.set_y_axis((-1.5), 1.5)
        self.qtgui_const_sink_x_0_0_0_2_0.set_x_axis((-1.5), 1.5)
        self.qtgui_const_sink_x_0_0_0_2_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0_0_0_2_0.enable_autoscale(True)
        self.qtgui_const_sink_x_0_0_0_2_0.enable_grid(False)
        self.qtgui_const_sink_x_0_0_0_2_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0_0_0_2_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0_0_0_2_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0_0_0_2_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0_0_0_2_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0_0_0_2_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0_0_0_2_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0_0_0_2_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_0_0_2_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0_0_0_2_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_0_0_2_0_win)
        self.fft_vxx_1_1 = fft.fft_vcc(fft_len, True, (), True, 1)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_len, True, (), True, 1)
        self.digital_packet_headerparser_b_0_1 = digital.packet_headerparser_b(header_formatter.base())
        self.digital_ofdm_sync_sc_cfb_0_1 = digital.ofdm_sync_sc_cfb(fft_len, (int(fft_len/4)), False, 0.9)
        self.digital_ofdm_serializer_vcc_payload_0 = digital.ofdm_serializer_vcc(fft_len, occupied_carriers, length_tag_key1, packet_length_tag_key, 1, '', True)
        self.digital_ofdm_serializer_vcc_header_1 = digital.ofdm_serializer_vcc(fft_len, occupied_carriers, length_tag_key1, '', 0, '', True)
        self.digital_ofdm_frame_equalizer_vcvc_1_0 = digital.ofdm_frame_equalizer_vcvc(payload_equalizer.base(), (int(fft_len/4)), length_tag_key1, True, 0)
        self.digital_ofdm_frame_equalizer_vcvc_0_0 = digital.ofdm_frame_equalizer_vcvc(header_equalizer.base(), (int(fft_len/4)), length_tag_key1, True, 1)
        self.digital_ofdm_chanest_vcvc_0_0 = digital.ofdm_chanest_vcvc(sync_word1, sync_word2, 1, 0, 3, False)
        self.digital_header_payload_demux_0_1 = digital.header_payload_demux(
            4,
            fft_len,
            (int(fft_len/4)),
            length_tag_key1,
            "",
            True,
            gr.sizeof_gr_complex,
            "rx_time",
            samp_rate,
            (),
            0)
        self.digital_constellation_decoder_cb_0_1 = digital.constellation_decoder_cb(header_mod.base())
        self.blocks_multiply_xx_0_1 = blocks.multiply_vcc(1)
        self.blocks_delay_0_1 = blocks.delay(gr.sizeof_gr_complex*1, (int(fft_len+fft_len/4)))
        self.analog_frequency_modulator_fc_0_1 = analog.frequency_modulator_fc((-2.0/fft_len))


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.digital_packet_headerparser_b_0_1, 'header_data'), (self.digital_header_payload_demux_0_1, 'header_data'))
        self.connect((self.analog_frequency_modulator_fc_0_1, 0), (self.blocks_multiply_xx_0_1, 0))
        self.connect((self.blocks_delay_0_1, 0), (self.blocks_multiply_xx_0_1, 1))
        self.connect((self.blocks_multiply_xx_0_1, 0), (self.digital_header_payload_demux_0_1, 0))
        self.connect((self.digital_constellation_decoder_cb_0_1, 0), (self.digital_packet_headerparser_b_0_1, 0))
        self.connect((self.digital_header_payload_demux_0_1, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.digital_header_payload_demux_0_1, 1), (self.fft_vxx_1_1, 0))
        self.connect((self.digital_ofdm_chanest_vcvc_0_0, 0), (self.digital_ofdm_frame_equalizer_vcvc_0_0, 0))
        self.connect((self.digital_ofdm_frame_equalizer_vcvc_0_0, 0), (self.digital_ofdm_serializer_vcc_header_1, 0))
        self.connect((self.digital_ofdm_frame_equalizer_vcvc_1_0, 0), (self.digital_ofdm_serializer_vcc_payload_0, 0))
        self.connect((self.digital_ofdm_serializer_vcc_header_1, 0), (self.digital_constellation_decoder_cb_0_1, 0))
        self.connect((self.digital_ofdm_serializer_vcc_header_1, 0), (self.qtgui_const_sink_x_0_0_0_2_1_0_0, 0))
        self.connect((self.digital_ofdm_serializer_vcc_header_1, 0), (self.qtgui_time_sink_x_0_1_0_1, 0))
        self.connect((self.digital_ofdm_serializer_vcc_payload_0, 0), (self.qtgui_const_sink_x_0_0_0_2_0, 0))
        self.connect((self.digital_ofdm_serializer_vcc_payload_0, 0), (self.qtgui_time_sink_x_0_1_2, 0))
        self.connect((self.digital_ofdm_sync_sc_cfb_0_1, 0), (self.analog_frequency_modulator_fc_0_1, 0))
        self.connect((self.digital_ofdm_sync_sc_cfb_0_1, 1), (self.digital_header_payload_demux_0_1, 1))
        self.connect((self.fft_vxx_0_0, 0), (self.digital_ofdm_chanest_vcvc_0_0, 0))
        self.connect((self.fft_vxx_1_1, 0), (self.digital_ofdm_frame_equalizer_vcvc_1_0, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.blocks_delay_0_1, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.digital_ofdm_sync_sc_cfb_0_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "MIMO_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_pilot_symbols(self):
        return self.pilot_symbols

    def set_pilot_symbols(self, pilot_symbols):
        self.pilot_symbols = pilot_symbols
        self.set_header_equalizer(digital.ofdm_equalizer_simpledfe(self.fft_len, header_mod.base(), self.occupied_carriers, self.pilot_carriers, self.pilot_symbols))
        self.set_payload_equalizer(digital.ofdm_equalizer_simpledfe(self.fft_len, payload_mod.base(), self.occupied_carriers, self.pilot_carriers, self.pilot_symbols, 1))

    def get_pilot_carriers(self):
        return self.pilot_carriers

    def set_pilot_carriers(self, pilot_carriers):
        self.pilot_carriers = pilot_carriers
        self.set_header_equalizer(digital.ofdm_equalizer_simpledfe(self.fft_len, header_mod.base(), self.occupied_carriers, self.pilot_carriers, self.pilot_symbols))
        self.set_payload_equalizer(digital.ofdm_equalizer_simpledfe(self.fft_len, payload_mod.base(), self.occupied_carriers, self.pilot_carriers, self.pilot_symbols, 1))

    def get_payload_mod(self):
        return self.payload_mod

    def set_payload_mod(self, payload_mod):
        self.payload_mod = payload_mod

    def get_packet_length_tag_key(self):
        return self.packet_length_tag_key

    def set_packet_length_tag_key(self, packet_length_tag_key):
        self.packet_length_tag_key = packet_length_tag_key
        self.set_header_formatter(digital.packet_header_ofdm(self.occupied_carriers, n_syms=1, len_tag_key=self.packet_length_tag_key, frame_len_tag_key=self.length_tag_key1, bits_per_header_sym=header_mod.bits_per_symbol(), bits_per_payload_sym=payload_mod.bits_per_symbol(), scramble_header=False))

    def get_occupied_carriers(self):
        return self.occupied_carriers

    def set_occupied_carriers(self, occupied_carriers):
        self.occupied_carriers = occupied_carriers
        self.set_hdr_format(digital.header_format_ofdm(self.occupied_carriers, 1, self.length_tag_key,))
        self.set_header_equalizer(digital.ofdm_equalizer_simpledfe(self.fft_len, header_mod.base(), self.occupied_carriers, self.pilot_carriers, self.pilot_symbols))
        self.set_header_formatter(digital.packet_header_ofdm(self.occupied_carriers, n_syms=1, len_tag_key=self.packet_length_tag_key, frame_len_tag_key=self.length_tag_key1, bits_per_header_sym=header_mod.bits_per_symbol(), bits_per_payload_sym=payload_mod.bits_per_symbol(), scramble_header=False))
        self.set_payload_equalizer(digital.ofdm_equalizer_simpledfe(self.fft_len, payload_mod.base(), self.occupied_carriers, self.pilot_carriers, self.pilot_symbols, 1))

    def get_length_tag_key1(self):
        return self.length_tag_key1

    def set_length_tag_key1(self, length_tag_key1):
        self.length_tag_key1 = length_tag_key1
        self.set_header_formatter(digital.packet_header_ofdm(self.occupied_carriers, n_syms=1, len_tag_key=self.packet_length_tag_key, frame_len_tag_key=self.length_tag_key1, bits_per_header_sym=header_mod.bits_per_symbol(), bits_per_payload_sym=payload_mod.bits_per_symbol(), scramble_header=False))

    def get_length_tag_key(self):
        return self.length_tag_key

    def set_length_tag_key(self, length_tag_key):
        self.length_tag_key = length_tag_key
        self.set_hdr_format(digital.header_format_ofdm(self.occupied_carriers, 1, self.length_tag_key,))

    def get_header_mod(self):
        return self.header_mod

    def set_header_mod(self, header_mod):
        self.header_mod = header_mod

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_header_equalizer(digital.ofdm_equalizer_simpledfe(self.fft_len, header_mod.base(), self.occupied_carriers, self.pilot_carriers, self.pilot_symbols))
        self.set_payload_equalizer(digital.ofdm_equalizer_simpledfe(self.fft_len, payload_mod.base(), self.occupied_carriers, self.pilot_carriers, self.pilot_symbols, 1))
        self.analog_frequency_modulator_fc_0_1.set_sensitivity((-2.0/self.fft_len))
        self.blocks_delay_0_1.set_dly(int((int(self.fft_len+self.fft_len/4))))

    def get_sync_word5(self):
        return self.sync_word5

    def set_sync_word5(self, sync_word5):
        self.sync_word5 = sync_word5

    def get_sync_word4(self):
        return self.sync_word4

    def set_sync_word4(self, sync_word4):
        self.sync_word4 = sync_word4

    def get_sync_word3(self):
        return self.sync_word3

    def set_sync_word3(self, sync_word3):
        self.sync_word3 = sync_word3

    def get_sync_word2(self):
        return self.sync_word2

    def set_sync_word2(self, sync_word2):
        self.sync_word2 = sync_word2

    def get_sync_word1(self):
        return self.sync_word1

    def set_sync_word1(self, sync_word1):
        self.sync_word1 = sync_word1

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_1_2.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_1_0_1.set_samp_rate(self.samp_rate)

    def get_rolloff(self):
        return self.rolloff

    def set_rolloff(self, rolloff):
        self.rolloff = rolloff

    def get_payload_equalizer(self):
        return self.payload_equalizer

    def set_payload_equalizer(self, payload_equalizer):
        self.payload_equalizer = payload_equalizer

    def get_packet_len(self):
        return self.packet_len

    def set_packet_len(self, packet_len):
        self.packet_len = packet_len

    def get_header_formatter(self):
        return self.header_formatter

    def set_header_formatter(self, header_formatter):
        self.header_formatter = header_formatter

    def get_header_equalizer(self):
        return self.header_equalizer

    def set_header_equalizer(self, header_equalizer):
        self.header_equalizer = header_equalizer

    def get_hdr_format(self):
        return self.hdr_format

    def set_hdr_format(self, hdr_format):
        self.hdr_format = hdr_format

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_source_0_0.set_gain(self.gain, 0)

    def get_centre_fre(self):
        return self.centre_fre

    def set_centre_fre(self, centre_fre):
        self.centre_fre = centre_fre
        self.uhd_usrp_source_0_0.set_center_freq(self.centre_fre, 0)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq




def main(top_block_cls=MIMO_rx, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
