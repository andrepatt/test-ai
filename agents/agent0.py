import os
import openai
import logging
from dotenv import load_dotenv

# Configura il logging
logging.basicConfig(level=logging.INFO)

def agent0_validate(aru_content):
    # Carica il prompt dal file
    with open('prompts/agent0_prompt.txt', 'r', encoding='utf-8') as file:
        agent0_prompt = file.read()
    
    # Sostituisci il placeholder con il contenuto dell'ARU
    prompt = agent0_prompt.replace("[ARU_ORIGINALE]", aru_content)
    
    # Carica le variabili d'ambiente dal file .env
    load_dotenv()
    
    # Configura le credenziali di Azure OpenAI
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')  # Azure OpenAI endpoint
    openai.api_version = os.getenv('OPENAI_API_VERSION')  # API version
    openai.api_key = os.getenv('OPENAI_API_KEY')  # API key

    # Nome del deployment (modello) da utilizzare
    deployment_name = os.getenv('DEPLOYMENT_NAME')
    
    # Inizializza la conversazione
    conversation = [{"role": "user", "content": prompt}]
    
    # Utilizza il metodo ChatCompletion della nuova API
    try:
        completion = openai.ChatCompletion.create(
            deployment_id=deployment_name,
            messages=conversation,
            temperature=0.5,
            stream=False
        )
        
        # Estrai il contenuto della risposta
        feedback = completion['choices'][0]['message']['content']
        
        # Determina se l'ARU è valida
        if "ARU VALIDA" in feedback.upper():
            valid = True
        else:
            valid = False
        
        return valid, feedback

    except Exception as e:
        logging.error(f"Errore nell'agente 0: {e}")
        return False, f"Errore nell'agente 0: {e}"
