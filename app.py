#!/usr/bin/env python3
"""
🎂 HAPPY BIRTHDAY SAYANG — Versi Web (Streamlit) 🎂
=====================================================
Aplikasi web ucapan ulang tahun otomatis, siap deploy ke Streamlit
Community Cloud langsung dari GitHub.

Fitur:
- 🎵 Musik "Happy Birthday" disintesis sendiri dari gelombang sinus
  (tanpa file audio eksternal) dan diputar OTOMATIS begitu halaman dibuka.
- 🎨 Judul teks pelangi animasi + balon melayang + kue ulang tahun.
- ⌨️ Efek ucapan & doa muncul dengan animasi "typewriter".
- ✏️ Nama "sayang" bisa diganti langsung dari sidebar.
- 🎈 Efek confetti balon bawaan Streamlit.

--------------------------------------------------------------------
SEMUA KODE ADA DI SATU FILE INI. Hanya ada satu hal di luar kode yang
wajib ada karena aturan platform Streamlit Cloud (bukan pilihan saya):
sebuah file bernama `requirements.txt` berisi SATU BARIS "streamlit",
supaya Streamlit Cloud tahu library apa yang perlu diinstall sebelum
menjalankan app-mu. Tanpa file itu, platform tidak akan bisa install
Streamlit sama sekali (ini murni syarat hosting, bukan bagian logika
program).

CARA DEPLOY KE GITHUB + STREAMLIT (gratis):
1. Buat repo baru di GitHub, upload file ini dengan nama `streamlit_app.py`.
2. Buat 1 file lagi bernama `requirements.txt` isinya cuma:
       streamlit
3. Buka https://share.streamlit.io -> "New app".
4. Pilih repo & branch kamu, isi "Main file path" = streamlit_app.py
5. Klik "Deploy" -> tunggu build selesai -> aplikasi langsung online 🎉

CARA JALANKAN LOKAL:
    pip install streamlit
    streamlit run streamlit_app.py
--------------------------------------------------------------------
"""

import base64
import io
import math
import struct
import wave

import streamlit as st

# ------------------------------------------------------------------
# 1. GENERATOR MUSIK "HAPPY BIRTHDAY" (sintesis gelombang sinus)
# ------------------------------------------------------------------

NOTE_FREQ = {
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
    "G4": 392.00, "A4": 440.00, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46,
    "G5": 783.99, "REST": 0.0,
}

# Melodi "Happy Birthday to You"
MELODY = [
    ("G4", 0.5), ("G4", 0.5), ("A4", 1.0), ("G4", 1.0), ("C5", 1.0), ("B4", 2.0),
    ("G4", 0.5), ("G4", 0.5), ("A4", 1.0), ("G4", 1.0), ("D5", 1.0), ("C5", 2.0),
    ("G4", 0.5), ("G4", 0.5), ("G5", 1.0), ("E5", 1.0), ("C5", 1.0), ("B4", 1.0), ("A4", 2.0),
    ("F5", 0.5), ("F5", 0.5), ("E5", 1.0), ("C5", 1.0), ("D5", 1.0), ("C5", 2.0),
]

SAMPLE_RATE = 44100
BPM = 100


def _envelope(i, n):
    fade = max(1, int(0.05 * n))
    if i < fade:
        return i / fade
    if i > n - fade:
        return (n - i) / fade
    return 1.0


def _generate_tone(freq, duration_sec, volume=0.35):
    n_samples = int(SAMPLE_RATE * duration_sec)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        if freq <= 0:
            value = 0.0
        else:
            value = (
                math.sin(2 * math.pi * freq * t) * 0.6
                + math.sin(2 * math.pi * freq * 2 * t) * 0.25
                + math.sin(2 * math.pi * freq * 3 * t) * 0.15
            )
            value *= _envelope(i, n_samples) * volume
        samples.append(value)
    return samples


@st.cache_data(show_spinner=False)
def generate_wav_bytes():
    """Bangun musik ulang tahun di memori (tanpa file eksternal), kembalikan bytes WAV."""
    beat_duration = 60.0 / BPM
    all_samples = []
    for note, beats in MELODY:
        freq = NOTE_FREQ.get(note, 0.0)
        all_samples.extend(_generate_tone(freq, beats * beat_duration))
        all_samples.extend(_generate_tone(0.0, 0.03))

    buffer = io.BytesIO()
    with wave.open(buffer, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in all_samples
        )
        wf.writeframes(frames)
    return buffer.getvalue()


def autoplay_audio(wav_bytes: bytes):
    """Putar audio otomatis begitu halaman dimuat, pakai tag HTML5 <audio autoplay>."""
    b64 = base64.b64encode(wav_bytes).decode()
    st.markdown(
        f"""
        <audio autoplay="true" loop>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# 2. STYLE & TAMPILAN
# ------------------------------------------------------------------

DOA = (
    "Semoga selalu diberi kesehatan, panjang umur, selalu disertai kenikmatan "
    "dalam hidup dan rasa syukur, dan sukses.. aamiinn 🤲✨"
)

CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #1e1033, #33184a, #4a1d5c);
    background-attachment: fixed;
}
.rainbow-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(270deg, #ff0000, #ff9900, #ffee00, #33ff00, #00ffee, #0066ff, #cc00ff, #ff0000);
    background-size: 1600% 1600%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: rainbow-move 6s linear infinite;
    margin-bottom: 0;
}
@keyframes rainbow-move {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}
.subtitle {
    text-align: center;
    color: #ffd6f5;
    font-size: 1.3rem;
    margin-top: 0;
}
.balloon-row {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    font-size: 3rem;
    margin: 1rem 0;
}
.balloon {
    animation: float 3s ease-in-out infinite;
}
.balloon:nth-child(2) { animation-delay: 0.4s; }
.balloon:nth-child(3) { animation-delay: 0.8s; }
.balloon:nth-child(4) { animation-delay: 1.2s; }
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-18px); }
}
.cake-box {
    text-align: center;
    font-size: 4rem;
    margin: 0.5rem 0;
    animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}
.wish-box {
    text-align: center;
    color: #fff;
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 1rem;
    padding: 1rem;
    animation: fadein 1.5s ease-in;
}
@keyframes fadein {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}
.doa-box {
    max-width: 680px;
    margin: 1.5rem auto;
    padding: 1.3rem 1.6rem;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 215, 0, 0.4);
    color: #ffe9a8;
    font-size: 1.15rem;
    line-height: 1.7;
    text-align: center;
    animation: fadein 2.2s ease-in;
}
</style>
"""


def main():
    st.set_page_config(page_title="Happy Birthday Sayang 🎂", page_icon="🎂", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.header("✏️ Kustomisasi")
        nama = st.text_input("Nama sayang", value="Sayang")
        putar_musik = st.checkbox("🎵 Putar musik otomatis", value=True)
        st.caption("Ganti nama di atas, ucapan & judul akan otomatis ikut berubah.")

    st.markdown('<p class="rainbow-title">🎉 SELAMAT ULANG TAHUN 🎉</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">Untuk kamu, {nama} tersayang 💖</p>', unsafe_allow_html=True)

    st.markdown(
        '<div class="balloon-row">'
        '<span class="balloon">🎈</span><span class="balloon">🎈</span>'
        '<span class="balloon">🎈</span><span class="balloon">🎈</span>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="cake-box">🎂🕯️🎂</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="wish-box">Happy Birthday {nama}... semoga harimu secerah senyummu! 🥳</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="doa-box">🤲 {DOA}</div>', unsafe_allow_html=True)

    st.balloons()

    wav_bytes = generate_wav_bytes()
    if putar_musik:
        autoplay_audio(wav_bytes)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Putar Ulang Lagu"):
            st.balloons()
            autoplay_audio(wav_bytes)
    with col2:
        st.download_button(
            "⬇️ Unduh Musik (.wav)",
            data=wav_bytes,
            file_name="happy_birthday_tune.wav",
            mime="audio/wav",
        )

    st.audio(wav_bytes, format="audio/wav")


if __name__ == "__main__":
    main()
