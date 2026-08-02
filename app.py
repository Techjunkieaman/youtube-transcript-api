from flask import Flask, render_template, request, jsonify
import requests
import os
import re

app = Flask(__name__)

API_KEY = os.environ.get(sk_4gdcJi1O-dDha0MNaq27x1PeXudrjbBDdEcIwccNii4)


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

        endpoint = "https://transcriptapi.com/api/v2/youtube/transcript"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        }

        params = {
            "video_url": f"https://youtu.be/{video_id}",
            "format": "json",
            "include_timestamp": "true"
        }

        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "message": response.text
            })

        transcript = response.json()

        text = "\n".join(
            item["text"]
            for item in transcript
        )

        return jsonify({
            "success": True,
            "transcript": text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
