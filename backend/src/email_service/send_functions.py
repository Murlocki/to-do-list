import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib
from src.shared.config import settings
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)

async def send_email_with_retry(subject, reset_link, to_email, retries=settings.email_send_retries, delay=settings.email_send_delay):

    # Загрузка шаблона HTML
    if subject == "register_email":
        with open("register_email.html", "r", encoding="utf-8") as file:
            subject = "Registration Confirmation in to-do list"
            html_content = file.read()
    else:
        with open("recover_password.html", "r", encoding="utf-8") as file:
            subject = "Recovery Confirmation in to-do list"
            html_content = file.read()
    # Форматирование шаблона
    html_content = html_content.strip().replace("{name}", to_email).replace("{link}", reset_link)
    # Создание MIME-сообщения
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.email_send_address
    msg["To"] = to_email
    msg["Subject"] = subject

    # Прикрепление HTML контента
    msg.attach(MIMEText(html_content, "html"))

    # Отправка письма с повторными попытками
    for attempt in range(1, retries + 1):
        try:
            await aiosmtplib.send(msg, hostname=settings.email_host, port=settings.email_port, start_tls=True,
                                  username=settings.email_send_address, password=settings.email_send_password)
            logger.info(f"Email sent to {to_email}")
            return
        except Exception as e:
            logger.error(f"Attempt {attempt}: Failed to send email to {to_email}: {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                logger.critical(f"All retry attempts failed for {to_email}")
