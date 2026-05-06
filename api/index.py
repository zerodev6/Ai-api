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
        # In the 2026 version, the method is often accessed via ddgs.chat() 
        # but if you get an attribute error, use this universal wrapper:
        with DDGS() as ddgs:
            # New internal logic for Duck.ai 2026
            response = ddgs.chat(prompt, model=model)
            return json_response({"success": True, "model": model, "response": response})
    except AttributeError:
        # Fallback for older library versions still on Vercel cache
        return json_response({
            "success": False, 
            "message": "Library version mismatch. Please update requirements.txt to 'ddgs' or 'duckduckgo-search>=6.0'"
        }, 500)
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)

@app.route("/")
def index():
    return json_response({"status": "online", "service": "Duck AI Proxy"})
