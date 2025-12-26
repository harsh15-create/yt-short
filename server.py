from flask import Flask, request, send_file, abort, after_this_request
import subprocess
import uuid
import os
import glob
import threading
import time

app = Flask(__name__)

MAX_CONCURRENT_JOBS = 2
semaphore = threading.Semaphore(MAX_CONCURRENT_JOBS)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.route("/audio", methods=["GET"])
def get_audio():
    if not semaphore.acquire(blocking=False):
        abort(429, "Too many concurrent jobs")

    video_id = request.args.get("videoId")
    if not video_id:
        semaphore.release()
        abort(400, "Missing videoId")

    tmp_id = str(uuid.uuid4())
    output_template = f"/tmp/{tmp_id}.%(ext)s"
    url = f"https://www.youtube.com/watch?v={video_id}"

    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--no-playlist",
        "-o", output_template,
        url
    ]

    try:
        subprocess.check_call(cmd, timeout=300)
    except subprocess.TimeoutExpired:
        semaphore.release()
        abort(504, "Download timeout")
    except subprocess.CalledProcessError:
        semaphore.release()
        abort(500, "yt-dlp failed")

    files = glob.glob(f"/tmp/{tmp_id}*.mp3")
    if not files:
        semaphore.release()
        abort(500, "MP3 not generated")

    audio_path = files[0]

    @after_this_request
    def cleanup(response):
        try:
            os.remove(audio_path)
        except Exception:
            pass
        semaphore.release()
        return response

    return send_file(
        audio_path,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name=f"{video_id}.mp3"
    )
