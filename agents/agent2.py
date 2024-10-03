import os
import openai
from dotenv import load_dotenv
import logging

# Carica le variabili d'ambiente
load_dotenv()

def calculate_ufp(restructured_aru):
    # Carica il prompt dal file
    with open('prompts/agent2_prompt.txt', 'r', encoding='utf-8') as file:
        agent2_prompt = file.read()
    
    # Sostituisci il placeholder con l'ARU ristrutturato
    prompt = agent2_prompt.replace("[ARU_RISTRUTTURATO]", restructured_aru)
    
    # Configura le credenziali di Azure OpenAI
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')  # Azure OpenAI endpoint
    openai.api_version = os.getenv('OPENAI_API_VERSION')  # API version
    openai.api_key = os.getenv('OPENAI_API_KEY')  # API key

    # Utilizza il metodo ChatCompletion della nuova API con deployment_id
    response = ""
    completion = openai.ChatCompletion.create(
        deployment_id=os.getenv('DEPLOYMENT_NAME'),  # Usa deployment_id per Azure OpenAI
        messages=[{"role": "user", "content": prompt}],
        stream=True  # Stream the response
    )

    # Processa i chunk della risposta in streaming
    for chunk in completion:
        # Estrarre il testo dal campo 'delta'
        chunk_text = chunk['choices'][0]['delta'].get('content', '')
        response += chunk_text
        yield chunk_text  # Genera il chunk per lo streaming

    logging.info("Agente 2 ha completato il calcolo UFP.")
    return response
