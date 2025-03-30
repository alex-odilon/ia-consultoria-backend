from app.ai_gpt import ask_gpt

def process_question(pergunta: str) -> dict:
    return ask_gpt(pergunta)
