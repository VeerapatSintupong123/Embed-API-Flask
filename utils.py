from PIL import Image
from io import BytesIO
import base64
import urllib.parse

import numpy as np
import cv2 as cv

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart

from sklearn.cluster import DBSCAN

class AreaSegmentor:
    def __init__(self, image):
        self.image = image
        self.gray_image = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        self.coordinates = [(234, 22), (91, 25), (65, 231), (266, 233)]

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
        
def count_specific_color(image_input, lower, upper, eps=6, min_samples=100):
    """
    Apply DBSCAN clustering to count the number of objects of a specific color by clustering pixels in the image.
    
    Args:
    - image_input: Input image (RGB format).
    - lower: Lower bound of the target color in HSV (H, S, V).
    - upper: Upper bound of the target color in HSV (H, S, V).
    - eps: Maximum distance between two samples for them to be considered in the same cluster.
    - min_samples: Minimum number of samples in a neighborhood to form a cluster.
    
    Returns:
    - num_cluster: The number of detected color-based clusters.
    """

    hsv_image = cv.cvtColor(image_input, cv.COLOR_RGB2HSV)

    mask = cv.inRange(hsv_image, lower, upper)
    target_pixels = np.where(mask > 0)
    coords = np.column_stack(target_pixels)

    if coords.size == 0:
        return 0

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(coords)

    unique_labels = set(labels)
    num_cluster = len([label for label in unique_labels if label != -1])

    return num_cluster

def image_from_base64(base64_string: str) -> Image:
    base64_string = urllib.parse.unquote(base64_string)

    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '=' * (4 - missing_padding)

    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))

    return image

def send_email(receiver_email, subject, body_html, base64_image_string):
    """
    Sends an email with an HTML body and an embedded image.

    Args:
    - receiver_email: The recipient's email address.
    - subject: Subject of the email.
    - body_html: The HTML body of the email.
    - base64_image_string: Base64 encoded image string.
    """
    sender_name = "Anomaly Detector"
    sender_email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    try:
        msg = MIMEMultipart()
        msg['From'] = formataddr((sender_name, sender_email))
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body_html, 'html'))
        image = image_from_base64(base64_image_string)

        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)

        mime_image = MIMEBase('image', 'jpeg')
        mime_image.set_payload(buffer.read())
        encoders.encode_base64(mime_image)
        mime_image.add_header('Content-Disposition', 'attachment', filename='anomaly_image.jpg')
        mime_image.add_header('Content-ID', '<anomaly_image>')
        msg.attach(mime_image)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    
def save_email(email):
    try:
        with open('emails.txt', mode='a') as f:
            f.write(f"{email}\n")
        return True
    except Exception as e:
        return False