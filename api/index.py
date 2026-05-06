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
            # Check for the 2026 method name
            if hasattr(ddgs, 'chat'):
                response = ddgs.chat(prompt, model=model)
            else:
                # Fallback for library versions that moved it to .text_ai()
                # or similar modern variations
                response = ddgs.text(prompt, region='wt-wt', safesearch='off', timelimit='y')
            
            return json_response({"success": True, "model": model, "response": response})
            
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)

@app.route("/")
def index():
    return json_response({"status": "online", "service": "Duck AI Proxy Fixed"})
