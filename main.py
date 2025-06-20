from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)

# Railway hanya izinkan tulis ke /tmp
DOWNLOAD_FOLDER = "/tmp/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        start_time = request.form["start"]
        end_time = request.form["end"]
        resolution = request.form["resolution"]

        def time_to_sec(t):
            h, m, s = map(int, t.split(":"))
            return h * 3600 + m * 60 + s

        start_sec = time_to_sec(start_time)
        end_sec = time_to_sec(end_time)

        duration = end_sec - start_sec
        video_id = str(uuid.uuid4())[:8]
        output_file = f"{video_id}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_file)

        ydl_opts = {
    "format": f"best[ext=mp4][height<={resolution}]",
    "outtmpl": output_path,
    "paths": {"home": DOWNLOAD_FOLDER},
    "download_sections": [f"*{start_time}-{end_time}"],
    "noplaylist": True,
    "quiet": True,
}


        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return redirect(url_for("download", filename=output_file))
        except Exception as e:
            return f"Gagal download. Coba lagi. Error: {e}"

    return render_template("index.html")

@app.route("/downloads/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
