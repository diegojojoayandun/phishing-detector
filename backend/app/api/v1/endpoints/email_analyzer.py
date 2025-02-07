from fastapi import APIRouter, Form, UploadFile, Depends
import re
import requests
from app.repositories.email_repository import save_email_analysis

router = APIRouter()

TELEGRAM_TOKEN = "TU_TELEGRAM_BOT_TOKEN_AQUÍ"
TELEGRAM_CHAT_ID = "TU_CHAT_ID_AQUÍ"

def detect_suspicious_urls(text):
    url_pattern = r"https?://[^\s]+"
    return re.findall(url_pattern, text)

def send_telegram_alert(subject, content, detected_urls):
    message = f"""
🚨 *Phishing Alert Detected!* 🚨

*Subject:* {subject}
*Content:* {content}
*Detected URLs:* {' '.join(detected_urls)}
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

@router.post("/analyze_email/")
async def analyze_email(subject: str = Form(None), content: str = Form(None), file: UploadFile = None):
    full_text = f"Subject: {subject}\n\n{content}"
    if file:
        file_content = await file.read()
        full_text = file_content.decode("utf-8")

    detected_urls = detect_suspicious_urls(full_text)
    if detected_urls:
        send_telegram_alert(subject, content, detected_urls)
        save_email_analysis(subject, content, detected_urls)  # Guardar en la base de datos
        return {"status": "Phishing detected", "suspicious_urls": detected_urls}
    return {"status": "Legitimate", "suspicious_urls": []}