# app.py
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
import google.generativeai as genai
from docx import Document
from docx.shared import Inches

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

doc_stream = None
# openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key="AIzaSyAJMRq6IlbLTA-bbnxTWjpYB59cUl_H7o0")

# Function to generate text using GPT-3


def generate_text(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(
        max_output_tokens=(35*3),
    ))
    return response.text


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index1.html', document_url=None)


@app.route('/upload', methods=['POST'])
def upload():

    # file = request.files['file']
    files = request.files.getlist('files')
    edited_images = []

    for file in files:
        if file and allowed_file(file.filename):
            # Process the image
            img = Image.open(file)

            draw = ImageDraw.Draw(img)
            font_size = 20
            font_path = os.path.join(app.root_path, 'fonts', 'ARIAL.TTF')
            font = ImageFont.truetype(font_path, font_size)

            event_name = request.form.get('event_name', 'Your Event Name')

            # Calculate the rectangle coordinates to center it at the top with a small gap
            rect_height = 35
            gap = 30  # Adjust the gap as needed
            rect_width = draw.textsize(event_name, font=font)[
                0] + 2 * gap  # Add some padding
            rect_coordinates = [img.width // 2 - rect_width // 2, gap,
                                img.width // 2 + rect_width // 2, gap + rect_height]

            # Draw the white rectangle
            draw.rectangle(rect_coordinates, fill=(255, 255, 255))

            # Calculate the text position to center it within the rectangle
            text_width, text_height = draw.textsize(event_name, font=font)
            text_position = ((img.width - text_width) // 2,
                             gap + (rect_height - text_height) // 2)

            # Draw the event name text
            draw.text(text_position, event_name, font=font, fill=(0, 0, 0))

            # text_position = (10, 10)
            # text_color = (0, 0, 0)

            # draw.rectangle([0, 0, img.width, 50], fill=(255, 255, 255))
            # draw.text(text_position, event_name, font=font, fill=text_color)

            # Save the edited image to a BytesIO object
            edited_image_stream = BytesIO()
            img.save(edited_image_stream, format='PNG')
            edited_image_stream.seek(0)

            edited_images.append(edited_image_stream)
        else:
            return render_template('index1.html', error='Invalid file format')

        # Generate text using GPT-3
    context = request.form.get('context', 'Your event context here.')

    rephrased_context = generate_text(context)

    # Create a Word document with the image and rephrased context
    document = Document()
    document.add_heading(event_name, level=1)
    # document.add_picture(edited_image_stream, width=Inches(4.0))
    for edited_image_stream in (edited_images):
        document.add_picture(edited_image_stream, width=Inches(4.0))
    document.add_paragraph('Rephrased Context:')
    document.add_paragraph(rephrased_context)

    # Save the document to a BytesIO object
    doc_stream = BytesIO()
    document.save(doc_stream)

    doc_stream.seek(0)
    return send_file(BytesIO(doc_stream.read()),
                     mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     as_attachment=True, download_name='output_document.docx')
    # Return template with download link
    # return render_template('index1.html', document_url='/download', doc_stream=doc_stream)


# if __name__ == '__main__':
#     app.run(debug=True)
