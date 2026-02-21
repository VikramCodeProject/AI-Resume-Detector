import requests
import time

print("Testing upload via Vite dev server proxy (localhost:3001 -> localhost:8000)")

# Create test file
test_file_path = r"c:\Users\ACER\Desktop\UsMiniProject\Fake-Resume.pdf"
with open(test_file_path, 'wb') as f:
    f.write(b"Test resume content")

time.sleep(1)

try:
    with open(test_file_path, 'rb') as f:
        files = {'file': ('Fake-Resume.pdf', f, 'application/pdf')}
        
        # This is what the frontend sends to localhost:3001/api/resumes/upload
        # which Vite proxies to localhost:8000/resumes/upload
        r = requests.post(
            'http://127.0.0.1:3001/api/resumes/upload',
            files=files,
            timeout=10
        )
        
        print(f"\n=== Response from localhost:3001/api/resumes/upload ===")
        print(f"Status Code: {r.status_code}")
        print(f"Headers: {dict(r.headers)}")
        print(f"Body: {r.text}")
        
        if r.status_code == 200:
            print("\n✓ Upload successful via proxy!")
            data = r.json()
            print(f"Resume ID: {data.get('resume_id')}")
        else:
            print(f"\n✗ Upload failed via proxy")
            
except Exception as e:
    print(f"Error: {e}")
