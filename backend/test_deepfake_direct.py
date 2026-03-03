import asyncio
import json
from services import get_deepfake_detector

async def test():
    text = "I have extensive experience with Python, Java, and C++. I've led teams and delivered projects. My skills span full-stack development. I have worked on scaling systems. I contribute to open source projects."
    detector = get_deepfake_detector(use_perplexity=False)
    result = await detector.analyze_resume_text(text)
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(test())
