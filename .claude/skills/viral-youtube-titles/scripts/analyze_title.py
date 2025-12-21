#!/usr/bin/env python3
"""
Analyze YouTube titles for viral potential and provide optimization suggestions.
"""

import sys
import json
from typing import Dict, List

# Power words database for analysis
POWER_WORDS = {
    "emotional": ["shocking", "insane", "mind-blowing", "revolutionary", "unbelievable", "crazy", "amazing", "incredible", "epic", "legendary"],
    "value": ["free", "easy", "simple", "fast", "ultimate", "complete", "master", "essential", "beginner", "advanced"],
    "urgency": ["now", "today", "finally", "new", "breaking", "just", "latest", "urgent", "immediate", "quick"],
    "credibility": ["proven", "scientific", "expert", "professional", "tested", "guaranteed", "official", "verified", "authentic"],
    "curiosity": ["secret", "hidden", "exposed", "revealed", "unknown", "mystery", "truth", "discover", "uncover"],
    "numbers": ["top", "best", "worst", "first", "last", "only", "every", "all", "most", "few"]
}

# Common viral patterns
VIRAL_PATTERNS = [
    "how to", "how i", "why you", "what if", "the truth about",
    "stop doing", "start doing", "nobody talks about", "everyone is",
    "i tried", "we tested", "the real reason", "you've been",
    "this is why", "here's how", "the secret to", "mistakes that"
]

def analyze_title_comprehensive(title: str) -> Dict:
    """
    Perform comprehensive analysis of a YouTube title.

    Args:
        title: The YouTube title to analyze

    Returns:
        Detailed analysis with scores and recommendations
    """
    analysis = {
        "title": title,
        "metrics": {},
        "scores": {},
        "strengths": [],
        "weaknesses": [],
        "recommendations": []
    }

    # Basic metrics
    analysis["metrics"]["character_count"] = len(title)
    analysis["metrics"]["word_count"] = len(title.split())

    # Mobile visibility check
    if len(title) <= 40:
        analysis["metrics"]["mobile_visibility"] = "Full"
    elif len(title) <= 70:
        analysis["metrics"]["mobile_visibility"] = "Partial"
    else:
        analysis["metrics"]["mobile_visibility"] = "Truncated"

    # Score calculations
    title_lower = title.lower()

    # 1. Length Score (10 points)
    char_count = len(title)
    if 50 <= char_count <= 60:
        analysis["scores"]["length"] = 10
        analysis["strengths"].append("Perfect length for all devices")
    elif 40 <= char_count <= 70:
        analysis["scores"]["length"] = 7
        if char_count < 50:
            analysis["weaknesses"].append("Title might be too short to convey value")
        else:
            analysis["weaknesses"].append("Title might be truncated on some devices")
    else:
        analysis["scores"]["length"] = 4
        analysis["weaknesses"].append("Title length is not optimal")
        analysis["recommendations"].append(f"Adjust length to 50-60 characters (currently {char_count})")

    # 2. Power Words Score (10 points)
    power_words_found = []
    for category, words in POWER_WORDS.items():
        for word in words:
            if word in title_lower:
                power_words_found.append((word, category))

    power_word_score = min(len(power_words_found) * 3, 10)
    analysis["scores"]["power_words"] = power_word_score
    analysis["metrics"]["power_words_found"] = [word for word, _ in power_words_found]

    if power_word_score >= 6:
        analysis["strengths"].append(f"Good use of power words: {', '.join(analysis['metrics']['power_words_found'])}")
    else:
        analysis["weaknesses"].append("Limited use of emotional trigger words")
        analysis["recommendations"].append("Add power words like: " + ", ".join(POWER_WORDS["emotional"][:3]))

    # 3. Number/Specificity Score (10 points)
    has_number = any(char.isdigit() for char in title)
    if has_number:
        analysis["scores"]["specificity"] = 10
        analysis["strengths"].append("Contains specific numbers (increases credibility)")
    else:
        analysis["scores"]["specificity"] = 5
        analysis["recommendations"].append("Consider adding specific numbers or data points")

    # 4. Curiosity Gap Score (10 points)
    curiosity_indicators = ["?", "how", "why", "what", "secret", "truth", "revealed", "exposed"]
    curiosity_count = sum(1 for indicator in curiosity_indicators if indicator in title_lower)

    if curiosity_count >= 2:
        analysis["scores"]["curiosity"] = 10
        analysis["strengths"].append("Strong curiosity gap created")
    elif curiosity_count == 1:
        analysis["scores"]["curiosity"] = 7
        analysis["strengths"].append("Some curiosity elements present")
    else:
        analysis["scores"]["curiosity"] = 4
        analysis["weaknesses"].append("Lacks curiosity-inducing elements")
        analysis["recommendations"].append("Create intrigue with questions or mystery elements")

    # 5. Viral Pattern Score (10 points)
    patterns_found = [pattern for pattern in VIRAL_PATTERNS if pattern in title_lower]
    if patterns_found:
        analysis["scores"]["viral_patterns"] = 10
        analysis["strengths"].append(f"Uses proven viral patterns: {', '.join(patterns_found)}")
        analysis["metrics"]["viral_patterns"] = patterns_found
    else:
        analysis["scores"]["viral_patterns"] = 5
        analysis["recommendations"].append("Consider using proven patterns like 'How I...' or 'Why You Should...'")

    # 6. Emoji Score (10 points)
    has_emoji = any(ord(char) > 127 for char in title)
    emoji_count = sum(1 for char in title if ord(char) > 127)

    if has_emoji:
        if emoji_count <= 2:
            analysis["scores"]["visual_appeal"] = 8
            analysis["strengths"].append("Good use of emojis for visual appeal")
        else:
            analysis["scores"]["visual_appeal"] = 5
            analysis["weaknesses"].append("Too many emojis might appear spammy")
            analysis["recommendations"].append("Limit emojis to 1-2 per title")
    else:
        analysis["scores"]["visual_appeal"] = 6
        analysis["recommendations"].append("Consider adding 1 strategic emoji for visual impact")

    # 7. Capitalization Check
    words = title.split()
    all_caps_words = [word for word in words if word.isupper() and len(word) > 1]

    if len(all_caps_words) > 2:
        analysis["weaknesses"].append("Excessive capitalization detected")
        analysis["recommendations"].append("Limit ALL CAPS to 1-2 words maximum")

    # Calculate total score
    total_score = sum(analysis["scores"].values())
    max_score = len(analysis["scores"]) * 10
    percentage = (total_score / max_score) * 100

    analysis["total_score"] = round(total_score, 1)
    analysis["max_score"] = max_score
    analysis["percentage"] = round(percentage, 1)

    # Overall rating
    if percentage >= 80:
        analysis["rating"] = "⭐⭐⭐⭐⭐ Excellent viral potential"
    elif percentage >= 65:
        analysis["rating"] = "⭐⭐⭐⭐ Good viral potential"
    elif percentage >= 50:
        analysis["rating"] = "⭐⭐⭐ Moderate potential"
    elif percentage >= 35:
        analysis["rating"] = "⭐⭐ Needs improvement"
    else:
        analysis["rating"] = "⭐ Major improvements needed"

    # Generate optimized variations
    analysis["suggested_variations"] = generate_optimized_variations(title, analysis)

    return analysis

def generate_optimized_variations(original_title: str, analysis: Dict) -> List[str]:
    """
    Generate optimized title variations based on analysis.

    Args:
        original_title: The original title
        analysis: The analysis results

    Returns:
        List of optimized title variations
    """
    variations = []

    # If title lacks numbers, add one
    if analysis["scores"].get("specificity", 0) < 10:
        variations.append(f"7 {original_title}")

    # If title lacks power words, add one
    if analysis["scores"].get("power_words", 0) < 7:
        variations.append(f"{original_title} (Mind-Blowing Results)")

    # If title lacks curiosity, make it a question
    if "?" not in original_title:
        variations.append(f"Why {original_title}?")

    # Create a controversy version
    variations.append(f"The Truth About {original_title}")

    # Create urgency version
    variations.append(f"{original_title} - Do This Now!")

    return variations[:3]  # Return top 3 variations

def print_analysis_report(analysis: Dict):
    """
    Print a formatted analysis report.

    Args:
        analysis: The analysis results dictionary
    """
    print("\n" + "=" * 70)
    print("📊 YOUTUBE TITLE VIRAL POTENTIAL ANALYSIS")
    print("=" * 70)

    print(f"\n📝 Title: {analysis['title']}")
    print(f"📏 Length: {analysis['metrics']['character_count']} characters")
    print(f"📱 Mobile: {analysis['metrics']['mobile_visibility']}")

    print(f"\n{analysis['rating']}")
    print(f"Score: {analysis['total_score']}/{analysis['max_score']} ({analysis['percentage']}%)")

    print("\n📈 DETAILED SCORES:")
    print("-" * 40)
    for category, score in analysis['scores'].items():
        bar = "█" * score + "░" * (10 - score)
        print(f"{category.replace('_', ' ').title():20} [{bar}] {score}/10")

    if analysis['strengths']:
        print("\n✅ STRENGTHS:")
        for strength in analysis['strengths']:
            print(f"  • {strength}")

    if analysis['weaknesses']:
        print("\n⚠️ WEAKNESSES:")
        for weakness in analysis['weaknesses']:
            print(f"  • {weakness}")

    if analysis['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"  {i}. {rec}")

    if analysis['suggested_variations']:
        print("\n🔄 SUGGESTED VARIATIONS:")
        for i, var in enumerate(analysis['suggested_variations'], 1):
            print(f"  {i}. {var}")

    print("\n" + "=" * 70)

def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_title.py '<title>'")
        print("Example: python analyze_title.py 'How I Built a $10K Business in 30 Days'")
        sys.exit(1)

    title = sys.argv[1]
    analysis = analyze_title_comprehensive(title)

    # Print formatted report
    print_analysis_report(analysis)

    # Option to output JSON
    if len(sys.argv) > 2 and sys.argv[2] == "--json":
        print("\n📄 JSON OUTPUT:")
        print(json.dumps(analysis, indent=2))

if __name__ == "__main__":
    main()