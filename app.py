import os
import qrcode
import cloudinary
import cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, render_template

# Flask App Setup
app = Flask(__name__)

# Cloudinary Configuration (Replace with your credentials)
cloudinary.config( 
  cloud_name = "djr7tven5",  
  api_key = "683487828554685",  
  api_secret = "l5EbsR46OgilS0DGj_upJLtORqY"
)

# Configuration
IMAGE_FOLDER = r"C:\Users\user\Documents\pin-protected-qr\images"  # Folder containing images
QR_FOLDER = r"C:\Users\user\Documents\pin-protected-qr\qr_codes"  # Folder to save QR codes
ACCESS_PIN = "7013"  # Set your PIN here

# Ensure QR code folder exists
os.makedirs(QR_FOLDER, exist_ok=True)

# Store uploaded image data
image_data = {}

# Upload Images & Generate QR Codes
for filename in os.listdir(IMAGE_FOLDER):
    if filename.endswith((".png", ".jpg", ".jpeg")):
        file_path = os.path.join(IMAGE_FOLDER, filename)

        # Upload to Cloudinary using the same filename (without extension)
        cloudinary_filename = os.path.splitext(filename)[0]
        upload_result = cloudinary.uploader.upload(file_path, public_id=cloudinary_filename)
        image_url = upload_result["secure_url"]
        image_id = upload_result["public_id"]

        # Store image details
        image_data[image_id] = {"url": image_url, "password": ACCESS_PIN}

        # Generate QR Code linking to Flask app
        qr_url = f"http://127.0.0.1:5000/view/{image_id}"
        qr = qrcode.make(qr_url)

        # Convert QR code to image and add text
        qr = qr.convert("RGB")
        draw = ImageDraw.Draw(qr)
        font = ImageFont.load_default()

        # Add text (image name) on top of QR code
        text = os.path.splitext(filename)[0]  # Get filename without extension
        bbox = draw.textbbox((0, 0), text, font=font)  # Corrected text size calculation
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        image_width, image_height = qr.size
        text_position = ((image_width - text_width) // 2, 10)  # Centered at the top
        draw.text(text_position, text, fill="black", font=font)

        # Save QR code with the same filename as the image
        qr.save(os.path.join(QR_FOLDER, f"{filename}"))

print("✅ Images uploaded & QR codes generated!")


# Flask Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view/<img_id>", methods=["GET", "POST"])
def view_image(img_id):
    if request.method == "POST":
        password = request.form.get("password")

        # Validate PIN
        if img_id in image_data and image_data[img_id]["password"] == password:
            return render_template("image.html", image_url=image_data[img_id]["url"])
        else:
            return "Invalid PIN", 403

    return render_template("pin.html", img_id=img_id)

# Start Flask Server
if __name__ == "__main__":
    app.run(debug=True)
