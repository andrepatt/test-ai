import os
import openai
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

def supervise_process(restructured_aru, ufp_results, total_ufp):
    # Load the prompt from the file
    with open('prompts/supervisor_prompt.txt', 'r', encoding='utf-8') as file:
        supervisor_prompt = file.read()
    
    # Replace placeholders with available data
    prompt = supervisor_prompt.replace("[ARU_RISTRUTTURATO]", restructured_aru)
    prompt = prompt.replace("[RISULTATI_UFP]", ufp_results)
    prompt = prompt.replace("[TOTALE_UFP]", str(total_ufp) if total_ufp else "Non disponibile")
    
    # Configure Azure OpenAI credentials
    openai.api_type = "azure"
    openai.api_base = os.getenv('OPENAI_API_BASE')  # Azure OpenAI endpoint
    openai.api_version = os.getenv('OPENAI_API_VERSION')  # API version
    openai.api_key = os.getenv('OPENAI_API_KEY')  # API key

    # Use the ChatCompletion API with deployment_id for Azure
    response = ""
    completion = openai.ChatCompletion.create(
        deployment_id=os.getenv('DEPLOYMENT_NAME'),
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    # Process the streaming response chunks
    for chunk in completion:
        chunk_text = chunk['choices'][0]['delta'].get('content', '')
        response += chunk_text
        yield chunk_text  # Yield the chunk for streaming

    logging.info("Supervisor has completed the verification.")
    return response
