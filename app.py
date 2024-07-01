import os
import time
from flask import Flask, jsonify, render_template, request, send_file, make_response
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
import pytz

app = Flask(__name__)

# Set your local timezone here
LOCAL_TIMEZONE = 'Asia/Jakarta'  # Replace with your actual timezone

# Generate a version number based on the current timestamp
VERSION = str(int(time.time()))

@app.route('/')
def index():
    courses = get_courses()
    response = make_response(render_template('index.html', courses=courses, version=VERSION))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/last_modified/<course>')
def get_last_modified(course):
    last_modified_date = get_last_modified_date(course)
    return jsonify({'last_modified_date': last_modified_date})

@app.route('/grades/<course>/<student_id>')
def get_grades(course, student_id):
    grades, headers, separators = read_grades_from_csv(f'{course}.csv', student_id)
    if grades:
        return jsonify({
            'grades': grades,
            'headers': headers,
            'separators': separators
        })
    else:
        return jsonify({'error': 'Student ID not found'}), 404

@app.route('/export-pdf/<course>/<student_id>')
def export_pdf(course, student_id):
    grades, headers, separators = read_grades_from_csv(f'{course}.csv', student_id)
    if not grades:
        return jsonify({'error': 'Student ID not found'}), 404

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=inch/2, rightMargin=inch/2)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Gradebook for {course}", styles['Title']))
    elements.append(Paragraph(f"Student ID: {student_id}", styles['Heading2']))
    elements.append(Spacer(1, 12))

    data = [[header, grades.get(header, '-')] for header in headers]
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 24))

    # Add timestamp at the bottom with correct timezone
    local_tz = pytz.timezone(LOCAL_TIMEZONE)
    timestamp = datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    timestamp_text = f"Generated automatically by Martin Manullang Gradebook at {timestamp}"
    elements.append(Paragraph(timestamp_text, styles['Italic']))

    doc.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'gradebook_{course}_{student_id}.pdf', mimetype='application/pdf')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

def get_courses():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    return [file.rsplit('.', 1)[0] for file in csv_files]

def get_last_modified_date(course):
    csv_file = f'{course}.csv'
    with open(csv_file, 'r') as file:
        first_line = file.readline().strip().split(',')
        if first_line[0] == 'Last Updated':
            return first_line[1]
    return ''

def read_grades_from_csv(file_path, student_id):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        headers = lines[1].strip().split(',')
        separators = []
        cleaned_headers = []
        for i, header in enumerate(headers):
            cleaned_header = header.rstrip('|')
            cleaned_headers.append(cleaned_header)
            if header.endswith('|'):
                separators.append(i)
        
        for line in lines[2:]:
            values = line.strip().split(',')
            if values[0] == student_id:
                student_grades = {}
                for i, header in enumerate(cleaned_headers):
                    if i < len(values) and values[i].strip():
                        student_grades[header] = values[i].strip()
                return student_grades, cleaned_headers, separators
    return None, None, None

if __name__ == '__main__':
    app.run(debug=True)