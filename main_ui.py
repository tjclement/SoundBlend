from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLineEdit, QComboBox, \
    QSpinBox, QGridLayout, QHBoxLayout, QFormLayout, QCheckBox, \
    QToolButton, QLabel, QStyle, QVBoxLayout
from pyqt5_plugins.examplebuttonplugin import QtGui


class MainUI(QWidget):
    def __init__(self):
        super(MainUI, self).__init__()

        self.button_save = QToolButton()
        self.button_save.setIcon(self.style().standardIcon(getattr(QStyle, "SP_DialogSaveButton")))
        self.button_open = QToolButton()
        self.button_open.setIcon(self.style().standardIcon(getattr(QStyle, "SP_DirIcon")))
        self.choice_outputs = QComboBox()
        self.choice_inputs = QComboBox()

        self.input_path = QLineEdit()
        self.input_path.setMinimumWidth(200)
        self.button_path = QToolButton()
        self.button_path.setText("...")
        self.input_on_note = QLineEdit()
        self.input_gain = QSpinBox()
        self.input_gain.setMinimum(-60)
        self.input_fade_in = QSpinBox()
        self.input_fade_in.setMaximum(9999)
        self.input_fade_out = QSpinBox()
        self.input_fade_out.setMaximum(9999)
        self.check_remove_silence = QCheckBox()
        self.check_loop = QCheckBox()
        self.input_skip_start = QSpinBox()
        self.input_skip_start.setMaximum(999999)
        self.input_skip_end = QSpinBox()
        self.input_skip_end.setMaximum(999999)
        self.choice_play_mode = QComboBox()
        self.choice_play_mode.addItems(["single", "multi", "hold", "toggle"])
        self.buttons = [QToolButton() for i in range(16)]
        self.code = ""

        top = QHBoxLayout()
        top.addWidget(self.button_save)
        top.addWidget(self.button_open)
        label_output = QLabel("Sound output")
        label_output.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top.addWidget(label_output)
        top.addWidget(self.choice_outputs)
        label_input = QLabel("MIDI input")
        label_input.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top.addWidget(label_input)
        top.addWidget(self.choice_inputs)

        grid = QGridLayout()
        for i in range(4):
            for j in range(4):
                grid.addWidget(self.buttons[j * 4 + i], j, i)

        form = QFormLayout()
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.input_path)
        path_layout.addWidget(self.button_path)
        form.addRow("Path to sample", path_layout)
        form.addRow("MIDI note", self.input_on_note)
        form.addRow("Play mode", self.choice_play_mode)
        form.addRow("Gain (dB)", self.input_gain)
        fade_layout = QHBoxLayout()
        fade_layout.addWidget(QLabel("in"))
        fade_layout.addWidget(self.input_fade_in)
        fade_layout.addWidget(QLabel("out"))
        fade_layout.addWidget(self.input_fade_out)
        form.addRow("Fade (ms)", fade_layout)
        form.addRow("Auto-remove silence", self.check_remove_silence)
        form.addRow("Loop", self.check_loop)
        skip_layout = QHBoxLayout()
        skip_layout.addWidget(QLabel("start"))
        skip_layout.addWidget(self.input_skip_start)
        skip_layout.addWidget(QLabel("end"))
        skip_layout.addWidget(self.input_skip_end)
        form.addRow("Skip (ms)", skip_layout)

        bottom = QHBoxLayout()
        bottom.addLayout(grid)
        bottom.addLayout(form)

        self.setLayout(QVBoxLayout())
        self.layout().addLayout(top)
        self.layout().addLayout(bottom)

        self.setWindowTitle("SoundBlend")
        self.center()
        self.show()

        self.timer = QTimer()
        self.timer.start(10)
        self.setFocus()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_settings_change(self, callback):
        signals = [self.input_path.textChanged, self.input_on_note.textChanged,
                   self.choice_play_mode.currentTextChanged,
                   self.input_gain.valueChanged, self.input_fade_in.valueChanged, self.input_fade_out.valueChanged,
                   self.check_remove_silence.stateChanged, self.check_loop.stateChanged,
                   self.input_skip_start.valueChanged,
                   self.input_skip_end.valueChanged]

        for signal in signals:
            signal.connect(callback)

    def on_grid_press(self, callback):
        for index, button in enumerate(self.buttons):
            button.clicked.connect(lambda _, note=(60 + index): callback(note))

    def on_tick(self, callback):
        self.timer.timeout.connect(callback)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        map = {
            Qt.Key_Up: "u",
            Qt.Key_Down: "d",
            Qt.Key_Left: "l",
            Qt.Key_Right: "r",
            Qt.Key_A: "a",
            Qt.Key_B: "b",
        }
        if event.key() in map.keys():
            self.code += map[event.key()]
            if len(self.code) > 10:
                self.code = self.code[:-10]
            if self.code == "uuddlrlrba":
                import random
                import webbrowser
                v = random.choice(["6Lle4lKh9YE&t=39s", "l2yYauKujfM&t=29s"])
                webbrowser.open(f"https://youtu.be/{v}")
