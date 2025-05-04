# ProjetFinal

You can play instruments with mouse or keyboard, record your performance, and play back partitions.

## Requirements

* Python 3.8+
* PyQt5
* numpy, pygame, scipy (for `MusicPlayer`)

Install dependencies:

```bash
pip install -r requirements.txt
```
or
```bash
pip install PyQt5 numpy pygame scipy
```

## Running

Launch the main window:

```bash
python main.py
```

## Interface Overview

* **Toolbar / Menu**

  * **Ouvrir (Ctrl+O)**: Open a `.txt` partition (note + duration per line).
  * **Enregistrer (Ctrl+S)**: Start recording your session.
  * **Stop (Ctrl+T)**: Stop recording or playback.
  * **Quitter (Ctrl+Q)**: Exit the application.

* **Instrument Tabs**: Click or use keys to switch between:

  * **Piano**: SpinBox selects 1–3 octaves.
  * **Xylophone**
  * **Video Game** pad

* **Tempo Slider**: Adjust playback speed (0.5×–3.0×).

## Playing via Mouse

Click on keys/bars/buttons to play. Each instrument animates on press.

## Playing via Keyboard

* **Piano** (when active):

  * **Octave1**: ASDFGHJ → DoRéMiFaSolLaSi
  * **Octave2**: QWERTYU → DoRéMiFaSolLaSi
  * **Octave3**: 1234567 → DoRéMiFaSolLaSi

* **Xylophone** (when active): ASDFGHJ → DoRéMiFaSolLaSi

* **Video Game** (when active): 1234567890 → pad icons in order

## Recording & Playback

1. Click **Enregistrer** (or Ctrl+S) to record.
2. Play instruments.
3. Click **Stop** (or Ctrl+T) to save a `.txt` file with notes and pauses.
4. Use **Ouvrir** (or Ctrl+O) to load and play the recorded partition.

## Settings Persistence

Last-used instrument, octave count, click durations, and tempo are saved to `QSettings` and restored on startup.