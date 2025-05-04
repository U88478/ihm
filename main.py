import os
import sys
import time

from PyQt5.QtCore import QSettings, QTimer, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QAction, QFileDialog, QToolBar,
    QSpinBox, QDoubleSpinBox, QPushButton, QButtonGroup, QVBoxLayout,
    QHBoxLayout, QLayout, QStackedWidget
)

from gui.instruments.instrument import note_to_frequency
from gui.instruments.piano import Piano
from gui.instruments.videogame import VideoGame
from gui.instruments.xylophone import Xylophone


class DynamicStackedWidget(QStackedWidget):
    def sizeHint(self):
        current = self.currentWidget()
        return current.sizeHint() if current else super().sizeHint()

    def minimumSizeHint(self):
        return self.sizeHint()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projet")
        self.settings = QSettings("IHM", "ProjetFinal")

        # Fixed click durations
        self.click_durations = {
            'piano': float(self.settings.value('click_piano', 0.5)),
            'xylophone': float(self.settings.value('click_xylophone', 0.5)),
            'videogame': float(self.settings.value('click_videogame', 0.1)),
        }

        # State flags
        self.recording = False
        self.playing = False
        self.record_events = []
        self.tempo_factor = 1.0

        # UI setup
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_central_widget()
        self._load_settings()

        # Disable Stop until needed
        self.stopAction.setEnabled(False)

    def _create_actions(self):
        self.openAction = QAction(QIcon("icons/open.png"), "Ouvrir", self)
        self.openAction.triggered.connect(self.open_partition)
        self.openAction.setShortcut(QKeySequence("Ctrl+O"))

        self.recordAction = QAction(QIcon("icons/record.png"), "Enregistrer", self)
        self.recordAction.triggered.connect(self.start_recording)
        self.recordAction.setShortcut(QKeySequence("Ctrl+S"))

        self.stopAction = QAction(QIcon("icons/stop.png"), "Stop", self)
        self.stopAction.triggered.connect(self.stop_all)
        self.stopAction.setShortcut(QKeySequence("Ctrl+T"))

        self.quitAction = QAction(QIcon("icons/quit.png"), "Quitter", self)
        self.quitAction.triggered.connect(QApplication.instance().quit)
        self.quitAction.setShortcut(QKeySequence("Ctrl+Q"))

    def _create_menu(self):
        file_menu = self.menuBar().addMenu("Fichier")
        file_menu.addAction(self.openAction)
        file_menu.addAction(self.recordAction)
        file_menu.addAction(self.stopAction)
        file_menu.addSeparator()
        file_menu.addAction(self.quitAction)

    def _create_toolbar(self):
        toolbar = QToolBar("Fichier", self)
        self.addToolBar(toolbar)
        toolbar.addAction(self.openAction)
        toolbar.addAction(self.recordAction)
        toolbar.addAction(self.stopAction)
        toolbar.addSeparator()

        self.spin_octaves = QSpinBox()
        self.spin_octaves.setRange(1, 3)
        self.spin_octaves.setPrefix("Octaves: ")
        self.spin_octaves.valueChanged.connect(self.change_octaves)
        toolbar.addWidget(self.spin_octaves)
        toolbar.addSeparator()

        self.tempo_spin = QDoubleSpinBox()
        self.tempo_spin.setRange(0.5, 3.0)
        self.tempo_spin.setSingleStep(0.1)
        self.tempo_spin.setPrefix("Tempo: ")
        self.tempo_spin.setValue(1.0)
        self.tempo_spin.valueChanged.connect(lambda v: setattr(self, 'tempo_factor', v))
        toolbar.addWidget(self.tempo_spin)

    def _create_central_widget(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        btn_layout = QHBoxLayout()
        self.btn_group = QButtonGroup(self)
        for name, idx in [("Piano", 0), ("Xylophone", 1), ("Video Game", 2)]:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, i=idx: self.switch_instrument(i))
            self.btn_group.addButton(btn, idx)
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        self.stack = DynamicStackedWidget()
        self.piano = Piano(octaves=self.spin_octaves.value())
        self.xylophone = Xylophone()
        self.videogame = VideoGame()
        for widget in (self.piano, self.xylophone, self.videogame):
            self.stack.addWidget(widget)
        layout.addWidget(self.stack)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self.adjustSize()

    def _load_settings(self):
        octaves = int(self.settings.value('octaves', 1))
        instrument = int(self.settings.value('instrument', 0))
        self.spin_octaves.setValue(octaves)
        self.btn_group.button(instrument).setChecked(True)
        self.switch_instrument(instrument)

    # Partition playback
    def open_partition(self):
        start_dir = "partitions" if os.path.isdir("partitions") else ""
        path, _ = QFileDialog.getOpenFileName(self, "Ouvrir partition", start_dir, "Text Files (*.txt)")
        if not path:
            return
        sequence = []
        with open(path) as f:
            for line in f:
                text = line.strip()
                if not text:
                    continue
                parts = text.split()
                note = parts[0]
                duration = float(parts[1]) if len(parts) > 1 else self.click_durations['piano']
                sequence.append((note, duration))
        self.playing = True
        self.recordAction.setEnabled(False)
        self.stopAction.setEnabled(True)
        self.play_sequence(sequence, 0)

    def play_sequence(self, sequence, index):
        if not self.playing or index >= len(sequence):
            self.playing = False
            self.openAction.setEnabled(True)
            self.stopAction.setEnabled(False)
            self.recordAction.setEnabled(True)
            return
        note, duration = sequence[index]
        duration /= self.tempo_factor
        current = self.stack.currentIndex()
        freq = None
        if note != '0':
            freqs = note_to_frequency.get(note)
            if isinstance(freqs, int):
                freq = freqs
            elif freqs:
                freq = freqs[self.piano.octaves - 1] if current == 0 else freqs[0]
        if freq is not None:
            if current == 0:
                self.piano.player.play_piano_tone(freq, duration)
            elif current == 1:
                self.xylophone.player.play_xylophone_tone(freq, duration)
            else:
                self.videogame.player.play_videoGame_tone(freq, duration)
        QTimer.singleShot(int(duration * 1000), lambda: self.play_sequence(sequence, index + 1))

    # Recording
    def start_recording(self):
        if self.recording or self.playing:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer morceau", "", "Text Files (*.txt)")
        if not path:
            return
        self.record_events.clear()
        self.record_path = path
        self.recording = True
        for widget in (self.piano, self.xylophone, self.videogame):
            widget.notePlayed.connect(self._capture_event)
        self.recordAction.setEnabled(False)
        self.openAction.setEnabled(False)
        self.stopAction.setEnabled(True)

    def _capture_event(self, note, timestamp):
        if self.recording:
            self.record_events.append((note, timestamp, self.stack.currentIndex()))

    def stop_all(self):
        if self.recording:
            for widget in (self.piano, self.xylophone, self.videogame):
                widget.notePlayed.disconnect(self._capture_event)
            with open(self.record_path, 'w') as f:
                prev_time = self.record_events[0][1] if self.record_events else time.time()
                for note, t, inst in self.record_events:
                    delta = t - prev_time
                    click = self.click_durations[['piano', 'xylophone', 'videogame'][inst]]
                    if delta > click:
                        f.write(f"0 {delta - click:.4f}\n")
                    f.write(f"{note} {click:.4f}\n")
                    prev_time = t
            self.recording = False
            self.record_events.clear()
            self.recordAction.setEnabled(True)
            self.openAction.setEnabled(True)
        if self.playing:
            self.playing = False

    # Keys
    def keyPressEvent(self, event):
        key = event.key()
        current = self.stack.currentIndex()

        if current == 0:
            octave_maps = [
                {Qt.Key_A: 'Do', Qt.Key_S: 'Ré', Qt.Key_D: 'Mi', Qt.Key_F: 'Fa', Qt.Key_G: 'Sol', Qt.Key_H: 'La',
                 Qt.Key_J: 'Si'},
                {Qt.Key_Q: 'Do', Qt.Key_W: 'Ré', Qt.Key_E: 'Mi', Qt.Key_R: 'Fa', Qt.Key_T: 'Sol', Qt.Key_Y: 'La',
                 Qt.Key_U: 'Si'},
                {Qt.Key_1: 'Do', Qt.Key_2: 'Ré', Qt.Key_3: 'Mi', Qt.Key_4: 'Fa', Qt.Key_5: 'Sol', Qt.Key_6: 'La',
                 Qt.Key_7: 'Si'},
            ]
            for idx, mapping in enumerate(octave_maps):
                if key in mapping and idx < self.spin_octaves.value():
                    note = mapping[key]
                    buttons = [b for b in self.piano.findChildren(QPushButton) if b.text() == note]
                    if len(buttons) > idx:
                        buttons[idx].animateClick(self.piano.anim_dur)
                    return

        if current == 1:
            mapping = {Qt.Key_A: 'Do', Qt.Key_S: 'Ré', Qt.Key_D: 'Mi', Qt.Key_F: 'Fa', Qt.Key_G: 'Sol', Qt.Key_H: 'La',
                       Qt.Key_J: 'Si'}
            if key in mapping:
                note = mapping[key]
                buttons = [b for b in self.xylophone.findChildren(QPushButton) if b.text() == note]
                if buttons:
                    buttons[0].animateClick(self.xylophone.anim_duration)
                return

        if current == 2:
            vg_map = {Qt.Key_1: 0, Qt.Key_2: 1, Qt.Key_3: 2, Qt.Key_4: 3, Qt.Key_5: 4, Qt.Key_6: 5, Qt.Key_7: 6,
                      Qt.Key_8: 7, Qt.Key_9: 8, Qt.Key_0: 9}
            if key in vg_map:
                idx = vg_map[key]
                buttons = self.videogame.findChildren(QPushButton)
                if idx < len(buttons):
                    buttons[idx].animateClick(self.videogame.anim_duration)
                return

        super().keyPressEvent(event)

    def switch_instrument(self, idx):
        self.stack.setCurrentIndex(idx)
        self.spin_octaves.setEnabled(idx == 0)
        self.settings.setValue('instrument', idx)
        self.stack.updateGeometry()
        self.centralWidget().updateGeometry()
        self.centralWidget().layout().invalidate()
        self.centralWidget().layout().activate()
        self.adjustSize()

    def change_octaves(self, value):
        self.piano.setOctaves(value)
        self.settings.setValue('octaves', value)
        self.switch_instrument(self.stack.currentIndex())

    def closeEvent(self, event):
        self.settings.sync()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
