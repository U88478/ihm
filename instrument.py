import pygame
import numpy as np
from scipy.signal import lfilter, bilinear, lfilter_zi

note_to_frequency = {
    "Do" : (261,523,1046),
    "Do#" : (277,554,1108),
    "Ré" : (293,587,1174),
    "Ré#" : (311,622,1244),
    "Mi" : (329,659,1318),
    "Fa" : (349,698,1396),
    "Fa#" : (369,739,1479),
    "Sol" : (392,783,1568),
    "Sol#" : (415,830,1661),
    "La" : (440,880,1760),
    "La#" : (477,932,1864),
    "Si" : (496,987,1975),
    "B0": 31,
    "C1": 33,
    "C#1": 35,  # or "Db1": 35
    "D1": 37,
    "D#1": 39,  # or "Eb1": 39
    "E1": 41,
    "F1": 44,
    "F#1": 46,  # or "Gb1": 46
    "G1": 49,
    "G#1": 52,  # or "Ab1": 52
    "A1": 55,
    "A#1": 58,  # or "Bb1": 58
    "B1": 62,
    "C2": 65,
    "C#2": 69,  # or "Db2": 69
    "D2": 73,
    "D#2": 78,  # or "Eb2": 78
    "E2": 82,
    "F2": 87,
    "F#2": 93,  # or "Gb2": 93
    "G2": 98,
    "G#2": 104,  # or "Ab2": 104
    "A2": 110,
    "A#2": 117,  # or "Bb2": 117
    "B2": 123,
    "C3": 131,
    "C#3": 139,  # or "Db3": 139
    "D3": 147,
    "D#3": 156,  # or "Eb3": 156
    "E3": 165,
    "F3": 175,
    "F#3": 185,  # or "Gb3": 185
    "G3": 196,
    "G#3": 208,  # or "Ab3": 208
    "A3": 220,
    "A#3": 233,  # or "Bb3": 233
    "B3": 247,
    "C4": 262,
    "C#4": 277,  # or "Db4": 277
    "D4": 294,
    "D#4": 311,  # or "Eb4": 311
    "E4": 330,
    "F4": 349,
    "F#4": 370,  # or "Gb4": 370
    "G4": 392,
    "G#4": 415,  # or "Ab4": 415
    "A4": 440,
    "A#4": 466,  # or "Bb4": 466
    "B4": 494,
    "C5": 523,
    "C#5": 554,  # or "Db5": 554
    "D5": 587,
    "D#5": 622,  # or "Eb5": 622
    "E5": 659,
    "F5": 698,
    "F#5": 740,  # or "Gb5": 740
    "G5": 784,
    "G#5": 831,  # or "Ab5": 831
    "A5": 880,
    "A#5": 932,  # or "Bb5": 932
    "B5": 988,
    "C6": 1047,
    "C#6": 1109,  # or "Db6": 1109
    "D6": 1175,
    "D#6": 1245,  # or "Eb6": 1245
    "E6": 1319,
    "F6": 1397,
    "F#6": 1480,  # or "Gb6": 1480
    "G6": 1568,
    "G#6": 1661,  # or "Ab6": 1661
    "A6": 1760,
    "A#6": 1865,  # or "Bb6": 1865
    "B6": 1976,
    "C7": 2093,
    "C#7": 2217,  # or "Db7": 2217
    "D7": 2349,
    "D#7": 2489,  # or "Eb7": 2489
    "E7": 2637,
    "F7": 2794,
    "F#7": 2960,  # or "Gb7": 2960
    "G7": 3136,
    "G#7": 3322,  # or "Ab7": 3322
    "A7": 3520,
    "A#7": 3729,  # or "Bb7": 3729
    "B7": 3951,
    "C8": 4186,
    "C#8": 4435,  # or "Db8": 4435
    "D8": 4699,
    "D#8": 4978,  # or "Eb8": 4978
}
    
    


class MusicPlayer:
    
    def __init__(self, sample_rate=44100): 
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        self.sample_rate = sample_rate
        

    def play_xylophone_tone(self, frequency, duration):
        # Génération des harmoniques complexes pour un son métallique
        harmonics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        harmonics_weights = [0.5, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.03, 0.02, 0.01]

        # Generate the tone
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = sum(weight * np.sin(frequency * harmonic * 2 * np.pi * t) for harmonic, weight in zip(harmonics, harmonics_weights))
        tone *= (0.5 * np.pi)

        # Appliquer un filtre de résonance pour simuler la sonorité métallique
        b, a = bilinear([1, 0, 0], [1, -2 * 0.95 * np.cos(2 * np.pi * frequency / self.sample_rate), 0.9025], fs=self.sample_rate)
        zi = lfilter_zi(b, a)
        tone, _ = lfilter(b, a, tone, zi=zi*tone[0])

        # Apply a quick decay envelope
        envelope = np.linspace(1, 0, len(tone))
        tone *= envelope

        # Normalisation du ton
        tone = tone / np.max(np.abs(tone))

        # Jouer le son
        self._play_tone(tone, duration)

        
        
    def play_piano_tone(self, frequency, duration):
        # Create harmonics
        harmonics = [1, 2, 3, 4, 5, 6, 7, 8]
        harmonics_weights = [0.5, 0.25, 0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125]

        # Generate tone
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = sum(weight * np.sin(frequency * harmonic * 2 * np.pi * t) for harmonic, weight in zip(harmonics, harmonics_weights))

        # Ensure the envelope matches the length of the tone array
        envelope = self.create_envelope(len(tone), attack_percent=0.01, decay_percent=0.1, sustain_level=0.3, release_percent=0.1)

        # Apply envelope to the tone
        tone *= envelope
        tone = tone / np.max(np.abs(tone))  # Normalization

        # Play tone
        self._play_tone(tone, duration)

    def create_envelope(self, num_samples, attack_percent, decay_percent, sustain_level, release_percent):
        # Calculate lengths of each part of the ADSR envelope
        attack_samples = int(num_samples * attack_percent)
        decay_samples = int(num_samples * decay_percent)
        sustain_samples = num_samples - (attack_samples + decay_samples + int(num_samples * release_percent))
        release_samples = num_samples - (attack_samples + decay_samples + sustain_samples)

        # Generate ADSR envelope
        attack = np.linspace(0, 1, attack_samples, False)
        decay = np.linspace(1, sustain_level, decay_samples, False)
        sustain = np.full(sustain_samples, sustain_level)
        release = np.linspace(sustain_level, 0, release_samples, False)
        envelope = np.concatenate((attack, decay, sustain, release))
        
        # Ensure the envelope is not longer than the number of samples
        return envelope[:num_samples]

    def play_videoGame_tone(self, frequency, duration):
        # Onde carrée pour la guitare
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = np.sign(np.sin(frequency * 2 * np.pi * t))
        self._play_tone(tone, duration)

    def _play_tone(self, tone, duration):
        stereo_tone = np.vstack((tone, tone)).T
        contiguous_tone = np.ascontiguousarray((32767 * stereo_tone).astype(np.int16))
        sound = pygame.sndarray.make_sound(contiguous_tone)
        sound.set_volume(0.05)  # Réglez le volume
        sound.play()
        pygame.time.delay(int(duration * 1000))
        
        
    