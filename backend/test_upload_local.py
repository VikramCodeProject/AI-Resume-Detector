from fastapi.testclient import TestClient
from test_server import app
import time

client = TestClient(app)

with open('../sample_resume.pdf','rb') as f:
    files = {'file': ('sample_resume.pdf', f, 'application/pdf')}
    r = client.post('/resumes/upload', files=files)
    print('POST', r.status_code, r.json())
    if r.status_code==200:
        resume_id = r.json().get('resume_id')
        for i in range(6):
            rr = client.get(f'/resumes/{resume_id}')
            print('GET', i, rr.status_code, rr.json().get('status'))
            if rr.json().get('status')=='completed':
                print('Final:', rr.json())
                break
            time.sleep(1)
