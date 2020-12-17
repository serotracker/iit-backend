import ssl
import os
import smtplib

from email.mime.text import MIMEText

# SMTP setup
port = 465
context = ssl.create_default_context()
sender = 'iitbackendalerts@gmail.com'
password = os.getenv('GMAIL_PASS')

def send_email(body, recipients, subject):
    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(sender, password)

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ", ".join(recipients)
        server.sendmail(sender, recipients, msg.as_string())
    return


def send_api_error_email(body, data, error=None, request_info=None):
    recipients = ['abeljohnjoseph@gmail.com', 'ewanmay3@gmail.com', 'simonarocco09@gmail.com',
              'austin.atmaja@gmail.com', 'rahularoradfs@gmail.com']  # Add additional email addresses here

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

    send_email(body, recipients, "ALERT: Unsuccessful Record Retrieval")
    return


def send_schema_validation_error_email(unacceptable_records_map):
    # Set recipients
    recipients = ['abeljohnjoseph@gmail.com', 'simonarocco09@gmail.com',
                  'austin.atmaja@gmail.com']  # Add additional email addresses here

    # Configure the full email body
    body = "Hello Data Team,\n\nThere were one or more records that did not meet the schema criteria, as follows:\n\n"

    for record, errors in unacceptable_records_map.items():
        body += f"Record: {record}\n"
        body += f"Errors: {errors}\n\n"

    body += "\nSincerely,\nIIT Backend Alerts"

    send_email(body, recipients, "ALERT: Schema Validation Failed for Record(s)")
    return
