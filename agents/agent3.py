import os
import openai
import logging
from dotenv import load_dotenv

from agents.agent4 import agent4_verify

# Configura il logging
logging.basicConfig(level=logging.INFO)

def agent3_process(aru_revised):
    # Carica il prompt dal file
    with open('prompts/agent3_prompt.txt', 'r', encoding='utf-8') as file:
        agent3_prompt_template = file.read()
    
    # Sostituisci il placeholder con l'ARU approvata
    agent3_prompt = agent3_prompt_template.replace("[ARU_APPROVATA]", aru_revised)
    
    # Carica le variabili d'ambiente dal file .env
    load_dotenv()
    
    # Configura le credenziali di OpenAI
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')
    openai.api_version = os.getenv('OPENAI_API_VERSION')
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # Nome del deployment (modello) da utilizzare
    deployment_name = os.getenv('DEPLOYMENT_NAME')
    
    # Inizializza i log delle interazioni
    agent3_logs = ""
    agent4_logs = ""
    
    # Variabili per il loop di feedback
    max_iterations = 3
    iteration = 0
    approved = False
    
    try:
        while not approved and iteration < max_iterations:
            iteration += 1

            # Chiamata all'API per l'Agente 3
            completion = openai.ChatCompletion.create(
                deployment_id=deployment_name,
                messages=[{"role": "user", "content": agent3_prompt}],
                temperature=0.0,
                stream=False
            )
            
            # Estrai il contenuto della risposta
            ufp_results = completion['choices'][0]['message']['content']
            agent3_logs += f"**Iterazione {iteration} - Agente 3 ha prodotto un calcolo UFP.**\n{ufp_results}\n\n"

            logging.info(f"Agente 3 ha completato il calcolo UFP all'iterazione {iteration}.")

            # Chiamata all'Agente 4 per la verifica
            feedback, agent4_log = agent4_verify(ufp_results)
            agent4_logs += f"**Iterazione {iteration} - Feedback dell'Agente 4:**\n{agent4_log}\n\n"

            if "APPROVATO" in feedback.upper():
                approved = True
                logging.info("Agente 4 ha approvato il calcolo UFP.")
            else:
                # L'Agente 3 applica il feedback
                agent3_prompt = f"Applica il seguente feedback al calcolo UFP e correggi gli errori:\n{feedback}\n\nCalcolo UFP da aggiornare:\n{ufp_results}"
                logging.info(f"Agente 4 ha richiesto modifiche al calcolo UFP all'iterazione {iteration}.")

        if not approved:
            agent3_logs += "Numero massimo di iterazioni raggiunto senza approvazione.\n"
            logging.warning("Numero massimo di iterazioni raggiunto senza approvazione.")

        return ufp_results, agent3_logs, agent4_logs

    except Exception as e:
        logging.error(f"Errore nell'agente 3: {e}")
        return f"Errore nell'agente 3: {e}", "", ""