import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


def send_email(to: str, subject: str, body: str) -> None:
    """메일 발송. SMTP 미설정(앱 비밀번호 없음)이면 발송 대신 서버 로그로 출력."""
    if not settings.email_enabled:
        logger.info("[메일-개발모드] to=%s | %s\n%s", to, subject, body)
        return

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as s:
            s.starttls()
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.send_message(msg)
        logger.info("[메일발송 성공] to=%s subject=%s", to, subject)
    except Exception as e:  # 발송 실패해도 흐름은 끊지 않고 로그로 남김
        logger.error("[메일발송 실패] %s — 로그로 대체", e)
        logger.info("[메일-실패폴백] to=%s | %s\n%s", to, subject, body)
