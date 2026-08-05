from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
import re

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["https://techybuff.com", "https://www.techybuff.com"]}})

API_KEY = os.environ.get("TRANSCRIPT_API_KEY")

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
            return jsonify({"success": False, "message": "Invalid YouTube URL."})

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

        response = requests.get(endpoint, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            return jsonify({"success": False, "message": response.text}), response.status_code

        data = response.json()

        if "transcript" not in data:
            return jsonify({"success": False, "message": "No transcript returned by API."})

        transcript_items = data["transcript"]
        
        # Build two versions of the transcript: one with timestamps, one without
        plain_text_list = []
        timestamped_text_list = []

        for item in transcript_items:
            text = item.get("text", "")
            
            # Attempt to grab the timestamp (usually returned as 'start', 'offset', or 'timestamp')
            start_time = item.get("timestamp") or item.get("start") or item.get("offset")
            time_str = ""
            
            if start_time is not None:
                try:
                    # Convert to HH:MM:SS format
                    sec = int(float(start_time))
                    mins, secs = divmod(sec, 60)
                    hours, mins = divmod(mins, 60)
                    if hours > 0:
                        time_str = f"[{hours:02d}:{mins:02d}:{secs:02d}] "
                    else:
                        time_str = f"[{mins:02d}:{secs:02d}] "
                except:
                    # Fallback if API already formatted it as a string
                    time_str = f"[{start_time}] "

            plain_text_list.append(text)
            timestamped_text_list.append(f"{time_str}{text}")

        return jsonify({
            "success": True,
            "title": data.get("metadata", {}).get("title", ""),
            "author": data.get("metadata", {}).get("author_name", ""),
            "language": data.get("language", ""),
            "transcript": "\n".join(plain_text_list),
            "transcript_timestamps": "\n".join(timestamped_text_list)
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
