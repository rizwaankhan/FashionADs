import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

username = 'farhanhafeez880@gmail.com'
password = 'Farhan12345'


def send_mail(html=None, text='Email_body', subject='Hello word', from_email='', to_emails=['']):
    assert isinstance(to_emails, list)
    msg = MIMEMultipart('alternative')
    msg['From'] = from_email
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    txt_part = MIMEText(text, 'plain')
    msg.attach(txt_part)
    html_part = MIMEText(f"{html}", 'html')
    # htmlFile = open(html, 'rb')
    # html_part = MIMEText(html, "html", "utf-8")
    msg.attach(html_part)
    msg_str = msg.as_string()

    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_email, to_emails, msg_str)
    server.quit()
