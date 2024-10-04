import os
import openai
import logging
from dotenv import load_dotenv
import json
import re

# Configura il logging
logging.basicConfig(level=logging.INFO)

def agent2_verify(aru_revised):
    # Carica il prompt dal file
    with open('prompts/agent2_prompt.txt', 'r', encoding='utf-8') as file:
        agent2_prompt = file.read()

    prompt = agent2_prompt.replace("[ARU_REVISIONATA]", aru_revised)
    load_dotenv()
    
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')
    openai.api_version = os.getenv('OPENAI_API_VERSION')
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    deployment_name = os.getenv('DEPLOYMENT_NAME')
    
    if not all([openai.api_base, openai.api_version, openai.api_key, deployment_name]):
        logging.error("Configurazione OpenAI incompleta.")
        return "NON APPROVATO", "Errore nella configurazione OpenAI", ""
    
    conversation = [{"role": "user", "content": prompt}]
    
    try:
        completion = openai.ChatCompletion.create(
            deployment_id=deployment_name,
            messages=conversation,
            temperature=0.0,
            max_tokens=None,
            stream=False
        )
        
        feedback = completion['choices'][0]['message']['content']
        agent2_log = feedback

        # Estrai il JSON utilizzando una regex
        json_match = re.search(r'\{.*\}', feedback, re.DOTALL)
        if json_match:
            feedback_json = json_match.group(0)
        else:
            logging.error(f"Errore nel parsing del feedback JSON dell'agente 2. Feedback raw: {feedback}")
            return "NON APPROVATO", "Feedback JSON non valido", agent2_log

        # Ora prova a convertire il testo JSON in un dizionario
        try:
            result = json.loads(feedback_json)
            stato = result.get('stato', '').upper()
            feedback_text = result.get('feedback', '')
            return stato, feedback_text, agent2_log

        except json.JSONDecodeError:
            logging.error(f"Errore nel parsing del feedback JSON dell'agente 2. Feedback raw: {feedback_json}")
            return "NON APPROVATO", "Feedback JSON non valido", agent2_log

    except openai.error.OpenAIError as e:
        logging.error(f"Errore OpenAI nell'agente 2: {e}")
        return "NON APPROVATO", f"Errore OpenAI: {str(e)}", ""
    except Exception as e:
        logging.error(f"Errore generico nell'agente 2: {e}")
        return "NON APPROVATO", f"Errore generico: {str(e)}", ""