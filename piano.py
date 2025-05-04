import time

from PyQt5.QtCore import pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout

from config import settings
from gui.instruments.instrument import note_to_frequency, MusicPlayer


class Piano(QWidget):
    notePlayed = pyqtSignal(str, float)

    def __init__(self, octaves=1, parent=None):
        super().__init__(parent)
        self.octaves = octaves
        self.player = MusicPlayer()
        self.click_duration = float(settings.value("click_piano", 0.5))

        # Key dimensions and spacing
        self.white_w, self.white_h = 60, 200
        self.black_w, self.black_h = 36, 120
        self.white_spacing, self.black_spacing = 2, 4

        # Animation timing
        self.anim_dur = 100

        self._build_ui()

    def _build_ui(self):
        # Clear existing layout
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)

        # Create main layouts
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        black_layout = QHBoxLayout()
        black_layout.setContentsMargins(0, 0, 0, 0)
        black_layout.setSpacing(self.black_spacing)

        white_layout = QHBoxLayout()
        white_layout.setContentsMargins(0, 0, 0, 0)
        white_layout.setSpacing(self.white_spacing)

        # Note names per octave
        white_notes = ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si']
        black_notes = ['Do#', 'Ré#', None, 'Fa#', 'Sol#', 'La#', None]

        # Build keys for each octave
        for oct_idx in range(self.octaves):
            # White keys
            for note in white_notes:
                btn = QPushButton(note)
                btn.setFixedSize(self.white_w, self.white_h)
                btn.setStyleSheet(
                    "QPushButton { background: white;"
                    " border-top:2px solid #eee; border-left:2px solid #eee;"
                    " border-bottom:2px solid #888; border-right:2px solid #888; }"
                    "QPushButton:pressed { background: #ddd; }"
                )
                btn.clicked.connect(self._make_play_fn(note, oct_idx, btn))
                white_layout.addWidget(btn)

            # Black keys
            for note in black_notes:
                if note:
                    btn = QPushButton(note)
                    btn.setFixedSize(self.black_w, self.black_h)
                    btn.setStyleSheet(
                        "QPushButton { background: black; color: white;"
                        " border-top-left-radius:4px; border-top-right-radius:4px; }"
                        "QPushButton:pressed { background: #333; }"
                    )
                    btn.clicked.connect(self._make_play_fn(note, oct_idx, btn))
                    black_layout.addWidget(btn)
                else:
                    spacer = QWidget()
                    spacer.setFixedSize(self.white_w, self.black_h)
                    black_layout.addWidget(spacer)

        main_layout.addLayout(black_layout)
        main_layout.addLayout(white_layout)
        self.setLayout(main_layout)

        # Update geometry hints
        self.updateGeometry()
        self.adjustSize()

    def _make_play_fn(self, note, oct_idx, button):
        def handler():
            # Animate key press
            orig = button.geometry()
            shrink = orig.adjusted(2, 2, -2, -2)
            anim = QPropertyAnimation(button, b"geometry", self)
            anim.setDuration(self.anim_dur)
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            anim.setKeyValueAt(0, orig)
            anim.setKeyValueAt(0.5, shrink)
            anim.setKeyValueAt(1, orig)
            anim.start()

            # Play tone after half animation
            def play_note():
                freqs = note_to_frequency.get(note, [])
                if len(freqs) > oct_idx:
                    freq = freqs[oct_idx]
                elif freqs:
                    freq = freqs[0]
                else:
                    freq = 440
                self.player.play_piano_tone(freq, self.click_duration)
                self.notePlayed.emit(note, time.time())

            QTimer.singleShot(self.anim_dur // 2, play_note)

        return handler

    def setOctaves(self, octaves):
        if octaves != self.octaves and 1 <= octaves <= 3:
            self.octaves = octaves
            self._build_ui()
