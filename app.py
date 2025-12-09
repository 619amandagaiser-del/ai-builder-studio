from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse
from jinja2 import Template
from io import BytesIO
import re

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/build-html")
async def build_html(request: Request):
    data = await request.json()
    
    # Надёжное экранирование для JavaScript
    def escape_js_string(s):
        return (
            s
            .replace("\\", "\\\\")
            .replace("`", "\\`")          # ← КРИТИЧНО для шаблонных строк
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )

    safe_prompt = escape_js_string(data["system_prompt"])

    with open("templates/agent.html.j2", encoding="utf-8") as f:
        template = Template(f.read())
    
    html_content = template.render(
        ai_name=data["ai_name"],
        system_prompt=safe_prompt,
        groq_key=data["groq_key"]
    )
    
    return StreamingResponse(
        BytesIO(html_content.encode("utf-8")),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={data['ai_name'].replace(' ', '_')}.html"}
    )