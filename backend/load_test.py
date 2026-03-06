"""
Load Testing Suite for Resume Verification System
Performance testing with Locust
Measures API response latency, throughput, and system stability
"""

from locust import HttpUser, task, constant_throughput, between
from locust.contrib.fasthttp import FastHttpUser
import random
import json
from datetime import datetime
import io


class ResumeUploadData:
    """Generate mock resume data for testing"""
    
    @staticmethod
    def generate_resume_pdf():
        """Generate mock PDF bytes"""
        # Minimal PDF structure for testing
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<< /Size 4 /Root 1 0 R >>
startxref
229
%%EOF
"""
        return pdf_content
    
    @staticmethod
    def generate_resume_text():
        """Generate mock resume text"""
        sample_data = {
            "name": f"Test Candidate {random.randint(1000, 9999)}",
            "email": f"candidate{random.randint(1000, 9999)}@example.com",
            "phone": f"555-{random.randint(1000, 9999)}",
            "summary": "Experienced software engineer with expertise in ML and distributed systems.",
            "experience": [
                {
                    "company": f"Tech Company {random.randint(1, 100)}",
                    "title": random.choice(["Software Engineer", "Senior Engineer", "Tech Lead"]),
                    "duration": f"{random.randint(1, 8)} years"
                }
            ],
            "skills": ["Python", "JavaScript", "Machine Learning", "FastAPI", "PostgreSQL"],
            "education": {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "university": "State University"
            }
        }
        return json.dumps(sample_data)


class ResumeVerificationUser(FastHttpUser):
    """Load test user for resume verification endpoints"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize user - register and login"""
        # Register user
        user_data = {
            "email": f"loadtest{random.randint(100000, 999999)}@example.com",
            "password": "TestPassword123!",
            "full_name": f"Load Test User {random.randint(1, 1000)}",
            "gdpr_consent": True
        }
        
        response = self.client.post(
            "/api/auth/register",
            json=user_data
        )
        
        if response.status_code == 201:
            self.user_data = response.json()
            self.access_token = self.user_data.get("access_token")
        else:
            # Try login if already registered
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            response = self.client.post(
                "/api/auth/login",
                json=login_data
            )
            if response.status_code == 200:
                self.user_data = response.json()
                self.access_token = self.user_data.get("access_token")
    
    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}"
        }
    
    @task
    def upload_resume(self):
        """Upload resume (high weight)"""
        files = {
            'file': ('resume.pdf', ResumeUploadData.generate_resume_pdf(), 'application/pdf')
        }
        
        response = self.client.post(
            "/api/resume/upload",
            files=files,
            headers=self.get_headers(),
            name="/api/resume/upload"
        )
        
        if response.status_code == 200:
            resume_data = response.json()
            self.resume_id = resume_data.get("resume_id")
    
    @task
    def get_resume_status(self):
        """Check resume processing status"""
        if hasattr(self, 'resume_id'):
            self.client.get(
                f"/api/resume/{self.resume_id}/status",
                headers=self.get_headers(),
                name="/api/resume/{resume_id}/status"
            )
    
    @task
    def check_similarity(self):
        """Check resume similarity and plagiarism"""
        if hasattr(self, 'resume_id'):
            self.client.post(
                "/api/ai/resume-similarity",
                json={"resume_id": self.resume_id},
                headers=self.get_headers(),
                name="/api/ai/resume-similarity"
            )
    
    @task
    def get_verification_report(self):
        """Get verification report"""
        if hasattr(self, 'resume_id'):
            self.client.get(
                f"/api/resume/{self.resume_id}/verification",
                headers=self.get_headers(),
                name="/api/resume/{resume_id}/verification"
            )
    
    @task
    def list_user_resumes(self):
        """List user's resumes"""
        self.client.get(
            "/api/resume/list",
            headers=self.get_headers(),
            name="/api/resume/list"
        )
    
    @task
    def get_user_profile(self):
        """Get user profile"""
        self.client.get(
            "/api/user/profile",
            headers=self.get_headers(),
            name="/api/user/profile"
        )


class AdminUser(FastHttpUser):
    """Load test admin user"""
    
    def on_start(self):
        """Admin login"""
        login_data = {
            "email": "admin@example.com",
            "password": "AdminPassword123!"
        }
        
        response = self.client.post(
            "/api/auth/login",
            json=login_data
        )
        
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
    
    def get_headers(self):
        """Get admin headers"""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    @task
    def get_system_metrics(self):
        """Get system metrics"""
        self.client.get(
            "/metrics",
            headers=self.get_headers()
        )
    
    @task
    def get_verification_stats(self):
        """Get verification statistics"""
        self.client.get(
            "/api/admin/stats",
            headers=self.get_headers()
        )


class HighLoadUser(FastHttpUser):
    """High load test user - more aggressive"""
    
    def on_start(self):
        """Initialize"""
        self.access_token = "test_token"
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}
    
    @task(5)
    def rapid_uploads(self):
        """Rapid resume uploads"""
        files = {
            'file': ('resume.pdf', ResumeUploadData.generate_resume_pdf(), 'application/pdf')
        }
        
        self.client.post(
            "/api/resume/upload",
            files=files,
            headers=self.get_headers(),
            name="/api/resume/upload"
        )
    
    @task(3)
    def rapid_api_calls(self):
        """Rapid API calls"""
        endpoints = [
            "/api/user/profile",
            "/api/resume/list",
            "/metrics"
        ]
        
        for endpoint in endpoints:
            self.client.get(
                endpoint,
                headers=self.get_headers(),
                name=endpoint
            )


# ===================== LOCUST CONFIGURATION =====================

if __name__ == "__main__":
    """
    Run load tests
    
    Command:
    locust -f load_test.py --host=http://localhost:8000 --users 100 --spawn-rate 10
    
    Options:
    --users: Number of concurrent users
    --spawn-rate: Rate to spawn new users
    --run-time: Duration of test (e.g., 1h)
    --headless: Run without UI
    --stats: Print stats
    """
    print("Resume Verification System - Load Testing")
    print("=" * 50)
    print("\nUsage:")
    print("  locust -f load_test.py --host=http://localhost:8000 --users 100")
    print("\nTest Scenarios:")
    print("  - 100 concurrent users uploading resumes")
    print("  - Checking verification status")
    print("  - Plagiarism detection")
    print("  - Admin metrics collection")
    print("\nMetrics Collected:")
    print("  - API response latency (avg, min, max)")
    print("  - Throughput (requests/sec)")
    print("  - Error rate")
    print("  - 95th percentile latency")
    print("  - Blockchain write time")
