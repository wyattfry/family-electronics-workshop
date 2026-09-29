# Lesson 4: play songs on a passive buzzer on GP18.
from machine import Pin, PWM
import time

NOTES = {  # frequency in Hz
    "C4": 262, "D4": 294, "E4": 330, "F4": 349, "G4": 392, "A4": 440, "B4": 494,
    "C5": 523, "D5": 587, "E5": 659, "F5": 698, "G5": 784, "-": 0,  # "-" = rest
}

buzzer = PWM(Pin(18))


def play(song, beat=0.25):
    for note, beats in song:
        freq = NOTES[note]
        if freq:
            buzzer.freq(freq)
            buzzer.duty_u16(32768)  # half on, half off = loudest square wave
        else:
            buzzer.duty_u16(0)
        time.sleep(beat * beats * 0.9)
        buzzer.duty_u16(0)          # tiny gap so repeated notes sound separate
        time.sleep(beat * beats * 0.1)


# Twinkle Twinkle. Write your own list: (note, how many beats)
twinkle = [
    ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1), ("A4", 1), ("A4", 1), ("G4", 2),
    ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1), ("D4", 1), ("D4", 1), ("C4", 2),
]

if __name__ == "__main__":
    play(twinkle)
