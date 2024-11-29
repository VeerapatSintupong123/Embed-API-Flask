from PIL import Image
from io import BytesIO
import base64
import urllib.parse

import numpy as np
import cv2 as cv

import os
import smtplib
from email.mime.text import MIMEText

class AreaSegmentor:
    def __init__(self, image):
        self.image = image
        self.gray_image = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        self.coordinates = [(81, 15), (214, 15), (273, 235), (36, 234)]

    def segment_road(self) -> np.ndarray:
        if self.coordinates:
            points = np.array(self.coordinates, dtype=np.int32)
            points = points.reshape((-1, 1, 2)) 
            mask = np.zeros_like(self.gray_image)
            cv.fillPoly(mask, [points], 255)

            segment = cv.bitwise_and(self.image, self.image, mask=mask)
            return segment
        else:
            raise ValueError("No coordinates selected for segmentation.")

def count_circles(image) -> int:
    circles = cv.HoughCircles(
        image,
        cv.HOUGH_GRADIENT,
        dp=1.2,
        minDist=30,
        param1=32,
        param2=30,
        minRadius=10,
        maxRadius=50
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        return len(circles)
    else:
        return 0

def image_from_base64(base64_string: str) -> Image:
    base64_string = urllib.parse.unquote(base64_string)

    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '=' * (4 - missing_padding)

    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))

    return image

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
        return True
    except Exception as e:
        return False
    
def save_email(email):
    try:
        with open('emails.txt', mode='a') as f:
            f.write(f"{email}\n")
        return True
    except Exception as e:
        return False