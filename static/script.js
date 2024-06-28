function updateLastModified(course) {
    fetch(`/last_modified/${course}`)
        .then(response => response.json())
        .then(data => {
            const lastUpdatedElement = document.getElementById('lastUpdated');
            lastUpdatedElement.textContent = `Last Updated: ${data.last_modified_date}`;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function getGrades() {
    const course = document.getElementById('course').value;
    const studentId = document.getElementById('studentId').value;

    // Update the last modified timestamp
    updateLastModified(course);

    fetch(`/grades/${course}/${studentId}`)
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById('result');
            if (data.error) {
                resultDiv.innerHTML = `<p>${data.error}</p>`;
            } else {
                let gradesHtml = `<h2>Grades for Student ID: ${studentId}</h2><ul>`;
                const categories = ['Name', 'Assignment', 'Mid-term', 'Final Exam', 'Class Participation', 'Quiz'];
                categories.forEach(category => {
                    if (data.hasOwnProperty(category)) {
                        gradesHtml += `<li>${category}: ${data[category]}</li>`;
                    }
                });
                gradesHtml += '</ul>';
                resultDiv.innerHTML = gradesHtml;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}