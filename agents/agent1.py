import os
import openai
import logging
from dotenv import load_dotenv
import json
from agents.agent2 import agent2_verify

# Configura il logging
logging.basicConfig(level=logging.INFO)

def agent1_process(aru_content):
    with open('prompts/agent1_prompt.txt', 'r', encoding='utf-8') as file:
        agent1_prompt_template = file.read()

    agent1_prompt = agent1_prompt_template.replace("[ARU_ORIGINALE]", aru_content)
    load_dotenv()
    
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')
    openai.api_version = os.getenv('OPENAI_API_VERSION')
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    deployment_name = os.getenv('DEPLOYMENT_NAME')
    
    agent1_logs = ""
    agent2_logs = ""
    
    max_iterations = 3
    iteration = 0
    approved = False
    aru_revisionata = ""

    try:
        while not approved and iteration < max_iterations:
            iteration += 1

            completion = openai.ChatCompletion.create(
                deployment_id=deployment_name,
                messages=[{"role": "user", "content": agent1_prompt}],
                temperature=0.0,
                max_tokens=None,
                stream=True
            )

            aru_revisionata = ""
            for chunk in completion:
                if 'choices' in chunk:
                    aru_revisionata += chunk['choices'][0].get('delta', {}).get('content', '')

            agent1_logs += f"**Iterazione {iteration} - Agente 1 ha prodotto una nuova versione dell'ARU.**\n{aru_revisionata}\n\n"

            stato, feedback, agent2_log = agent2_verify(aru_revisionata)
            agent2_logs += f"**Iterazione {iteration} - Feedback dell'Agente 2:**\n{agent2_log}\n\n"

            if stato == "APPROVATO" or (stato == "PARZIALMENTE APPROVATO" and iteration > 1):
                approved = True
            else:
                try:
                    feedback_json = json.loads(feedback)
                    feedback_text = feedback_json.get('feedback', 'Il feedback non è disponibile')
                except json.JSONDecodeError:
                    logging.error(f"Errore nel parsing del feedback JSON dell'agente 2. Feedback raw: {feedback}")
                    feedback_text = "Il feedback dell'agente 2 non è stato processato correttamente."

                agent1_prompt = f"Applica il seguente feedback all'ARU e correggi gli errori:\n{feedback_text}\n\nARU da aggiornare:\n{aru_revisionata}"

        if not approved:
            agent1_logs += "Numero massimo di iterazioni raggiunto senza approvazione.\n"

        return aru_revisionata, agent1_logs, agent2_logs, approved

    except Exception as e:
        logging.error(f"Errore nell'agente 1: {e}")
        return f"Errore nell'agente 1: {e}", "", "", False


