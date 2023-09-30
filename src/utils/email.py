import os
import re
from email.message import EmailMessage

import aiosmtplib

REGEX = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
assert EMAIL_SENDER, "EMAIL_SENDER environment variable not set"
assert PASSWORD, "EMAIL_PASSWORD environment variable not set"


def verify_regex(email: str):
    if re.match(REGEX, email):
        return True
    raise ValueError(f"Invalid email address: {email}")


async def send_verifaction(email: str):
    try:
        await send_email(
            send_to=email,
            subject="Verification",
            body="Your email has been verified !",
        )
    except Exception:
        raise Exception("Unable to send verification email")


async def send_email(send_to: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = EMAIL_SENDER
    message["To"] = send_to
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message=message,
        hostname="smtp.gmail.com",
        port=465,
        username=EMAIL_SENDER,
        password=PASSWORD,
        use_tls=True,
    )
