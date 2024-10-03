import os
import openai
from dotenv import load_dotenv
import logging

# Carica le variabili d'ambiente
load_dotenv()

def restructure_aru(aru_content):
    # Carica il prompt dal file
    with open('prompts/agent1_prompt.txt', 'r', encoding='utf-8') as file:
        agent1_prompt = file.read()
    
    # Sostituisci il placeholder con il contenuto dell'ARU
    prompt = agent1_prompt.replace("[ARU_ORIGINALE]", aru_content)
    
    # Configura le credenziali di Azure OpenAI
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')  # Azure OpenAI endpoint
    openai.api_version = os.getenv('OPENAI_API_VERSION')  # API version
    openai.api_key = os.getenv('OPENAI_API_KEY')  # API key

    # Utilizza il metodo ChatCompletion della nuova API
    response = ""
    completion = openai.ChatCompletion.create(
        deployment_id=os.getenv('DEPLOYMENT_NAME'),
        messages=[{"role": "user", "content": prompt}],
        stream=True  # Stream the response
    )
    
    for chunk in completion:
        chunk_text = chunk['choices'][0]['delta'].get('content', '')
        response += chunk_text
        yield chunk_text  # Genera il chunk per lo streaming

    logging.info("Agente 1 ha completato la ristrutturazione.")
    return response
