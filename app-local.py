import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    courses = get_courses()
    return render_template('index.html', courses=courses)

@app.route('/last_modified/<course>')
def get_last_modified(course):
    last_modified_date = get_last_modified_date(course)
    return jsonify({'last_modified_date': last_modified_date})

@app.route('/grades/<course>/<student_id>')
def get_grades(course, student_id):
    grades = read_grades_from_csv(f'{course}.csv')
    student_grades = grades.get(student_id)
    
    if student_grades:
        return jsonify(student_grades)
    else:
        return jsonify({'error': 'Student ID not found'}), 404

def get_courses():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    return [file.rsplit('.', 1)[0] for file in csv_files]

def get_last_modified_date(course):
    csv_file = f'{course}.csv'
    last_modified = os.path.getmtime(csv_file)
    return datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')

def read_grades_from_csv(file_path):
    grades = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        headers = lines[0].strip().split(',')
        for line in lines[1:]:
            values = line.strip().split(',')
            student_id = values[0]
            student_grades = {header: value for header, value in zip(headers[1:], values[1:])}
            grades[student_id] = student_grades
    return grades

if __name__ == '__main__':
    app.run(debug=True)