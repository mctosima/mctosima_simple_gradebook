import os
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
    grades = read_grades_from_csv(f'{course}.csv', student_id)
    if grades:
        return jsonify(grades)
    else:
        return jsonify({'error': 'Student ID not found'}), 404

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
        headers = [header.strip() for header in lines[1].strip().split(',')]
        for line in lines[2:]:
            values = line.strip().split(',')
            if values[0] == student_id:
                student_grades = dict(zip(headers, values))
                return student_grades
    return None

if __name__ == '__main__':
    app.run(debug=True)