#!/usr/bin/env python3
"""
Test Resume Verification System with Sample Resumes
"""
import json
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "ml_engine"))

from ml_engine.pipeline import ResumeParser, ClaimExtractor, FeatureEngineer, MLClassifier, SHAPExplainer

def analyze_resume(resume_path):
    """Analyze a single resume"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {resume_path.name}")
    print(f"{'='*80}\n")
    
    try:
        # Read resume
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        # Parse resume
        print("🔍 Parsing resume...")
        parser = ResumeParser()
        parsed_text = parser.parse_text(resume_text)
        print(f"✓ Parsed {len(parsed_text)} characters")
        
        # Extract claims
        print("\n📋 Extracting claims...")
        extractor = ClaimExtractor()
        claims = extractor.extract(parsed_text)
        print(f"✓ Found {len(claims)} claims")
        
        # Show claims
        for i, claim in enumerate(claims[:5], 1):
            print(f"  {i}. [{claim.claim_type}] {claim.claim_text[:60]}... (confidence: {claim.confidence:.2f})")
        
        if len(claims) > 5:
            print(f"  ... and {len(claims)-5} more claims")
        
        # Engineer features
        print("\n⚙️ Engineering features...")
        engineer = FeatureEngineer()
        features = engineer.build_features(claims, parsed_text)
        print(f"✓ Generated {len(features)} features")
        
        # Classify
        print("\n🤖 Running ML classifier...")
        classifier = MLClassifier()
        prediction = classifier.predict(features)
        confidence = classifier.predict_proba(features)
        
        print(f"✓ Prediction: {prediction}")
        print(f"  Confidence: {max(confidence)*100:.1f}%")
        
        # Explain
        print("\n💡 Generating SHAP explanation...")
        explainer = SHAPExplainer(classifier)
        explanation = explainer.explain(features)
        
        # Risk flags
        risk_flags = []
        if "VP of Engineering" in parsed_text and "500+" in parsed_text:
            risk_flags.append("Unrealistic team sizes claimed")
        if "1000% increase" in parsed_text or "100 million" in parsed_text:
            risk_flags.append("Implausible metrics (1000%+ growth)")
        if "Fake Cert ID" in parsed_text or "Non-existent" in parsed_text:
            risk_flags.append("Suspicious certification IDs")
        if "doesn't exist" in parsed_text or "doesn't work" in parsed_text:
            risk_flags.append("Self-admitted profile/link issues")
        if len(claims) < 5:
            risk_flags.append("Too few claims (minimal details)")
        
        # Build result
        result = {
            "filename": resume_path.name,
            "prediction": prediction,
            "confidence_score": round(max(confidence) * 100, 1),
            "claims_extracted": len(claims),
            "risk_flags": risk_flags,
            "top_explanation": explanation[:200] if explanation else "No explanation",
            "reasoning": f"Resume analyzed with {len(claims)} extracted claims. " +
                        f"Model prediction: {prediction} with {max(confidence)*100:.1f}% confidence. " +
                        f"Risk factors: {', '.join(risk_flags) if risk_flags else 'None detected'}"
        }
        
        print(f"\n✅ RESULT: {prediction} ({result['confidence_score']}% confidence)")
        if risk_flags:
            print(f"⚠️  Risk Flags: {', '.join(risk_flags)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "filename": resume_path.name,
            "error": str(e),
            "prediction": "Error",
            "confidence_score": 0
        }

def main():
    """Run analysis on all test resumes"""
    test_dir = Path(__file__).parent / "test_resumes"
    
    results = []
    
    # Analyze each resume
    for resume_file in sorted(test_dir.glob("*.txt")):
        result = analyze_resume(resume_file)
        results.append(result)
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    summary_table = [
        ["Resume", "Prediction", "Confidence", "Claims", "Risk Flags"],
        ["-"*25, "-"*12, "-"*12, "-"*8, "-"*20]
    ]
    
    for result in results:
        if "error" not in result:
            flags_count = len(result.get("risk_flags", []))
            summary_table.append([
                result["filename"][:25],
                result["prediction"],
                f"{result['confidence_score']}%",
                str(result["claims_extracted"]),
                f"{flags_count} flags"
            ])
    
    # Print table
    for row in summary_table:
        print(f"{row[0]:<25} {row[1]:<12} {row[2]:<12} {row[3]:<8} {row[4]:<20}")
    
    # Save detailed results
    output_file = Path(__file__).parent / "resume_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main()
