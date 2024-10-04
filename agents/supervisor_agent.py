import os
import openai
import logging
from dotenv import load_dotenv

# Configura il logging
logging.basicConfig(level=logging.INFO)

def supervisor_process(aru_revised, ufp_results):
    # Carica il prompt per il supervisore
    with open('prompts/supervisor_prompt.txt', 'r', encoding='utf-8') as file:
        supervisor_prompt = file.read()
    
    # Sostituisci i placeholder con i dati finali
    prompt = supervisor_prompt.replace("[ARU_APPROVATA]", aru_revised)
    prompt = prompt.replace("[UFP_RESULTS]", ufp_results)
    
    # Carica le variabili d'ambiente dal file .env
    load_dotenv()
    
    # Configura le credenziali di Azure OpenAI
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')  # Endpoint Azure OpenAI
    openai.api_version = os.getenv('OPENAI_API_VERSION')  # Versione API
    openai.api_key = os.getenv('OPENAI_API_KEY')  # Chiave API

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
        supervision_report = completion['choices'][0]['message']['content']
        
        logging.info("Rapporto del supervisore generato.")
        return supervision_report

    except Exception as e:
        logging.error(f"Errore nel supervisore: {e}")
        return f"Errore nel supervisore: {e}"
