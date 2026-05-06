import json
import requests
import uuid
from datetime import datetime
from flask import Flask, request, Response

app = Flask(__name__)

# CORS Configuration
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}

API_URL = "https://plai.chat/api/web/chat/send"
# Current known working free model ID
# You can also use "meta-llama/llama-3-70b-instruct:free" 
DEFAULT_MODEL = "nvidia/llama-3.1-nemotron-70b-instruct:free"

def json_response(data, status=200):
    return Response(
        json.dumps(data, indent=2, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json", **CORS_HEADERS}
    )

def get_chat_response(prompt):
    session = requests.Session()
    
    # Required headers for the current plai.chat API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "Origin": "https://plai.chat",
        "Referer": "https://plai.chat/",
        "X-Requested-With": "XMLHttpRequest"
    }

    payload = {
        "message": prompt,
        "history": [],
        "model": DEFAULT_MODEL,
        "attachments": [],
        # Generate a standard ISO timestamp
        "conversationStartedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "zdr": False
    }

    try:
        # We use stream=True because plai.chat uses Server-Sent Events (SSE)
        response = session.post(API_URL, headers=headers, json=payload, timeout=30, stream=True)
        
        if response.status_code != 200:
            return f"Error: API returned status {response.status_code}"

        full_text = ""
        for line in response.iter_lines():
            if not line:
                continue
                
            line_str = line.decode("utf-8")
            
            # SSE format usually starts with 'data: '
            if line_str.startswith("data: "):
                try:
                    content = line_str[6:].strip()
                    if content == "[DONE]":
                        break
                        
                    data = json.loads(content)
                    
                    # The API typically sends chunks in a 'text' or 'content' field
                    if "text" in data:
                        full_text += data["text"]
                    elif "content" in data:
                        full_text += data["content"]
                        
                except json.JSONDecodeError:
                    continue

        return full_text.strip() if full_text else "Error: Empty response from AI"

    except Exception as e:
        return f"Request failed: {str(e)}"

@app.route("/chat", methods=["GET", "OPTIONS"])
def chat_endpoint():
    if request.method == "OPTIONS":
        return Response(None, headers=CORS_HEADERS)

    prompt = request.args.get("prompt", "").strip()

    if not prompt:
        return json_response({"success": False, "message": "Prompt parameter required"}, 400)

    response_text = get_chat_response(prompt)
    
    if "Error" in response_text or "failed" in response_text:
        return json_response({"success": False, "response": response_text}, 500)
        
    return json_response({"success": True, "response": response_text})

@app.route("/", methods=["GET"])
def index():
    return json_response({
        "success": True,
        "service": "PLAI.chat Proxy API",
        "usage": "/chat?prompt=Hello"
    })

if __name__ == "__main__":
    # Standard port 3000 as requested
    app.run(host="0.0.0.0", port=3000, debug=True)
