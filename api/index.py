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
    # In 2026, the default is often gpt-4o-mini
    model = request.args.get("model", "gpt-4o-mini") 

    if not prompt:
        return json_response({"success": False, "message": "Prompt is required"}, 400)

    try:
        # Latest library syntax for 2026
        with DDGS() as ddgs:
            results = ddgs.chat(prompt, model=model)
            return json_response({"success": True, "model": model, "response": results})
    except Exception as e:
        # Fallback error reporting
        return json_response({"success": False, "message": str(e)}, 500)

@app.route("/")
def index():
    return json_response({
        "status": "online", 
        "usage": "/chat?prompt=Hello",
        "tip": "If you see 'no attribute chat', check your requirements.txt version."
    })
