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
    model = request.args.get("model", "gpt-4o-mini")

    if not prompt:
        return json_response({"success": False, "message": "Prompt is required"}, 400)

    try:
        with DDGS() as ddgs:
            # Current DDG Models: 'gpt-4o-mini', 'claude-3-haiku', 'llama-3.1-70b', 'mixtral-8x7b'
            response = ddgs.chat(prompt, model=model)
            return json_response({"success": True, "model": model, "response": response})
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return json_response({
        "success": True,
        "service": "DuckDuckGo AI Vercel Proxy",
        "endpoints": {
            "chat": "/chat?prompt=your_message",
            "models": ["gpt-4o-mini", "claude-3-haiku", "llama-3.1-70b"]
        }
    })
