import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_survey_email(student_email, student_name, form_url):
    sender_email = "bivektest97@gmail.com"
    sender_password = "ypxt tsbh okvx qali"

    subject = "Workshop Feedback Request"
    body = f"""
    Hi {student_name},

    Thank you for attending the workshop. Please provide your feedback by clicking on the link below:

    {form_url}

    Best regards,
    Your Team
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = student_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, student_email, text)
        server.quit()
        print(f"Email sent to {student_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
