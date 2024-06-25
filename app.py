from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import pandas as pd
import numpy as np
import pandas as pd          
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import chardet
import csv
import textwrap  




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['REPORT_FOLDER'] = 'reports/'
app.config['TEMPLATES_AUTO_RELOAD'] = True 

@app.route('/')
def index():
    print("Rendering index.html") # Debugging
    return render_template('index.html')  

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        print("No selected file")  # Debugging
        # return 'No selected file'
        return redirect(url_for('index'))
    # extra validation if someone uploads a .word file
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        print(f"File saved to {filepath}") # Debugging
        return redirect(url_for('process_file', filename=file.filename))
    else:
        return 'Invalid file type. Please upload a CSV file.'

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


@app.route('/process/<filename>')
def process_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Processing file {filepath}")  # Debugging

    # Detect encoding
    encoding = detect_encoding(filepath)
    print(f"Detected file encoding: {encoding}")

    # Attempt to read the CSV file with detected encoding
    try:
        data = pd.read_csv(filepath, encoding=encoding, quoting=csv.QUOTE_MINIMAL, on_bad_lines='error')
    except UnicodeDecodeError:
        print(f"Failed to read file with detected encoding, trying with iso-8859-1")  
        data = pd.read_csv(filepath, encoding='iso-8859-1', quoting=csv.QUOTE_MINIMAL, on_bad_lines='skip')
        print("First 3 rows of the data:") 
        print(data.head(3))
    except pd.errors.ParserError as e:
        print(f"ParserError: {e}")
        return redirect(url_for('index'))  
    pdf_path = os.path.join(app.config['REPORT_FOLDER'], f'{filename}.pdf')
    generate_pdf(data, pdf_path) 
    print(f"PDF generated at {pdf_path}") 
    return redirect(url_for('download_report', filename=f'{filename}.pdf')) 


# Generating a multi-page PDF with large data:
def generate_pdf(data, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)  
    c.drawString(100, 750, "Bandcamp Sales Report") 
    textobject = c.beginText(40, 700)  
    textobject.setFont("Helvetica", 12)  
    lines = data.to_string().split('\n')  
    for line in lines:
        textobject.textLine(line)  
    c.drawText(textobject)
    c.save()  
    print(f"PDF saved to {output_path}") 

@app.route('/reports/<filename>')
def download_report(filename):
    print(f"Downloading report {filename}")  # Debugging
    return send_from_directory(app.config['REPORT_FOLDER'], filename)  

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)  
    app.run(debug=True) 

