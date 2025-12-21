#!/usr/bin/env python3
"""
Script simples para testar integração skill + agente
Gera 3 títulos virais baseado em um tópico
"""

import sys

def generate_titles(topic):
    """Gera 3 títulos virais para teste"""

    formulas = [
        f"🔥 {topic} em 5 MINUTOS (Impossível Falhar)",
        f"Por que TODOS estão falando sobre {topic}?",
        f"A verdade sobre {topic} que ninguém conta"
    ]

    return formulas

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_simple.py 'seu tópico aqui'")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    titles = generate_titles(topic)

    print(f"\n✅ Skill funcionando! 3 títulos para '{topic}':\n")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")

    print("\n💡 Skill pode ser chamada por agentes ou diretamente!")