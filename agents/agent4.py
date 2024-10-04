import os
import openai
import logging
from dotenv import load_dotenv

# Configura il logging
logging.basicConfig(level=logging.INFO)

def agent4_verify(ufp_results):
    # Carica il prompt dal file
    with open('prompts/agent4_prompt.txt', 'r', encoding='utf-8') as file:
        agent4_prompt = file.read()
    
    # Sostituisci il placeholder con i risultati UFP
    prompt = agent4_prompt.replace("[UFP_RESULTS]", ufp_results)
    
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
            temperature=0.0,
            stream=False
        )
        
        # Estrai il contenuto della risposta
        feedback = completion['choices'][0]['message']['content']

        # Prepara i log
        agent4_log = feedback

        return feedback, agent4_log

    except Exception as e:
        logging.error(f"Errore nell'agente 4: {e}")
        return f"Errore nell'agente 4: {e}", ""
