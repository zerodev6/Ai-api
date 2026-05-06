from flask import Flask, request, Response
import json
from duckduckgo_search import DDGS

app = Flask(__name__)

def json_response(data, status=200):
    return Response(
        json.dumps(data, indent=2, ensure_ascii=False),
        status=status,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

@app.route("/chat", methods=["GET", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return json_response({})

    prompt = request.args.get("prompt", "").strip()
    # In 2026, the available models are 'gpt-4o-mini', 'claude-3-haiku', 'llama-3.3-70b'
    model = request.args.get("model", "gpt-4o-mini") 

    if not prompt:
        return json_response({"success": False, "message": "Prompt is required"}, 400)

    try:
        with DDGS() as ddgs:
            # The .chat() method returns a generator (stream) in 2026.
            # We must loop through it to build the full text string.
            full_text = ""
            for chunk in ddgs.chat(prompt, model=model):
                full_text += chunk
            
            if not full_text:
                return json_response({"success": False, "message": "DuckDuckGo returned an empty response."}, 500)

            return json_response({
                "success": True, 
                "model": model, 
                "response": full_text
            })
            
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)

@app.route("/")
def index():
    return json_response({"status": "online", "service": "Duck AI Proxy 2026"})
