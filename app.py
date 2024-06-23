from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['REPORT_FOLDER'] = 'reports/'
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Disable template caching

@app.route('/')
def index():
    print("Rendering index.html")  # Debugging
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file part")  # Debugging
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        print("No selected file")  # Debugging
        return redirect(url_for('index'))
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        print(f"File saved to {filepath}")  # Debugging
        return redirect(url_for('process_file', filename=file.filename))

@app.route('/process/<filename>')
def process_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Processing file {filepath}")  # Debugging
    data = pd.read_csv(filepath)
    pdf_path = os.path.join(app.config['REPORT_FOLDER'], f'{filename}.pdf')
    generate_pdf(data, pdf_path)
    print(f"PDF generated at {pdf_path}")  # Debugging
    return redirect(url_for('download_report', filename=f'{filename}.pdf'))

def generate_pdf(data, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.drawString(100, 750, "Bandcamp Sales Report")
    textobject = c.beginText(40, 700)
    textobject.setFont("Helvetica", 12)
    lines = data.head().to_string().split('\n')
    for line in lines:
        textobject.textLine(line)
    c.drawText(textobject)
    c.save()
    print(f"PDF saved to {output_path}")  # Debugging

@app.route('/reports/<filename>')
def download_report(filename):
    print(f"Downloading report {filename}")  # Debugging
    return send_from_directory(app.config['REPORT_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
    app.run(debug=True)
