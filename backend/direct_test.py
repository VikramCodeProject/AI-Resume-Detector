#!/usr/bin/env python
"""Direct test of deepfake detector"""
import sys
import traceback

try:
    from services import get_deepfake_detector
    print("✓ Imported deepfake_detector")
    
    detector = get_deepfake_detector(use_perplexity=False)
    print("✓ Created detector instance")
    
    text = "I have extensive experience with Python, Java, and C++. I've led teams and delivered projects. My skills span full-stack development. I have worked on scaling systems. I contribute to open source projects."
    print(f"✓ Text ready ({len(text)} chars)")
    
    # Test synchronous method first
    import asyncio
    result = asyncio.run(detector.analyze_resume_text(text))
    print(f"✓ Analysis complete:")
    
    import json
    print(json.dumps(result, indent=2, default=str))
    
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}")
    print(f"  Message: {e}")
    traceback.print_exc()
