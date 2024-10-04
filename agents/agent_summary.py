import os
import openai
import logging
from dotenv import load_dotenv

# Configura il logging
logging.basicConfig(level=logging.INFO)

def agent_summary(aru_revised):
    # Carica il prompt per l'agente di sintesi
    with open('prompts/agent_summary_prompt.txt', 'r', encoding='utf-8') as file:
        summary_prompt = file.read()
    
    # Sostituisci il placeholder con l'ARU revisionata
    prompt = summary_prompt.replace("[ARU_REVISIONATA]", aru_revised)
    
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
        summary = completion['choices'][0]['message']['content']
        
        logging.info("Sintesi dell'ARU completata.")
        return summary

    except Exception as e:
        logging.error(f"Errore nell'agente di sintesi: {e}")
        return f"Errore nell'agente di sintesi: {e}"
