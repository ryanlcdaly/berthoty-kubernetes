from flask import Flask, request, render_template_string, send_from_directory
import subprocess
import os
import pymysql
from security import safe_command

aws_access_key_id = 'AKIAIOSFODNN72HYSDD8'
aws_secret = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ''
    # SQL Injection?
    db = pymysql.connect("localhost")
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password))

    if request.method == 'POST':
        if 'command' in request.form:
            cmd = request.form['command']
            process = safe_command.run(subprocess.Popen, cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                output = stdout.decode('utf-8')
            else:
                output = f"Error (Exit Code: {process.returncode}):\n{stderr.decode('utf-8')}"
        elif 'file' in request.files:
            uploaded_file = request.files['file']
            uploaded_file.save(os.path.join('/uploads', uploaded_file.filename))
            output = f"File {uploaded_file.filename} uploaded successfully!"
        elif 'sql' in request.form:
            sql = request.form['sql']
            cursor.execute(sql)
            output = 'SQL command executed successfully!'

    return render_template_string("""
        <h1>Intentionally Insecure App</h1>
        <form action="/" method="post">
            Run a command: <input type="text" name="command">
            <input type="submit" value="Run">
        </form>
        <br>
        <form action="/" method="post" enctype="multipart/form-data">
            Upload a file: <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
        <br>
        <form action="/" method="post">
            Inject some SQL <input type="text" name="sql">
            <input type="submit" value="Run">
        </form>
        <pre>{{output}}</pre>
    """, output=output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
