import time

from PyQt5.QtCore import pyqtSignal, QTimer, QSize
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout

from config import settings
from gui.instruments.instrument import note_to_frequency, MusicPlayer


class Xylophone(QWidget):
    notePlayed = pyqtSignal(str, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = MusicPlayer()
        self.click_duration = float(settings.value("click_xylophone", 0.5))

        # Bar dimensions and spacing
        self.bar_width = 60
        self.bar_heights = [240, 220, 200, 180, 160, 140, 120]
        self.spacing = 20

        # Note names and colors
        self.notes = ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si']
        self.colors = ['#9b30ff', '#4b0082', '#0000ff', '#00ff00', '#ffff00', '#ff8c00', '#ff0000']

        # Press animation duration in ms
        self.anim_duration = 150

        self._build_ui()

    def _build_ui(self):
        # Clear any existing layout
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)

        # Horizontal layout for bars
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.spacing)

        # Create bars with press animation
        for idx, note in enumerate(self.notes):
            btn = QPushButton(note)
            btn.setFixedSize(self.bar_width, self.bar_heights[idx])
            btn.setStyleSheet(
                f"QPushButton {{ background: {self.colors[idx]}; border: none; border-radius: 10px; }}"
                "QPushButton:pressed { background: #444; }"
            )
            btn.clicked.connect(self._make_play_fn(note, idx, btn))
            layout.addWidget(btn)

        self.setLayout(layout)

    def sizeHint(self) -> QSize:
        width = self.bar_width * len(self.notes) + self.spacing * (len(self.notes) - 1)
        height = max(self.bar_heights)
        return QSize(width, height)

    def _make_play_fn(self, note, button):
        def handler():
            # Simulate press animation
            button.setDown(True)
            QTimer.singleShot(self.anim_duration, lambda: button.setDown(False))

            # Play tone after half animation
            def play_note():
                freqs = note_to_frequency.get(note, [])
                # Always use base octave for xylophone
                freq = freqs[0] if freqs else 440
                self.player.play_xylophone_tone(freq, self.click_duration)
                self.notePlayed.emit(note, time.time())

            QTimer.singleShot(self.anim_duration // 2, play_note)

        return handler
