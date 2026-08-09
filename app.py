"""
app.py
------
Website ucapan ulang tahun bertema lautan (Streamlit).
SEMUA logika ada di satu file ini:
  1. Pembangkit musik ulang tahun (sintesis gelombang sinus, bukan rekaman
     berhak cipta - melodi lagu ulang tahun klasik sudah public domain).
  2. CSS + animasi gelembung bertema lautan.
  3. Tampilan foto, judul, dan ucapan doa.

Cara pakai:
    pip install -r requirements.txt
    streamlit run app.py

Yang perlu kamu siapkan:
    assets/foto_faridutt.jpg   -> taruh foto yang mau ditampilkan
(musiknya dibuat otomatis oleh kode ini, tidak perlu file audio terpisah)
"""

import base64
import io
import math
import os
import struct
import wave

import streamlit as st

# ==============================================================================
# 1) PEMBANGKIT MUSIK ULANG TAHUN (disintesis dari gelombang sinus)
# ==============================================================================

SAMPLE_RATE = 44100

NOTES = {
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
    "G4": 392.00, "A4": 440.00, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46,
    "G5": 783.99, "A5": 880.00,
    "REST": 0,
}

# Pola melodi lagu ulang tahun klasik (public domain)
MELODY = [
    ("G4", 0.75), ("G4", 0.25), ("A4", 1), ("G4", 1), ("C5", 1), ("B4", 2),
    ("REST", 0.25),
    ("G4", 0.75), ("G4", 0.25), ("A4", 1), ("G4", 1), ("D5", 1), ("C5", 2),
    ("REST", 0.25),
    ("G4", 0.75), ("G4", 0.25), ("G5", 1), ("E5", 1), ("C5", 1), ("B4", 1), ("A4", 1.5),
    ("REST", 0.25),
    ("F5", 0.75), ("F5", 0.25), ("E5", 1), ("C5", 1), ("D5", 1), ("C5", 2),
]

BEAT_DURATION = 0.42  # detik per ketuk (tempo lagu)


def _note_wave(freq, duration, volume=0.5):
    """Bangun satu segmen gelombang sinus untuk 1 not, dengan envelope
    fade in/out sederhana supaya tidak ada bunyi 'klik'."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    fade = max(1, int(n_samples * 0.08))
    for i in range(n_samples):
        if freq == 0:
            value = 0.0
        else:
            t = i / SAMPLE_RATE
            value = math.sin(2 * math.pi * freq * t)
            if i < fade:
                value *= i / fade
            elif i > n_samples - fade:
                value *= (n_samples - i) / fade
            value *= volume
        samples.append(value)
    return samples


@st.cache_data(show_spinner=False)
def build_birthday_song_bytes():
    """Bangkitkan seluruh lagu dan kembalikan sebagai bytes WAV (in-memory,
    tidak perlu simpan file terpisah ke disk)."""
    all_samples = []
    for note, beats in MELODY:
        freq = NOTES[note]
        duration = beats * BEAT_DURATION
        all_samples.extend(_note_wave(freq, duration))
        all_samples.extend(_note_wave(0, 0.02))  # jeda kecil antar not

    buffer = io.BytesIO()
    with wave.open(buffer, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        for s in all_samples:
            s = max(-1.0, min(1.0, s))
            wf.writeframesraw(struct.pack("<h", int(s * 32767)))
    return buffer.getvalue()


# ==============================================================================
# 2) KONFIGURASI HALAMAN & PATH
# ==============================================================================

st.set_page_config(
    page_title="It's Faridutt Birthday !!",
    page_icon="🐬",
    layout="centered",
)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
PHOTO_PATHS = [
    os.path.join(ASSETS_DIR, "foto_faridutt.jpg"),
    os.path.join(ASSETS_DIR, "foto_faridutt2.jpg"),
]


def get_base64_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ==============================================================================
# 3) CSS TEMA LAUTAN (background gradient, gelembung animasi, kartu kaca)
# ==============================================================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: linear-gradient(180deg, #001d3d 0%, #003566 25%, #005b96 55%, #0077b6 75%, #48cae4 100%);
        background-attachment: fixed;
        overflow-x: hidden;
    }

    .bubble {
        position: fixed;
        bottom: -100px;
        background: rgba(255, 255, 255, 0.35);
        border-radius: 50%;
        pointer-events: none;
        animation: rise linear infinite;
        z-index: 0;
    }
    @keyframes rise {
        0%   { transform: translateY(0) translateX(0); opacity: 0.9; }
        100% { transform: translateY(-110vh) translateX(30px); opacity: 0; }
    }

    .title-text {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 0 12px #00b4d8, 0 0 24px #90e0ef;
        margin-bottom: 0.2em;
        font-family: 'Trebuchet MS', sans-serif;
    }

    .subtitle-text {
        text-align: center;
        font-size: 1.15rem;
        color: #caf0f8;
        margin-bottom: 1.2em;
        font-style: italic;
    }

    .photo-frame {
        border: 6px solid #90e0ef;
        border-radius: 20px;
        box-shadow: 0 0 25px rgba(144, 224, 239, 0.8), 0 0 60px rgba(0, 180, 216, 0.5);
        overflow: hidden;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(8px);
        border-radius: 18px;
        padding: 1.6em 1.8em;
        margin-top: 1.6em;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    }

    .glass-card p {
        color: #f0f9ff;
        font-size: 1.05rem;
        line-height: 1.7em;
        text-align: center;
        margin: 0;
    }

    .wave-emoji {
        text-align: center;
        font-size: 1.8rem;
        letter-spacing: 10px;
        margin-top: 1.2em;
    }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #caf0f8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom-color: #90e0ef !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 4) ANIMASI GELEMBUNG
# ==============================================================================
sizes = [14, 22, 10, 30, 18, 26, 12, 20, 16, 24]
lefts = [5, 15, 25, 35, 45, 55, 65, 75, 85, 95]
durations = [9, 12, 7, 15, 10, 13, 8, 11, 14, 9]
delays = [0, 2, 4, 1, 3, 5, 2.5, 0.5, 4.5, 1.5]

bubbles_html = ""
for i in range(10):
    bubbles_html += f"""
    <div class="bubble" style="
        left:{lefts[i]}%;
        width:{sizes[i]}px;
        height:{sizes[i]}px;
        animation-duration:{durations[i]}s;
        animation-delay:{delays[i]}s;">
    </div>
    """
st.markdown(bubbles_html, unsafe_allow_html=True)

# ==============================================================================
# 5) MUSIK ULANG TAHUN - AUTOPLAY (dibuat langsung di memori, tanpa file wav)
# ==============================================================================
song_bytes = build_birthday_song_bytes()
audio_b64 = base64.b64encode(song_bytes).decode()
st.markdown(
    f"""
    <audio autoplay loop style="display:none">
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
    </audio>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 6) KONTEN UTAMA
# ==============================================================================
st.markdown('<div class="title-text">🎉 It\'s Faridutt Birthday !! 🎉</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">🌊 Selamat berlayar ke usia baru, dudutt! 🌊</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    existing_photos = [p for p in PHOTO_PATHS if os.path.exists(p)]
    if existing_photos:
        st.markdown('<div class="photo-frame">', unsafe_allow_html=True)
        photo_tabs = st.tabs([f"📸 Foto {i+1}" for i in range(len(existing_photos))])
        for tab, photo_path in zip(photo_tabs, existing_photos):
            with tab:
                st.image(photo_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Taruh foto kamu di assets/foto_faridutt.jpg dan assets/foto_faridutt2.jpg")

st.markdown(
    """
    <div class="glass-card">
        <p>
        🐚 <b>Happy birthday dudutt</b> 🐚<br><br>
        Semoga selalu diberi kesehatan, panjang umur, selalu disertai kenikmatan
        dalam hidup dan rasa syukur, selalu dalam lindungan-Nya, dan sukses untukmu..
        <b>aamiinn</b> 🤲✨
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="wave-emoji">🐬 🐠 🐋 🐳 🦈 🐟 🌊</div>', unsafe_allow_html=True)

st.markdown(
    """
    <p style="text-align:center; color:#caf0f8; margin-top:2em; font-size:0.85rem;">
    Made with 💙 & ocean vibes
    </p>
    """,
    unsafe_allow_html=True,
)
