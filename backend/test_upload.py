import requests
import time

FILES = {'file': ('sample_resume.pdf', open('../sample_resume.pdf','rb'), 'application/pdf')}

res = requests.post('http://127.0.0.1:8000/resumes/upload', files=FILES)
print('POST status:', res.status_code)
print(res.json())

if res.status_code==200:
    resume_id = res.json().get('resume_id')
    # Poll for completion
    for i in range(6):
        r = requests.get(f'http://127.0.0.1:8000/resumes/{resume_id}')
        print('GET', i, r.status_code, r.json().get('status'))
        if r.json().get('status') == 'completed':
            print('Final data:', r.json())
            break
        time.sleep(1)
