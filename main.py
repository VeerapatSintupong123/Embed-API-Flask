import os
import numpy as np
from flask import Flask, request, render_template, jsonify, redirect
from utils import AreaSegmentor, image_from_base64, count_specific_color, send_email, save_email

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

body_html = """
<html>
<body>
    <h2>⚠️ Warning: Anomaly Detected!</h2>
    <p>An unusual number of clusters were detected.</p>
    <p>Please check the attached image for more details.</p>
    <img src="cid:anomaly_image" alt="Anomaly Image" style="width:100%;max-width:600px;">
</body>
</html>
"""
    
@app.route('/process', methods=['POST'])
def count_object():
    data = request.json
    image_string = data.get("image_string")
    string = image_string.strip().split(',')[1] 

    if not image_string:
        return jsonify({"error": "No image provided"}), 400
    
    try:
        image = image_from_base64(string)
        image = np.array(image)

        lower_blue = (100, 50, 50)
        upper_blue = (130, 255, 255)

        area_segmentor = AreaSegmentor(image)
        image = area_segmentor.segment_road()
        cluster = count_specific_color(image, lower=lower_blue, upper=upper_blue)

        # anomaly
        if cluster > 1:
            with open('emails.txt', mode='r', encoding='utf-8') as f:
                lines = f.readlines()

            lines = [line.strip() for line in lines] 
            lines = list(set(lines))
            for line in lines:
                email = line.split('\n')[0]
                send_email(
                    receiver_email=email,
                    subject="Anomaly Detected!",
                    body_html=body_html,
                    base64_image_string=string
                )
            
        return jsonify({"status": True, "cluster": cluster})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        if email:
            save_email(email)
            return redirect('https://fish-tank-embedded-front.vercel.app/')
        else:
            return redirect('/')
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))