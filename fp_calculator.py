import re
from agents.agent2 import calculate_ufp

def calculate_function_points(aru_ristrutturato):
    """Calcola i Function Points e restituisce i risultati in formato testuale e numerico."""
    ufp_text = ''.join([chunk for chunk in calculate_ufp(aru_ristrutturato)])

    # Estrai il totale UFP
    total_ufp_match = re.search(r"Totale UFP:\s*(\d+)", ufp_text)
    if total_ufp_match:
        total_ufp = int(total_ufp_match.group(1))
    else:
        total_ufp = None

    return ufp_text, total_ufp
