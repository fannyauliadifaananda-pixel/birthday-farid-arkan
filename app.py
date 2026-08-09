#!/usr/bin/env python3
"""
🎂✨ HAPPY BIRTHDAY SAYANGNYA AKOOO ✨🎂
=========================================
Web app ucapan ulang tahun bertema malam berbintang + neon glassmorphism,
siap deploy dari GitHub ke Streamlit Community Cloud.

SEMUA KODE ADA DI SATU FILE INI (streamlit_app.py).
Hanya ada 1 hal wajib di luar kode karena syarat platform Streamlit Cloud
(bukan pilihan, murni aturan hosting): file kecil bernama `requirements.txt`
isinya SATU BARIS -> streamlit
Tanpa file itu, Streamlit Cloud tidak tahu library apa yang harus diinstall.

Fitur unik di versi ini:
- 🌌 Latar langit malam dengan bintang berkelip + gradient bergerak
- 💎 Kartu ucapan bergaya glassmorphism dengan judul neon berkedip pelangi
- 🎈 Balon & 💝 hati melayang naik terus-menerus di layar
- 🕯️ Kue ulang tahun dengan lilin yang nyala apinya berkedip (CSS)
- 🎊 Confetti meledak otomatis saat halaman dibuka (canvas-confetti)
- ⌨️ Doa ulang tahun muncul dengan efek mengetik huruf demi huruf (JS)
- 🎵 Musik "Happy Birthday" disintesis SENDIRI dari gelombang sinus
  (tanpa file mp3 eksternal) & diputar otomatis saat masuk halaman
- ✏️ Nama bisa diganti dari sidebar tanpa edit kode

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

Catatan browser: sebagian browser (terutama di HP) memblokir autoplay
audio bersuara sebelum ada interaksi pengguna. Kalau musik tidak otomatis
bunyi, tombol "🔁 Putar Ulang Lagu" di halaman akan tetap memutarnya.
"""

import base64
import io
import math
import struct
import wave

import streamlit as st
import streamlit.components.v1 as components

# ------------------------------------------------------------------
# 1. GENERATOR MUSIK "HAPPY BIRTHDAY" (sintesis gelombang sinus)
# ------------------------------------------------------------------

NOTE_FREQ = {
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
    "G4": 392.00, "A4": 440.00, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46,
    "G5": 783.99, "REST": 0.0,
}

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


# ------------------------------------------------------------------
# 2. TEKS DOA
# ------------------------------------------------------------------

DOA = (
    "Semoga selalu diberi kesehatan, panjang umur, selalu disertai kenikmatan "
    "dalam hidup dan rasa syukur, dan sukses.. aamiinn"
)

# ------------------------------------------------------------------
# 3. CSS: LANGIT MALAM, KARTU GLASSMORPHISM, BALON & HATI MELAYANG
# ------------------------------------------------------------------

CSS = """
<style>
.stApp {
    background: radial-gradient(ellipse at top, #1b0d3a 0%, #0a0620 60%, #050311 100%);
    background-attachment: fixed;
    overflow-x: hidden;
}

/* Bintang berkelip */
.stars {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        radial-gradient(2px 2px at 20px 30px, #fff, transparent),
        radial-gradient(2px 2px at 140px 90px, #fff, transparent),
        radial-gradient(1.5px 1.5px at 90px 40px, #ffd7f5, transparent),
        radial-gradient(1.5px 1.5px at 200px 150px, #d7e9ff, transparent),
        radial-gradient(2px 2px at 260px 60px, #fff, transparent),
        radial-gradient(1.5px 1.5px at 320px 200px, #fff, transparent);
    background-repeat: repeat;
    background-size: 340px 220px;
    animation: twinkle 3s ease-in-out infinite alternate;
}
@keyframes twinkle {
    from { opacity: 0.35; }
    to { opacity: 0.95; }
}

.rainbow-title {
    position: relative;
    z-index: 1;
    text-align: center;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 1px;
    background: linear-gradient(270deg, #ff3cac, #ff9900, #ffee00, #33ff77, #00e5ff, #6a5cff, #ff3cac);
    background-size: 1600% 1600%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: rainbow-move 6s linear infinite;
    text-shadow: 0 0 25px rgba(255, 255, 255, 0.15);
    margin-bottom: 0.2rem;
}
@keyframes rainbow-move {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}

.subtitle {
    position: relative;
    z-index: 1;
    text-align: center;
    color: #ffd6f5;
    font-size: 1.25rem;
    margin-top: 0;
    text-shadow: 0 0 12px rgba(255, 214, 245, 0.5);
}

/* Kartu kaca */
.glass-card {
    position: relative;
    z-index: 1;
    max-width: 720px;
    margin: 1.5rem auto;
    padding: 1.8rem 2rem;
    border-radius: 26px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 0 40px rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(6px);
}

/* Balon & hati melayang */
.floaters {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}
.floaters span {
    position: absolute;
    bottom: -60px;
    font-size: 2.2rem;
    opacity: 0.85;
    animation-name: rise;
    animation-timing-function: ease-in;
    animation-iteration-count: infinite;
}
@keyframes rise {
    0%   { transform: translateY(0) translateX(0) rotate(0deg); opacity: 0; }
    10%  { opacity: 0.9; }
    100% { transform: translateY(-115vh) translateX(30px) rotate(15deg); opacity: 0; }
}

/* Kue & lilin */
.cake-wrap {
    position: relative;
    z-index: 1;
    text-align: center;
    margin: 0.3rem 0 0.8rem 0;
}
.cake-emoji {
    font-size: 4.2rem;
    display: inline-block;
    animation: bob 2.2s ease-in-out infinite;
}
@keyframes bob {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
.candle {
    display: inline-block;
    font-size: 1.6rem;
    animation: flicker 0.9s ease-in-out infinite alternate;
    filter: drop-shadow(0 0 8px #ffb703);
}
@keyframes flicker {
    from { opacity: 1; transform: scale(1); }
    to   { opacity: 0.7; transform: scale(0.92) translateY(-2px); }
}

.wish-box {
    position: relative;
    z-index: 1;
    text-align: center;
    color: #fff;
    font-size: 1.35rem;
    font-weight: 700;
    margin-top: 0.5rem;
    text-shadow: 0 0 14px rgba(255, 182, 235, 0.6);
}

.doa-title {
    text-align: center;
    color: #ffe9a8;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 0.4rem;
    text-transform: uppercase;
    font-size: 0.9rem;
    opacity: 0.85;
}
</style>

<div class="stars"></div>
<div class="floaters">
    <span style="left:5%;  animation-duration:9s;  animation-delay:0s;">🎈</span>
    <span style="left:15%; animation-duration:11s; animation-delay:1.5s;">💗</span>
    <span style="left:28%; animation-duration:8s;  animation-delay:3s;">🎈</span>
    <span style="left:42%; animation-duration:12s; animation-delay:0.5s;">✨</span>
    <span style="left:56%; animation-duration:10s; animation-delay:2s;">💗</span>
    <span style="left:68%; animation-duration:9.5s;animation-delay:4s;">🎈</span>
    <span style="left:80%; animation-duration:11s; animation-delay:1s;">✨</span>
    <span style="left:90%; animation-duration:8.5s; animation-delay:2.5s;">💗</span>
</div>
"""


def autoplay_audio_html(wav_bytes: bytes) -> str:
    b64 = base64.b64encode(wav_bytes).decode()
    return f"""
    <audio autoplay="true" loop>
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """


CONFETTI_JS = """
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js"></script>
<script>
function fireConfetti() {
    if (typeof confetti !== 'function') { return; }
    var duration = 3000;
    var end = Date.now() + duration;
    (function frame() {
        confetti({ particleCount: 4, angle: 60, spread: 65, origin: { x: 0 }, colors: ['#ff3cac','#ffee00','#00e5ff','#6a5cff'] });
        confetti({ particleCount: 4, angle: 120, spread: 65, origin: { x: 1 }, colors: ['#ff3cac','#ffee00','#00e5ff','#6a5cff'] });
        if (Date.now() < end) { requestAnimationFrame(frame); }
    })();
    confetti({ particleCount: 120, spread: 100, origin: { y: 0.4 } });
}
window.addEventListener('load', fireConfetti);
setTimeout(fireConfetti, 300);
</script>
"""


def typewriter_component(text: str, speed_ms: int = 35, height: int = 140):
    safe_text = text.replace("\\", "\\\\").replace("`", "\\`").replace("</", "<\\/")
    html = f"""
    <div style="
        font-family: 'Trebuchet MS', sans-serif;
        text-align:center;
        color:#ffe9a8;
        font-size:1.05rem;
        line-height:1.7;
        max-width:640px;
        margin:0 auto;
        min-height:{height - 20}px;
    ">
        <span id="typed"></span><span id="cursor" style="opacity:1;">🤲</span>
    </div>
    <script>
    const text = `{safe_text}`;
    let i = 0;
    const el = document.getElementById('typed');
    function tick() {{
        if (i <= text.length) {{
            el.textContent = text.slice(0, i);
            i++;
            setTimeout(tick, {speed_ms});
        }}
    }}
    tick();
    </script>
    """
    components.html(html, height=height)


# ------------------------------------------------------------------
# 4. HALAMAN UTAMA
# ------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Happy Birthday Sayangnya Akoo 🎂",
        page_icon="🎂",
        layout="centered",
    )
    st.markdown(CSS, unsafe_allow_html=True)
    components.html(CONFETTI_JS, height=0, width=0)

    with st.sidebar:
        st.header("✏️ Kustomisasi")
        nama = st.text_input("Nama panggilan", value="SAYANGNYA AKOOO")
        putar_musik = st.checkbox("🎵 Putar musik otomatis", value=True)
        st.caption("Ganti nama di atas, judul & ucapan otomatis berubah.")

    st.markdown(
        f'<p class="rainbow-title">🎉 HAPPY BIRTHDAY {nama.upper()} 🎉</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle">Satu hari spesial, untuk satu orang paling spesial 💖</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="cake-wrap">
            <span class="candle">🕯️</span>
            <span class="cake-emoji">🎂</span>
            <span class="candle">🕯️</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="wish-box">Happy Birthday, {nama}... semoga hari ini sepenuh cinta seperti kamu di hati aku 🥹💫</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="doa-title" style="margin-top:1.2rem;">🤍 Doa Untukmu 🤍</div>', unsafe_allow_html=True)
    typewriter_component(DOA, speed_ms=30, height=150)

    st.markdown("</div>", unsafe_allow_html=True)

    wav_bytes = generate_wav_bytes()
    if putar_musik:
        components.html(autoplay_audio_html(wav_bytes), height=0, width=0)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Putar Ulang Lagu", use_container_width=True):
            st.balloons()
            components.html(autoplay_audio_html(wav_bytes), height=0, width=0)
    with col2:
        st.download_button(
            "⬇️ Unduh Musik (.wav)",
            data=wav_bytes,
            file_name="happy_birthday_tune.wav",
            mime="audio/wav",
            use_container_width=True,
        )

    st.audio(wav_bytes, format="audio/wav")
    st.caption("Kalau musik tidak otomatis bunyi (aturan browser), tekan ▶️ di atas atau tombol 'Putar Ulang Lagu'.")


if __name__ == "__main__":
    main()
