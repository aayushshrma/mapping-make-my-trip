import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def send_email(receiver_email, subject, body, sender_email, sender_password):
    """
    Sends an email alert via SMTP.
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    email_text = message.as_string()

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # upgrade the connection to secure
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, email_text)
        server.quit()
        print("Email alert sent successfully!")
    except Exception as e:
        print("Error sending email:", e)


def main():
    # ---------------------------
    # 1. Get user inputs
    # ---------------------------
    place = input("Enter place: ")
    checkin_date = input("Enter check-in date (e.g. Thu Oct 12 2023): ")
    # (Note: Depending on the website’s calendar implementation, you may need to provide the date text exactly as shown on the calendar.)
    checkout_date = input("Enter check-out date (e.g. Sat Oct 14 2023): ")
    num_rooms = int(input("Enter number of rooms: "))
    num_adults = int(input("Enter number of adults: "))
    hotel_name = input("Enter hotel name to search: ")
    threshold_price = float(input("Enter price threshold: "))
    # Email details: update sender_email and sender_password with your credentials.
    receiver_email = input("Enter your email address to receive alert: ")
    sender_email = "youremail@example.com"  # Replace with your sender email
    sender_password = "yourpassword"  # Replace with your sender email password or app-specific password