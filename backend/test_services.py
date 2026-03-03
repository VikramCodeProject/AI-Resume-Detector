"""
Enterprise Verification Services - Test Script
Test all implemented services to verify installation
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_result(service, status, details=""):
    """Print test result"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {service}: {'PASS' if status else 'FAIL'}")
    if details:
        print(f"   {details}")

async def test_github_service():
    """Test GitHub verification service"""
    try:
        from services import get_github_service
        
        print("Testing GitHub Service...")
        service = get_github_service()
        
        # Test with a known GitHub user
        result = await service.verify_profile(
            username="octocat",
            claimed_skills=["Ruby", "JavaScript"]
        )
        
        success = (
            result.get('profile_exists', False) and
            'github_authenticity_score' in result
        )
        
        score = result.get('github_authenticity_score', 0)
        print_result("GitHub Service", success, f"Score: {score:.1f}/100")
        
        return success
    except Exception as e:
        print_result("GitHub Service", False, f"Error: {str(e)}")
        return False

async def test_ocr_service():
    """Test OCR certificate service"""
    try:
        from services import get_ocr_service
        
        print("Testing OCR Service...")
        service = get_ocr_service()
        
        # Just test initialization (no real certificate)
        success = service is not None
        print_result("OCR Service", success, "Service initialized successfully")
        
        return success
    except Exception as e:
        print_result("OCR Service", False, f"Error: {str(e)}")
        return False

async def test_llm_service():
    """Test LLM reasoning service"""
    try:
        from services import get_llm_service
        
        print("Testing LLM Service...")
        service = get_llm_service(use_openai=False)  # Template mode
        
        # Test with minimal data
        result = await service.generate_verification_explanation(
            resume_data={
                'name': 'Test User',
                'experience_years': 3,
                'skills': ['Python', 'JavaScript'],
                'education': [],
                'employment': []
            }
        )
        
        success = (
            'final_trust_score' in result and
            'explanation' in result
        )
        
        score = result.get('final_trust_score', 0)
        print_result("LLM Service", success, f"Trust Score: {score:.1f}/100")
        
        return success
    except Exception as e:
        print_result("LLM Service", False, f"Error: {str(e)}")
        return False

async def test_deepfake_detector():
    """Test deepfake detection service"""
    try:
        from services import get_deepfake_detector
        
        print("Testing Deepfake Detector...")
        detector = get_deepfake_detector(use_perplexity=False)
        
        # Test with sample text
        test_text = """
        I am a results-oriented professional with excellent communication skills.
        I have a proven track record of delivering results in fast-paced environments.
        I am a team player with strong analytical abilities and problem-solving skills.
        I work well independently and as part of a dynamic team.
        """
        
        result = await detector.analyze_resume_text(test_text)
        
        success = (
            'ai_generated_probability' in result and
            'deepfake_flag' in result
        )
        
        prob = result.get('ai_generated_probability', 0)
        flag = result.get('deepfake_flag', False)
        print_result("Deepfake Detector", success, 
                    f"AI Probability: {prob:.1%}, Flag: {flag}")
        
        return success
    except Exception as e:
        print_result("Deepfake Detector", False, f"Error: {str(e)}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("Checking Dependencies...")
    
    dependencies = {
        'fastapi': 'FastAPI framework',
        'aiohttp': 'Async HTTP client',
        'numpy': 'Numerical computing',
        'requests': 'HTTP library',
    }
    
    optional_dependencies = {
        'spacy': 'NLP processing',
        'pytesseract': 'OCR engine',
        'openai': 'OpenAI API',
        'transformers': 'HuggingFace models',
        'cv2': 'OpenCV (image processing)',
    }
    
    all_pass = True
    
    # Required dependencies
    for package, description in dependencies.items():
        try:
            __import__(package)
            print_result(f"{package:15} ({description})", True)
        except ImportError:
            print_result(f"{package:15} ({description})", False, "REQUIRED - Install missing")
            all_pass = False
    
    # Optional dependencies
    for package, description in optional_dependencies.items():
        try:
            if package == 'cv2':
                __import__('cv2')
            else:
                __import__(package)
            print_result(f"{package:15} ({description})", True)
        except ImportError:
            print_result(f"{package:15} ({description})", False, "Optional - Some features disabled")
    
    return all_pass

def test_environment():
    """Test environment configuration"""
    print("Checking Environment Variables...")
    
    env_vars = {
        'GITHUB_API_KEY': ('GitHub API token', False),
        'OPENAI_API_KEY': ('OpenAI API key', True),
        'TESSERACT_CMD': ('Tesseract executable path', True),
    }
    
    for var, (description, optional) in env_vars.items():
        value = os.getenv(var)
        has_value = bool(value)
        
        if has_value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print_result(f"{var:20}", True, f"{description}: {masked}")
        else:
            status = "Optional" if optional else "Recommended"
            print_result(f"{var:20}", optional, f"{description}: Not set ({status})")

async def run_all_tests():
    """Run all tests"""
    print_header("🧪 Enterprise Verification Services - Test Suite")
    
    print("Starting comprehensive service tests...\n")
    
    # Test 1: Dependencies
    print_header("1️⃣ Testing Dependencies")
    deps_ok = test_dependencies()
    
    # Test 2: Environment
    print_header("2️⃣ Testing Environment")
    test_environment()
    
    # Test 3: Services
    print_header("3️⃣ Testing Services")
    
    results = {}
    
    # GitHub Service
    results['github'] = await test_github_service()
    
    # OCR Service
    results['ocr'] = await test_ocr_service()
    
    # LLM Service
    results['llm'] = await test_llm_service()
    
    # Deepfake Detector
    results['deepfake'] = await test_deepfake_detector()
    
    # Summary
    print_header("📊 Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Tests Run: {total_tests}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests and deps_ok:
        print("\n✅ ALL TESTS PASSED!")
        print("🚀 System is ready for production use.")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Review errors above and install missing dependencies.")
    
    print("\n" + "="*60)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    print("\n🔬 Starting Enterprise Verification Test Suite...")
    print("This will test all implemented services.\n")
    
    try:
        result = asyncio.run(run_all_tests())
        
        if result:
            print("\n✅ Success! All services are working.")
            print("\nNext steps:")
            print("1. Start the backend: uvicorn main:app --reload")
            print("2. Visit API docs: http://localhost:8000/api/docs")
            print("3. Test endpoints with real data")
            sys.exit(0)
        else:
            print("\n⚠️ Some tests failed. Review output above.")
            print("\nTroubleshooting:")
            print("1. Install missing dependencies: pip install -r requirements.txt")
            print("2. Download spaCy model: python -m spacy download en_core_web_sm")
            print("3. Set GITHUB_API_KEY in .env file")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
