"""
topics.py - Dados dos temas de pesquisa mostrados na Home (um único lugar).

Cada tema: título, frase curta, pergunta de exemplo (leva à Search), SVG e emoji de reserva e cores (imagem, fundo do card e borda, todas da mesma família).
"""

from pathlib import Path

TOPICS_DIR = Path(__file__).resolve().parent.parent / "assets" / "topics"

TOPICS = [
    {
        "title": "Screen time and mental health",
        "text": "Anxiety, depression and well-being in young people",
        "question": "How does screen time affect children's mental health?",
        "svg": "mental_health.svg", "emoji": "🧠", "color": "#E9D5FF", "tint": "#FAF5FF", "border": "#E9D5FF",
    },
    {
        "title": "Digital media and childhood obesity",
        "text": "Sedentary behavior, snacking and body weight",
        "question": "What is the relationship between digital media use and childhood obesity?",
        "svg": "obesity.svg", "emoji": "🍔", "color": "#FDE68A", "tint": "#FFFBEB", "border": "#FDE68A",
    },
    {
        "title": "Impact on sleep and sleep quality",
        "text": "Bedtime use, duration and sleep disruption",
        "question": "How does screen use before bedtime affect children's sleep?",
        "svg": "sleep.svg", "emoji": "😴", "color": "#F28F43", "tint": "#FFF4EA", "border": "#F9D2B0",
    },
    {
        "title": "Cognitive development and learning",
        "text": "Attention, language and school performance",
        "question": "What is the impact of screen time on cognitive development and learning?",
        "svg": "cognitive.svg", "emoji": "📚", "color": "#BBF7D0", "tint": "#F0FDF4", "border": "#BBF7D0",
    },
    {
        "title": "Behavior and socialization",
        "text": "Peer relationships, play and social skills",
        "question": "How does screen time influence children's behavior and social skills?",
        "svg": "behavior.svg", "emoji": "💬", "color": "#FBCFE8", "tint": "#FDF2F8", "border": "#FBCFE8",
    },
    {
        "title": "Interventions and clinical",
        "text": "Guidelines, parental mediation and programs",
        "question": "What interventions reduce screen time in children?",
        "svg": "interventions.svg", "emoji": "🩺", "color": "#BFDBFE", "tint": "#EFF6FF", "border": "#BFDBFE",
    },
]
