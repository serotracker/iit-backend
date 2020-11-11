import ssl
import os
import smtplib

from email.mime.text import MIMEText

# SMTP setup
port = 465
context = ssl.create_default_context()
sender = 'iitbackendalerts@gmail.com'
recipients = ['abeljohnjoseph@gmail.com', 'ewanmay3@gmail.com', 'simonarocco09@gmail.com', 'austin.atmaja@gmail.com', 'rahularoradfs@gmail.com']  # Add additional email addresses here
password = os.getenv('GMAIL_PASS')


def send_api_error_email(body, data, error=None, request_info=None):
    # Configure the full email body
    body = "Hello Data Team,\n\n" + body

    # Add error to response body if exists
    if error is not None:
        body += f"\n\nError Info: {error}"

    try:
        body += f"\nType: {data['error']['type']}"  # If logging severity changes, this needs to be updated accordingly
        body += f"\nMessage: {data['error']['message']}"
    except (KeyError, TypeError):
        body += f"\nAPI Response Info: {data}"

    if request_info is not None:
        body += f"\n\nAPI Request info"
        body += f"\nURL: {request_info['url']}"
        body += f"\nHeaders: {request_info['headers']}"

    body += "\n\nSincerely,\nIIT Backend Alerts"

    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(sender, password)

        msg = MIMEText(body)
        msg['Subject'] = "ALERT: Unsuccessful Record Retrieval"
        msg['From'] = sender
        msg['To'] = ", ".join(recipients)
        server.sendmail(sender, recipients, msg.as_string())
    return
