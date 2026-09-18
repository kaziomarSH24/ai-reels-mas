import sys
sys.path.append('python_engine')
from app.services.ai_service import ai_agent

texts = [
    "I was walking down the street yesterday.",
    "He brought a 90-lb asthmatic onto my army base.",
    "It's raining cats and dogs outside."
]
res = ai_agent.batch_analyze_dialogues(texts)
for r in res:
    print(r['cefr_level'], "|", r['target_word'])
