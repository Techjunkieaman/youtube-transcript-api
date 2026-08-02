from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable
)
import traceback
import re

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

        video_id = extract_video_id(url)

        if not video_id:
            return jsonify({
                "success": False,
                "message": "Invalid YouTube URL."
            })

        api = YouTubeTranscriptApi()

        transcript = api.fetch(video_id)

        text = "\n".join(
            item.text for item in transcript
        )

        return jsonify({
            "success": True,
            "transcript": text
        })

    except Exception:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
