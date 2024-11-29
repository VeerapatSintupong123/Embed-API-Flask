import os
import numpy as np
import cv2 as cv
from flask import Flask, request, render_template, jsonify, redirect
from utils import AreaSegmentor, image_from_base64, count_circles, send_email, save_email

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
    
@app.route('/process', methods=['POST'])
def count_object():
    print(request.json)
    data = request.json
    image_string = data.get("image_string")
    cluster = 2

    if not image_string:
        return jsonify({"error": "No image provided"}), 400
    
    try:
        image = image_from_base64(image_string.strip().split(',')[1])
        segment = cv.cvtColor(AreaSegmentor(np.array(image)).segment_road(), cv.COLOR_BGR2GRAY)
        count = count_circles(segment)
        return jsonify({"count": count, "cluster": cluster})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        save_email(email)
        return redirect('https://youtube.com')
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))