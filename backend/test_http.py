import requests
import json

text = "I have extensive experience with Python, Java, and C++. I've led teams and delivered projects. My skills span full-stack development. I have worked on scaling systems. I contribute to open source projects."

response = requests.post(
    'http://localhost:8000/api/verify/deepfake',
    json={'text': text},
    timeout=10
)

print(f"Status Code: {response.status_code}")
print(f"Response:")
print(json.dumps(response.json(), indent=2))
