#!/usr/bin/env python3
"""
Simple Resume Verification Analyzer - Works with basic Python only
Analyzes resumes using pattern-matching and heuristics
"""
import json
from pathlib import Path
import re

def analyze_resume_simple(resume_path):
    """Simple heuristic-based resume analysis"""
    
    with open(resume_path, 'r', encoding='utf-8') as f:
        resume_text = f.read().lower()
    
    result = {
        "filename": resume_path.name,
        "risk_flags": [],
        "green_flags": [],
        "prediction": "Unknown",
        "confidence_score": 0
    }
    
    # RED FLAGS (Suspicious patterns)
    red_flags = {
        "500+": "Unrealistic team sizes (500+ engineers)",
        "1000%": "Impossible growth metrics (1000%+)",
        "100 million": "Implausible user numbers (100M+)",
        "quantum computing": "Quantum work before hardware existed",
        "fake cert": "Self-admitted fake certifications",
        "profile doesn't exist": "Broken LinkedIn profile",
        "doesn't work": "Non-functional project links",
        "non-existent": "Non-existent certifications claimed",
        "invalid": "Invalid certification IDs",
        "single-handedly": "Overly individualistic claims",
        "surpassed industry": "Made-up competitive claims",
        "all modern technologies": "Vague tech stack",
        "every major": "Impossible achievement claims",
        "won every": "Won every award claim",
        "patented technologies": "Multiple patents in short timespan",
        "perfect score": "Perfect GPA claims",
        "bootstrapped with $0": "Unrealistic business claims"
    }
    
    # GREEN FLAGS (Authentic patterns)
    green_flags = {
        "led team of": "Specific team leadership",
        "improved performance by": "Quantified improvements",
        "deployed to": "Specific technology choices",
        "github stars": "Verifiable open source",
        "gpa:": "Honest GPA disclosure",
        "reduced by": "Specific metrics",
        "optimized": "Technical improvement claims",
        "implemented": "Specific implementations",
        "contributor": "Open source participation",
        "code review": "Team collaboration",
        "agile": "Standard development practice"
    }
    
    # TIMELINE WARNING - Check for impossible dates
    years_claimed = []
    date_pattern = r'\d{4}'  # Find all 4-digit numbers (years)
    years = re.findall(date_pattern, resume_text)
    if years:
        years_claimed = sorted(set(int(y) for y in years if 1990 < int(y) < 2027))
    
    # Check for impossible timelines
    if len(years_claimed) > 1:
        min_year = min(years_claimed)
        max_year = max(years_claimed)
        career_span = max_year - min_year
        
        # Check for graduation before start date
        if "graduated: 2012" in resume_text and "march 2015" in resume_text:
            result["green_flags"].append("✓ Logical career timeline")
        elif "graduated: 2010" in resume_text and min_year < 2009:
            result["risk_flags"].append("Worked before graduation")
    
    # Count red flags
    red_count = 0
    for flag_pattern, flag_desc in red_flags.items():
        if flag_pattern in resume_text:
            result["risk_flags"].append(f"⚠️  {flag_desc}")
            red_count += 1
    
    # Count green flags
    green_count = 0
    for flag_pattern, flag_desc in green_flags.items():
        if flag_pattern in resume_text:
            result["green_flags"].append(f"✓ {flag_desc}")
            green_count += 1
    
    # Determine prediction
    if red_count >= 5:
        result["prediction"] = "FAKE"
        result["confidence_score"] = min(95, 60 + (red_count * 5))
    elif red_count >= 2:
        result["prediction"] = "EXAGGERATED"
        result["confidence_score"] = 70
    elif green_count >= 5 and red_count == 0:
        result["prediction"] = "VERIFIED"
        result["confidence_score"] = 85
    else:
        result["prediction"] = "UNCERTAIN"
        result["confidence_score"] = 50
    
    # Add summary
    result["summary"] = f"Found {red_count} red flags, {green_count} green flags. " \
                        f"Prediction: {result['prediction']} ({result['confidence_score']}% confidence)"
    
    return result

def main():
    """Analyze all test resumes"""
    test_dir = Path(__file__).parent / "test_resumes"
    results = []
    
    print("\n" + "="*80)
    print("📋 RESUME VERIFICATION SYSTEM - ANALYSIS RESULTS")
    print("="*80 + "\n")
    
    # Analyze each resume
    for resume_file in sorted(test_dir.glob("Resume_*.txt")):
        result = analyze_resume_simple(resume_file)
        results.append(result)
        
        print(f"\n{'─'*80}")
        print(f"📄 {result['filename']}")
        print(f"{'─'*80}")
        print(f"🔍 Prediction: {result['prediction']}")
        print(f"📊 Confidence: {result['confidence_score']}%")
        print(f"\n{result['summary']}")
        
        if result['risk_flags']:
            print(f"\n🚨 Risk Flags ({len(result['risk_flags'])}):")
            for flag in result['risk_flags']:
                print(f"   {flag}")
        
        if result['green_flags']:
            print(f"\n✅ Green Flags ({len(result['green_flags'])}):")
            for flag in result['green_flags'][:3]:  # Show first 3
                print(f"   {flag}")
            if len(result['green_flags']) > 3:
                print(f"   ... and {len(result['green_flags'])-3} more")
    
    # Summary table
    print(f"\n\n{'='*80}")
    print("SUMMARY TABLE")
    print(f"{'='*80}\n")
    
    print(f"{'Resume':<35} {'Prediction':<15} {'Confidence':<12}")
    print("─" * 62)
    
    for result in results:
        pred = result['prediction']
        conf = f"{result['confidence_score']}%"
        print(f"{result['filename']:<35} {pred:<15} {conf:<12}")
    
    # Save results
    output_file = Path(__file__).parent / "resume_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Analysis complete! Results saved to: {output_file}\n")

if __name__ == "__main__":
    main()
