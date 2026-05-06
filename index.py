import json
import requests
from datetime import datetime
from flask import Flask, request, Response

app = Flask(__name__)

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}

API_URL = "https://plai.chat/api/web/chat/send"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://plai.chat",
    "Referer": "https://plai.chat/",
}

def json_response(data, status=200):
    return Response(
        json.dumps(data, indent=2, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json", **CORS}
    )

def get_chat_response(prompt):
    session = requests.Session()
    payload = {
        "message": prompt,
        "history": [],
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "attachments": [],
        "conversationStartedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "zdr": False
    }

    response = session.post(API_URL, headers=DEFAULT_HEADERS, json=payload, timeout=60, stream=True)

    if not response.ok:
        raise Exception("API failed")

    full_text = ""
    for line in response.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                try:
                    data = json.loads(line_str[6:])
                    if data.get("type") == "content":
                        full_text = data.get("text", "")
                    if data.get("done") is True:
                        break
                except json.JSONDecodeError:
                    continue

    if not full_text.strip():
        raise Exception("No response from API")

    return full_text.strip()

@app.route("/chat", methods=["GET", "OPTIONS"])
def chat_endpoint():
    if request.method == "OPTIONS":
        return Response(None, headers=CORS)

    prompt = request.args.get("prompt", "").strip()

    if not prompt:
        return json_response({"success": False, "message": "Prompt parameter required"}, 400)

    try:
        response_text = get_chat_response(prompt)
        return json_response({"success": True, "response": response_text})
    except Exception:
        return json_response({"success": False, "message": "Error processing request"}, 400)

@app.route("/", methods=["GET"])
def index():
    return json_response({
        "success": True,
        "service": "NVIDIA Nemotron API",
        "usage": {
            "endpoint": "/chat",
            "method": "GET",
            "parameters": {"prompt": {"type": "string", "required": True}},
            "example": "/chat?prompt=Hello"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
