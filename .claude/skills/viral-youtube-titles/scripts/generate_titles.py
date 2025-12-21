#!/usr/bin/env python3
"""
Generate viral YouTube title variations based on input topic and niche.
"""

import random
import json
from typing import List, Dict

# Power words database
POWER_WORDS = {
    "emotional": ["Shocking", "Insane", "Mind-Blowing", "Revolutionary", "Unbelievable", "Crazy", "Amazing"],
    "value": ["Free", "Easy", "Simple", "Fast", "Ultimate", "Complete", "Master", "Essential"],
    "urgency": ["Now", "Today", "Finally", "New", "Breaking", "Just Released", "Latest"],
    "credibility": ["Proven", "Scientific", "Expert", "Professional", "Tested", "Guaranteed", "Official"],
    "curiosity": ["Secret", "Hidden", "Exposed", "Revealed", "Unknown", "Mystery", "Truth"],
    "numbers": ["Top", "Best", "Worst", "First", "Last", "Only", "Every", "All"]
}

# Title formulas
FORMULAS = {
    "number_list": {
        "patterns": [
            "{number} {adjective} {topic} That {result}",
            "{number} {topic} {audience} Need to Know",
            "Top {number} {topic} in {year}",
            "{number} {topic} Mistakes Everyone Makes"
        ],
        "numbers": ["5", "7", "10", "15", "21", "30"],
    },
    "question": {
        "patterns": [
            "Why {topic} {action}?",
            "Is {topic} {status}?",
            "What If {topic} {scenario}?",
            "How {topic} {transformation}?"
        ]
    },
    "transformation": {
        "patterns": [
            "How I {action} in {timeframe}",
            "From {start} to {end}: My {topic} Journey",
            "{topic}: {timeframe} Challenge Results",
            "I Tried {topic} for {timeframe} - Here's What Happened"
        ],
        "timeframes": ["24 Hours", "7 Days", "30 Days", "3 Months", "1 Year"]
    },
    "controversy": {
        "patterns": [
            "Why {topic} Is {controversial_take}",
            "The Truth About {topic} Nobody Talks About",
            "{topic} Is a Lie - Here's Why",
            "Stop {action} - Do This Instead"
        ]
    },
    "comparison": {
        "patterns": [
            "{option1} vs {option2}: The Clear Winner",
            "{topic} Comparison: Which Is Best?",
            "I Tested Every {topic} - Here's The Best",
            "{option1} or {option2}? The Answer Surprised Me"
        ]
    }
}

def generate_titles(topic: str, niche: str = "general", count: int = 10) -> List[Dict[str, str]]:
    """
    Generate multiple viral title variations for a given topic.

    Args:
        topic: The main subject of the video
        niche: The content niche (gaming, tech, education, lifestyle, etc.)
        count: Number of title variations to generate

    Returns:
        List of dictionaries containing title and metadata
    """
    titles = []

    # Generate titles using different formulas
    for _ in range(count):
        formula_type = random.choice(list(FORMULAS.keys()))
        formula = FORMULAS[formula_type]
        pattern = random.choice(formula["patterns"])

        # Build title based on formula
        if formula_type == "number_list":
            title = pattern.format(
                number=random.choice(formula["numbers"]),
                adjective=random.choice(POWER_WORDS["emotional"]),
                topic=topic,
                result=f"Will {random.choice(['Change Your Life', 'Blow Your Mind', 'Save You Hours', 'Make You Money'])}",
                audience="You",
                year="2024"
            )
        elif formula_type == "question":
            title = pattern.format(
                topic=topic,
                action=random.choice(["Really Works", "Changes Everything", "Matters", "Is Important"]),
                status=random.choice(["Dead", "The Future", "Worth It", "Overrated"]),
                scenario=random.choice(["Disappeared Tomorrow", "Was Free", "Could Talk"]),
                transformation=random.choice(["Became Popular", "Works So Well", "Failed"])
            )
        elif formula_type == "transformation":
            title = pattern.format(
                action=f"Mastered {topic}",
                timeframe=random.choice(formula["timeframes"]),
                start="Zero",
                end="Hero",
                topic=topic,
                scenario="Changed Everything"
            )
        elif formula_type == "controversy":
            title = pattern.format(
                topic=topic,
                controversial_take=random.choice(["Killing Your Productivity", "Not What You Think", "Actually Bad For You", "A Scam"]),
                action=f"Using {topic} Wrong"
            )
        elif formula_type == "comparison":
            title = pattern.format(
                option1=f"New {topic}",
                option2=f"Old {topic}",
                topic=topic
            )

        # Add power word if not already present
        if not any(word in title for word_list in POWER_WORDS.values() for word in word_list):
            power_category = random.choice(list(POWER_WORDS.keys()))
            power_word = random.choice(POWER_WORDS[power_category])
            title = f"{power_word}: {title}"

        # Add emoji occasionally (30% chance)
        if random.random() < 0.3:
            emoji = random.choice(["🔥", "😱", "🚨", "💰", "🎯", "⚡", "🤯"])
            title = f"{emoji} {title}"

        # Calculate metrics
        char_count = len(title)
        has_number = any(char.isdigit() for char in title)

        titles.append({
            "title": title,
            "formula": formula_type,
            "char_count": char_count,
            "has_number": has_number,
            "mobile_safe": char_count <= 40,
            "optimal_length": 50 <= char_count <= 60
        })

    return titles

def analyze_title(title: str) -> Dict[str, any]:
    """
    Analyze an existing title for viral potential.

    Args:
        title: The YouTube title to analyze

    Returns:
        Dictionary with analysis results and score
    """
    analysis = {
        "title": title,
        "char_count": len(title),
        "scores": {}
    }

    # Length score (optimal: 50-60 chars)
    if 50 <= len(title) <= 60:
        analysis["scores"]["length"] = 10
    elif 40 <= len(title) <= 70:
        analysis["scores"]["length"] = 7
    else:
        analysis["scores"]["length"] = 4

    # Power word score
    power_word_count = sum(1 for category in POWER_WORDS.values()
                          for word in category if word.lower() in title.lower())
    analysis["scores"]["power_words"] = min(power_word_count * 3, 10)

    # Number presence
    analysis["scores"]["has_number"] = 10 if any(char.isdigit() for char in title) else 5

    # Question mark bonus
    analysis["scores"]["is_question"] = 8 if "?" in title else 5

    # Emoji presence
    has_emoji = any(ord(char) > 127 for char in title)
    analysis["scores"]["has_emoji"] = 7 if has_emoji else 5

    # Calculate total score
    total_score = sum(analysis["scores"].values()) / len(analysis["scores"])
    analysis["total_score"] = round(total_score, 1)

    # Rating
    if total_score >= 8:
        analysis["rating"] = "Excellent viral potential"
    elif total_score >= 6:
        analysis["rating"] = "Good viral potential"
    elif total_score >= 4:
        analysis["rating"] = "Average potential"
    else:
        analysis["rating"] = "Needs improvement"

    # Recommendations
    recommendations = []
    if analysis["scores"]["length"] < 7:
        recommendations.append("Adjust title length to 50-60 characters")
    if analysis["scores"]["power_words"] < 6:
        recommendations.append("Add emotional or value-driven power words")
    if not any(char.isdigit() for char in title):
        recommendations.append("Consider adding numbers for specificity")

    analysis["recommendations"] = recommendations

    return analysis

def main():
    """Main function for command-line usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_titles.py '<topic>' [niche] [count]")
        print("Example: python generate_titles.py 'Python Programming' tech 15")
        sys.exit(1)

    topic = sys.argv[1]
    niche = sys.argv[2] if len(sys.argv) > 2 else "general"
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    print(f"\n🎬 Generating {count} viral title variations for: {topic}\n")
    print("-" * 60)

    titles = generate_titles(topic, niche, count)

    for i, title_data in enumerate(titles, 1):
        print(f"\n{i}. {title_data['title']}")
        print(f"   Formula: {title_data['formula']}")
        print(f"   Length: {title_data['char_count']} chars", end="")
        if title_data['optimal_length']:
            print(" ✅ (optimal)")
        elif title_data['mobile_safe']:
            print(" ⚠️ (short)")
        else:
            print(" ⚠️ (check mobile)")

    print("\n" + "-" * 60)
    print("\n💡 Tips:")
    print("- Test 3-5 variations with your audience")
    print("- Match title promise with video content")
    print("- Track CTR and adjust formula accordingly")

if __name__ == "__main__":
    main()