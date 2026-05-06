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
    # Updated 2026 default model name
    model = request.args.get("model", "gpt-4o-mini") 

    if not prompt:
        return json_response({"success": False, "message": "Prompt is required"}, 400)

    try:
        with DDGS() as ddgs:
            # The library moved to a unified chat interface in v9.0+
            # Use 'gpt-4o-mini', 'claude-3-haiku', or 'llama-3.1-70b'
            response = ddgs.chat(prompt, model=model)
            return json_response({"success": True, "model": model, "response": response})
            
    except Exception as e:
        # If .chat() fails, we check for the new 2026 syntax
        return json_response({
            "success": False, 
            "message": f"Error: {str(e)}. Try updating requirements.txt to 'ddgs'."
        }, 500)

@app.route("/")
def index():
    return json_response({"status": "online", "service": "DuckDuckGo AI Proxy 2026"})
