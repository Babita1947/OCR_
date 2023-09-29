from flask import Flask, render_template, request, send_file,redirect,url_for
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator
import io

app = Flask(__name__)

# Define the route for the home page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice == "1":
            # Process PDF
            pdf_file = request.files["pdf_file"]
            pdf_file.save("uploaded.pdf")

            poppler_path = r'C:\Program Files\poppler-23.08.0\Library\bin'
            images = convert_from_path("uploaded.pdf", 500, poppler_path=poppler_path)

            page_number = 1
            translated_texts = []

            for image in images:
                image_path = f'page{page_number}.jpg'
                image.save(image_path, 'JPEG')

                myconfig = r"--psm 6 --oem 3"
                img = Image.open(image_path)
                text = pytesseract.image_to_string(img, config=myconfig)

                choice = request.form.get("language_choice", "bn")
                t1 = Translator()
                op = t1.translate(text, dest=choice)
                translated_texts.append(op.text)

                page_number += 1

            return render_template("result.html", texts=translated_texts)

        elif choice == "2":
            # Process Image
            image_file = request.files["image_file"]
            image_file.save("uploaded_image.jpg")

            myconfig = r"--psm 6 --oem 3"
            img = Image.open("uploaded_image.jpg")
            text = pytesseract.image_to_string(img, config=myconfig)

            choice = request.form.get("language_choice", "bn")
            t1 = Translator()
            op = t1.translate(text, dest=choice)

            return render_template("result.html", texts=[op.text])

    return render_template("index.html")

# Convert text to image
def text_to_image(text):
    width, height = 400, 200
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text = text.encode('utf-8').decode('latin-1')
    text_width, text_height = draw.textsize(text, font)
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    draw.text((x, y), text, fill="black", font=font)
    return image

# Serve PIL image
def serve_pil_image(pil_img):
    img_io = io.BytesIO()
    pil_img.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

# Create PDF from text
def create_pdf(text, pdf_filename):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    lines = text.split('\n')

    for line in lines:
        encoded_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, encoded_line)

    pdf.output(pdf_filename)


@app.route("/download", methods=["POST"])
def download_text():
    text = request.form.get("text")
    format_choice = request.form.get("format")

    if format_choice == "pdf":
        pdf_filename = "translated_text.pdf"
        create_pdf(text, pdf_filename)
        return send_file(pdf_filename, as_attachment=True)
    elif format_choice == "image":
        img = text_to_image(text)
        return serve_pil_image(img)

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0')

