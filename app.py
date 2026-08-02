from flask import Flask, render_template, request, jsonify
import yt_dlp
import tempfile
import os
import re
import json

app = Flask(__name__)


def extract_video_id(url):
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:embed/)([A-Za-z0-9_-]{11})",
        r"(?:shorts/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/transcript", methods=["POST"])
def transcript():

    try:

        data = request.get_json()

        url = data.get("url", "").strip()

        if not url:
            return jsonify({
                "success": False,
                "message": "Please enter a YouTube URL."
            })

        with tempfile.TemporaryDirectory() as tempdir:

            ydl_opts = {
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["en", "en-US", "en-GB"],
                "subtitlesformat": "vtt",
                "outtmpl": os.path.join(tempdir, "%(id)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(url, download=False)

                video_id = info["id"]

                ydl.download([url])

                transcript = ""

                for file in os.listdir(tempdir):

                    if file.endswith(".vtt"):

                        with open(
                            os.path.join(tempdir, file),
                            "r",
                            encoding="utf-8"
                        ) as f:

                            for line in f:

                                line = line.strip()

                                if (
                                    "-->" in line
                                    or line == ""
                                    or line == "WEBVTT"
                                ):
                                    continue

                                if line.startswith("<"):
                                    continue

                                transcript += line + "\n"

                if transcript.strip() == "":
                    return jsonify({
                        "success": False,
                        "message": "No transcript found."
                    })

                return jsonify({
                    "success": True,
                    "video_id": video_id,
                    "transcript": transcript
                })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
