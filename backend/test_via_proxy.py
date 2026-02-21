#!/usr/bin/env python3
import requests
import time

# Test upload via Vite proxy (frontend dev server)
# This simulates what happens when you upload from the browser at localhost:3000

with open('../sample_resume.pdf', 'rb') as f:
    files = {'file': ('Fake-Resume.pdf', f, 'application/pdf')}
    
    # POST to the frontend dev server (which proxies to backend)
    try:
        r = requests.post('http://127.0.0.1:3000/api/resumes/upload', files=files, timeout=5)
        print(f'Status: {r.status_code}')
        print(f'Response: {r.text}')
        
        if r.status_code == 200:
            resume_id = r.json().get('resume_id')
            print(f'Resume ID: {resume_id}')
            
            # Poll for completion
            for i in range(5):
                rr = requests.get(f'http://127.0.0.1:3000/api/resumes/{resume_id}', timeout=5)
                print(f'Poll {i}: {rr.status_code} - Status: {rr.json().get("status")}')
                if rr.json().get('status') == 'completed':
                    print('✓ Upload successful!')
                    break
                time.sleep(1)
    except Exception as e:
        print(f'Error: {e}')
