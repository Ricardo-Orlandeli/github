from flask import Flask, request, render_template_string, redirect, url_for
import os
import shutil
from workflow_updated import ProjectManagementWorkflow

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'dataset', 'status_files')
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

HTML_FORM = '''
<!doctype html>
<title>Multi-Agent Project Management Demo</title>
<h2>Upload Project Status Files</h2>
<form method=post enctype=multipart/form-data>
  Cronograma: <input type=file name=cronograma required><br>
  Custos: <input type=file name=custos required><br>
  Escopo: <input type=file name=escopo required><br>
  Riscos: <input type=file name=riscos required><br>
  <input type=submit value='Run Workflow'>
</form>
{% if result %}
<h3>Workflow Result</h3>
<pre>{{ result }}</pre>
{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def upload_and_run():
    result = None
    if request.method == 'POST':
        # Save uploaded files
        files = {
            'cronograma': 'PROJ-0001_cronograma.txt',
            'custos': 'PROJ-0001_custos.txt',
            'escopo': 'PROJ-0001_escopo.txt',
            'riscos': 'PROJ-0001_riscos.txt'
        }
        for field, filename in files.items():
            file = request.files[field]
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        # Run workflow (sequential for demo)
        workflow = ProjectManagementWorkflow(process_type='sequential')
        results = workflow.run()
        if isinstance(results, list):
            result = '\n\n'.join(results)
        else:
            result = results
    return render_template_string(HTML_FORM, result=result)

if __name__ == '__main__':
    app.run(debug=True)
