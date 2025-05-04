import time

from PyQt5.QtCore import pyqtSignal, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout

from config import settings
from gui.instruments.instrument import MusicPlayer


class VideoGame(QWidget):
    notePlayed = pyqtSignal(str, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = MusicPlayer()
        self.click_duration = float(settings.value("click_videogame", 0.1))

        # Game pad buttons and identifiers
        self.buttons = [
            ('super-mario.png', 'Logo'),
            ('super-mario1.png', 'MarioHead'),
            ('plante-carnivore.png', 'Piranha'),
            ('pieces-de-monnaie.png', 'CoinBox'),
            ('mario11.png', 'Star'),
            ('waluigi.png', 'Waluigi'),
            ('plante.png', 'Plant'),
            ('jeu.png', 'Pipe'),
            ('mario.png', 'Mushroom'),
            ('le-manoir-de-luigi.png', 'Luigi'),
        ]

        # Corresponding frequencies for each button
        self.frequencies = [
            2093,  # C7
            2349,  # D7
            2637,  # E7
            2794,  # F7
            3136,  # G7
            3520,  # A7
            1976,  # B6
            1568,  # G6
            1760,  # A6
            1318,  # E6
        ]

        self.icon_size = QSize(64, 64)
        self.anim_duration = 150  # ms

        self._build_ui()

    def _build_ui(self):
        # Clear existing layout
        layout = self.layout()
        if layout:
            QWidget().setLayout(layout)

        # Horizontal layout for icons
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Create icon buttons
        for idx, (filename, identifier) in enumerate(self.buttons):
            btn = QPushButton()
            btn.setIcon(QIcon(f"icons/{filename}"))
            btn.setIconSize(self.icon_size)
            btn.setFixedSize(self.icon_size.width() + 12,
                             self.icon_size.height() + 12)
            btn.setFlat(True)
            btn.clicked.connect(self._make_play_fn(idx, identifier, btn))
            main_layout.addWidget(btn)

        self.setLayout(main_layout)

    def _make_play_fn(self, idx, identifier, button):
        def handler():
            # Button press animation
            orig = button.geometry()
            shrink = orig.adjusted(2, 2, -2, -2)
            anim = QPropertyAnimation(button, b"geometry", self)
            anim.setDuration(self.anim_duration)
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            anim.setKeyValueAt(0, orig)
            anim.setKeyValueAt(0.5, shrink)
            anim.setKeyValueAt(1, orig)
            anim.start()

            # Play tone after half animation
            def play_note():
                freq = self.frequencies[idx]
                self.player.play_videoGame_tone(freq, self.click_duration)
                self.notePlayed.emit(identifier, time.time())

            QTimer.singleShot(self.anim_duration // 2, play_note)

        return handler
