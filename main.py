from flask import Flask, request, render_template
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


def send_email(receiver_email, subject, body):
    sender_email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    try:
        msg = MIMEText(body)
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        return "Email sent!"
    except Exception as e:
        return f"Error: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        return send_email(email, subject, message)
    return render_template('form.html')


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))