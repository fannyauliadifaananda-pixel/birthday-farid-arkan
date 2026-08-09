#!/usr/bin/env python3
"""
🎂 HAPPY BIRTHDAY SAYANG 🎂
============================
Script ulang tahun otomatis dengan:
- Musik "Happy Birthday" yang di-generate sendiri (sintesis gelombang sinus, tanpa file audio eksternal)
- Animasi ASCII art kue & balon di terminal
- Efek teks mengetik (typewriter) dengan warna pelangi
- Ucapan doa ulang tahun

File ini SATU FILE MANDIRI (single-file), tidak butuh file audio eksternal —
musiknya digenerate langsung dari kode dengan sintesis gelombang sinus.

Cara pakai:
    python birthday_wish.py

Dependency:
    - Wajib: hanya modul bawaan Python (math, os, struct, sys, time, wave, platform)
    - Opsional: colorama (untuk warna terminal di Windows CMD lama)
        pip install colorama

Kustomisasi cepat:
    - Ganti NAMA_SAYANG di bawah dengan nama orang tersayangmu
    - Ganti isi DOA jika ingin ucapan doa yang berbeda

Author: Dibuat dengan cinta untuk seseorang yang spesial 💖
"""

import math
import os
import struct
import sys
import time
import wave
import platform

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

    class _Dummy:
        def __getattr__(self, name):
            return ""

    Fore = _Dummy()
    Style = _Dummy()

NAMA_SAYANG = "Sayang"  # Ganti dengan nama pasangan/orang tersayangmu ✏️
WAV_FILENAME = "happy_birthday_tune.wav"

# ------------------------------------------------------------------
# 1. GENERATOR MUSIK "HAPPY BIRTHDAY" (sintesis gelombang sinus)
# ------------------------------------------------------------------

NOTE_FREQ = {
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
    "G4": 392.00, "A4": 440.00, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46,
    "G5": 783.99, "REST": 0.0,
}

# Melodi "Happy Birthday to You" (notasi, durasi dalam ketukan)
MELODY = [
    ("G4", 0.5), ("G4", 0.5), ("A4", 1.0), ("G4", 1.0), ("C5", 1.0), ("B4", 2.0),
    ("G4", 0.5), ("G4", 0.5), ("A4", 1.0), ("G4", 1.0), ("D5", 1.0), ("C5", 2.0),
    ("G4", 0.5), ("G4", 0.5), ("G5", 1.0), ("E5", 1.0), ("C5", 1.0), ("B4", 1.0), ("A4", 2.0),
    ("F5", 0.5), ("F5", 0.5), ("E5", 1.0), ("C5", 1.0), ("D5", 1.0), ("C5", 2.0),
]

SAMPLE_RATE = 44100
BPM = 100  # tempo


def _envelope(i, n):
    """Fade in/out sederhana biar nada tidak 'klik'."""
    fade = int(0.05 * n)
    if i < fade:
        return i / fade
    if i > n - fade:
        return (n - i) / fade
    return 1.0


def generate_tone(freq, duration_sec, volume=0.35):
    n_samples = int(SAMPLE_RATE * duration_sec)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        if freq <= 0:
            value = 0.0
        else:
            # sedikit harmonisa supaya bunyinya lebih "hangat", bukan sinus polos
            value = (
                math.sin(2 * math.pi * freq * t) * 0.6
                + math.sin(2 * math.pi * freq * 2 * t) * 0.25
                + math.sin(2 * math.pi * freq * 3 * t) * 0.15
            )
            value *= _envelope(i, n_samples) * volume
        samples.append(value)
    return samples


def generate_wav(filename=WAV_FILENAME):
    beat_duration = 60.0 / BPM
    all_samples = []
    for note, beats in MELODY:
        freq = NOTE_FREQ.get(note, 0.0)
        all_samples.extend(generate_tone(freq, beats * beat_duration))
        all_samples.extend(generate_tone(0.0, 0.03))  # jeda mikro antar nada

    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in all_samples
        )
        wf.writeframes(frames)
    return filename


def play_wav(filename):
    """Putar file WAV otomatis sesuai sistem operasi (tanpa dependency berat)."""
    system = platform.system()
    try:
        if system == "Windows":
            import winsound
            winsound.PlaySound(filename, winsound.SND_FILENAME)
        elif system == "Darwin":
            os.system(f"afplay '{filename}' > /dev/null 2>&1")
        else:  # Linux / lainnya
            if os.system(f"aplay '{filename}' > /dev/null 2>&1") != 0:
                os.system(f"paplay '{filename}' > /dev/null 2>&1")
    except Exception:
        print(f"{Fore.YELLOW}(Tidak bisa memutar audio otomatis di perangkat ini, "
              f"tapi file musiknya sudah dibuat: {filename}){Style.RESET_ALL}")


# ------------------------------------------------------------------
# 2. TAMPILAN ANIMASI TERMINAL
# ------------------------------------------------------------------

RAINBOW = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

CAKE_ART = r"""
                 (   )
                (     )
                 )   (
               _______
              |       |
              | 🎂🎂🎂 |
              |_______|
           .-' |    | '-.
          /    |    |    \
         |     |    |     |
         |_____|____|_____|
          \    HAPPY    /
           `--BIRTHDAY-`
"""

BALLOONS = r"""
     (\_/)      (\_/)      (\_/)
    ( ^.^ )    ( o.o )    ( >.< )
     )   (      )   (      )   (
    (     )    (     )    (     )
      | |         | |        | |
      | |         | |        | |
"""


def rainbow_print(text, delay=0.02):
    for i, ch in enumerate(text):
        color = RAINBOW[i % len(RAINBOW)]
        sys.stdout.write(f"{color}{ch}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def typewriter(text, color=Fore.CYAN, delay=0.035):
    for ch in text:
        sys.stdout.write(f"{color}{ch}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")


def fireworks_animation(rounds=3):
    frames = ["   .   ", "  .*.  ", " .*|*. ", ".*-o-*.", " .*|*. ", "  .*.  ", "   .   "]
    for _ in range(rounds):
        for f in frames:
            color = RAINBOW[hash(f) % len(RAINBOW)]
            sys.stdout.write(f"\r{color}✨ {f} ✨{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.08)
    print("\r" + " " * 30 + "\r", end="")


# ------------------------------------------------------------------
# 3. UCAPAN & DOA
# ------------------------------------------------------------------

DOA = (
    "Semoga selalu diberi kesehatan, panjang umur, selalu disertai kenikmatan "
    "dalam hidup dan rasa syukur, dan sukses.. aamiinn 🤲✨"
)


def main():
    clear_screen()

    rainbow_print("=" * 46)
    rainbow_print("      🎉  S E L A M A T   U L A N G   T A H U N  🎉")
    rainbow_print("=" * 46)
    print()

    for color in (Fore.MAGENTA, Fore.CYAN):
        print(f"{color}{BALLOONS}{Style.RESET_ALL}")
    print(f"{Fore.RED}{CAKE_ART}{Style.RESET_ALL}")

    time.sleep(0.3)
    typewriter(f"Happy Birthday {NAMA_SAYANG}... 🎂💖", color=Fore.MAGENTA, delay=0.06)
    time.sleep(0.3)

    print()
    print(f"{Fore.GREEN}🎵 Menyiapkan lagu ulang tahun untukmu...{Style.RESET_ALL}")
    filename = generate_wav()
    fireworks_animation(rounds=2)
    print(f"{Fore.GREEN}🎵 Memutar musik...{Style.RESET_ALL}")
    play_wav(filename)

    print()
    print(f"{Fore.YELLOW}{'-' * 46}{Style.RESET_ALL}")
    typewriter(DOA, color=Fore.YELLOW, delay=0.03)
    print(f"{Fore.YELLOW}{'-' * 46}{Style.RESET_ALL}")
    print()

    fireworks_animation(rounds=2)
    rainbow_print("🎁 Semoga hari ini penuh cinta dan kebahagiaan 🎁")
    print()


if __name__ == "__main__":
    main()
