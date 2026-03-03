#!/usr/bin/env python
"""Test deepfake detector directly"""

import sys
import asyncio

sys.path.insert(0, '.')

from services import get_deepfake_detector

async def test():
    text = "I have extensive experience with Python, Java, and C++. I've led teams and delivered projects. My skills span full-stack development. I have worked on scaling systems. I contribute to open source projects."
    
    try:
        detector = get_deepfake_detector(use_perplexity=False)
        print("✓ Detector initialized")
        
        result = await detector.analyze_resume_text(text)
        print(f"✓ Analysis complete")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test())
