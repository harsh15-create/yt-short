from flask import Flask, request, send_file, abort, after_this_request
import subprocess
import uuid
import os
import glob

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

@app.route("/audio", methods=["GET"])
def get_audio():
    video_id = request.args.get("videoId")
    if not video_id:
        abort(400, "Missing videoId")

    tmp_id = str(uuid.uuid4())
    output_template = f"/tmp/{tmp_id}.%(ext)s"
    url = f"https://www.youtube.com/watch?v={video_id}"

    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--no-playlist",
        "-o", output_template,
        url
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=240
        )
    except Exception as e:
        print("SUBPROCESS ERROR:", e)
        abort(500, "yt-dlp execution failed")

    if result.returncode != 0:
        print("YT-DLP STDERR:", result.stderr)
        abort(500, "yt-dlp failed")

    files = glob.glob(f"/tmp/{tmp_id}*.mp3")
    if not files:
        print("NO MP3 FILE CREATED")
        abort(500, "File processing failed")

    audio_path = files[0]

    @after_this_request
    def cleanup(response):
        try:
            os.remove(audio_path)
        except Exception:
            pass
        return response

    return send_file(
        audio_path,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name=f"{video_id}.mp3"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
