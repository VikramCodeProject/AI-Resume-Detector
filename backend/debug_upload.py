import subprocess
import sys
import time
import requests
import os

python = r"c:\Users\ACER\Desktop\UsMiniProject\.venv\Scripts\python.exe"
cmd = [python, "-m", "uvicorn", "test_server:app", "--host", "127.0.0.1", "--port", "8000"]

p = subprocess.Popen(cmd, cwd=r"c:\Users\ACER\Desktop\UsMiniProject\backend")
print('Started uvicorn pid', p.pid)
time.sleep(1.5)

try:
    # Create a test file
    test_file_path = r"c:\Users\ACER\Desktop\UsMiniProject\Fake-Resume.pdf"
    with open(test_file_path, 'wb') as f:
        f.write(b"Test resume content for Fake-Resume.pdf")
    
    print(f"\n=== Testing upload to http://127.0.0.1:8000/resumes/upload ===")
    with open(test_file_path, 'rb') as f:
        files = {'file': ('Fake-Resume.pdf', f, 'application/pdf')}
        r = requests.post('http://127.0.0.1:8000/resumes/upload', files=files, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            resume_id = r.json().get('resume_id')
            print(f"\nUpload successful! Resume ID: {resume_id}")
            print("\nPolling for completion...")
            for i in range(6):
                rr = requests.get(f'http://127.0.0.1:8000/resumes/{resume_id}', timeout=5)
                status = rr.json().get('status')
                print(f"Poll {i}: {status}")
                if status == 'completed':
                    print("✓ Processing completed!")
                    break
                time.sleep(1)
        else:
            print(f"ERROR: Upload failed with status {r.status_code}")
            print(f"Error details: {r.text}")
            
finally:
    print("\nTerminating backend...")
    p.terminate()
    p.wait(timeout=5)
