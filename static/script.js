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
                document.getElementById('gradeAppealButton').style.display = 'none';
                document.getElementById('exportPdfButton').style.display = 'none';
            } else {
                let gradesHtml = `<h2>Grades for Student ID: ${studentId}</h2>`;
                gradesHtml += '<div class="grades-list">';
                
                data.headers.forEach((header, index) => {
                    gradesHtml += `<div class="grade-item">`;
                    gradesHtml += `<span class="grade-header">${header}:</span>`;
                    gradesHtml += `<span class="grade-value">${data.grades[header] || '-'}</span>`;
                    gradesHtml += `</div>`;
                    
                    if (data.separators.includes(index)) {
                        gradesHtml += `<hr class="grade-separator">`;
                    }
                });
                
                gradesHtml += '</div>';
                resultDiv.innerHTML = gradesHtml;
                
                // Show the Grade Appeal and Export to PDF buttons
                document.getElementById('gradeAppealButton').style.display = 'block';
                document.getElementById('exportPdfButton').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        getGrades();
    }
}

function openGradeAppealEmail() {
    const course = document.getElementById('course').value;
    const studentId = document.getElementById('studentId').value;
    const nameElement = document.querySelector('.grade-item:nth-child(2) .grade-value');
    
    if (!nameElement) {
        alert('Please retrieve grades before appealing.');
        return;
    }
    
    const name = nameElement.textContent;
    
    const subject = encodeURIComponent(`Sanggahan Nilai ${course} | ${name} | ${studentId}`);
    const body = encodeURIComponent(`Saya ${name}, dengan NIM ${studentId}, dari mata kuliah ${course}. Ingin melakukan sanggahan nilai sebagai berikut.`);
    
    window.location.href = `mailto:martin.manullang@if.itera.ac.id?subject=${subject}&body=${body}`;
}

function exportToPdf() {
    const course = document.getElementById('course').value;
    const studentId = document.getElementById('studentId').value;

    fetch(`/export-pdf/${course}/${studentId}`)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `gradebook_${course}_${studentId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate PDF. Please try again.');
        });
}

// Add event listeners when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('submitButton').addEventListener('click', getGrades);
    document.getElementById('studentId').addEventListener('keypress', handleKeyPress);
    document.getElementById('gradeAppealButton').addEventListener('click', openGradeAppealEmail);
    document.getElementById('exportPdfButton').addEventListener('click', exportToPdf);
});

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js').then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      }, err => {
        console.log('ServiceWorker registration failed: ', err);
      });
    });
  }