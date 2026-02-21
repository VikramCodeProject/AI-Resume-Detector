import subprocess
import sys
import time
import requests
import os

python = r"c:\Users\ACER\Desktop\UsMiniProject\.venv\Scripts\python.exe"
cmd = [python, "-m", "uvicorn", "test_server:app", "--host", "127.0.0.1", "--port", "8000"]

p = subprocess.Popen(cmd, cwd=os.path.dirname(__file__))
print('Started uvicorn pid', p.pid)
try:
    # wait for server to start
    time.sleep(1.5)
    with open(os.path.join(os.path.dirname(__file__), '..', 'sample_resume.pdf'), 'rb') as f:
        files = {'file': ('sample_resume.pdf', f, 'application/pdf')}
        r = requests.post('http://127.0.0.1:8000/resumes/upload', files=files)
        print('POST', r.status_code, r.text)
        if r.status_code==200:
            resume_id = r.json().get('resume_id')
            for i in range(6):
                rr = requests.get(f'http://127.0.0.1:8000/resumes/{resume_id}')
                print('GET', i, rr.status_code, rr.json().get('status'))
                if rr.json().get('status')=='completed':
                    print('Final:', rr.json())
                    break
                time.sleep(1)
finally:
    p.terminate()
    print('Terminated uvicorn')
