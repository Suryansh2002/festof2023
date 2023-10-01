import os
import re
from email.message import EmailMessage  # Python's email module

import aiosmtplib  # Async SMTP client

REGEX = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"  # Regex to validate email address

# Get environment variables
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
assert EMAIL_SENDER, "EMAIL_SENDER environment variable not set"
assert PASSWORD, "EMAIL_PASSWORD environment variable not set"


def verify_regex(email: str):
    """
    This function is used to check if the email address is valid.

    Args:
        email (str): Email address to check

    Returns:
        bool: True if email address is valid, False otherwise

    """
    if re.match(REGEX, email):  # check if email matches the regex
        return True
    raise ValueError(f"Invalid email address: {email}")


async def send_verifaction(email: str):
    """
    This function is used to send a verification email to the user.

    Args:
        email (str): Email address of the user

    Returns:
        None

    """
    try:
        await send_email(
            send_to=email,
            subject="Verification",
            body="Your email has been verified !",
        )  # send verification email
    except Exception:
        raise Exception("Unable to send verification email")


async def send_email(send_to: str, subject: str, body: str):
    """
    This function is used to send an email.

    Args:
        send_to (str): Email address of the receiver
        subject (str): Subject of the email
        body (str): Body of the email

    Returns:
        None

    """
    message = EmailMessage()
    message["From"] = EMAIL_SENDER
    message["To"] = send_to
    message["Subject"] = subject
    message.set_content(body)

    # send email
    await aiosmtplib.send(
        message=message,
        hostname="smtp.gmail.com",
        port=465,
        username=EMAIL_SENDER,
        password=PASSWORD,
        use_tls=True,
    )
