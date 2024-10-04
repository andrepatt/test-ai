import streamlit as st
from agents.agent0 import agent0_validate
from agents.agent1 import agent1_process
from agents.agent3 import agent3_process
from agents.agent_summary import agent_summary
from agents.supervisor_agent import supervisor_process
from aru_manager import handle_uploaded_file
from output_generator import create_docx_from_markdown, create_pdf_from_markdown
from logger import configure_logging, log_message
import time
import json

# Configura il logging
configure_logging()

# Definizione delle costanti
MAIN_STEPS = ["Caricamento ARU", "Validazione ARU", "Revisione ARU", "Calcolo FP", "Rapporto Supervisore"]
ALL_STEPS = MAIN_STEPS + ["Interazioni Agenti"]

def update_progress():
    progress = max(0, len(st.session_state['completed_steps']) / len(MAIN_STEPS))
    st.session_state['progress_bar'].progress(progress)

def initialize_session_state():
    if 'current_step' not in st.session_state:
        st.session_state['current_step'] = ALL_STEPS[0]
    if 'completed_steps' not in st.session_state:
        st.session_state['completed_steps'] = []
    if 'aru_content' not in st.session_state:
        st.session_state['aru_content'] = None
    if 'aru_valid' not in st.session_state:
        st.session_state['aru_valid'] = False
    if 'aru_revised' not in st.session_state:
        st.session_state['aru_revised'] = None
    if 'aru_approved' not in st.session_state:
        st.session_state['aru_approved'] = False
    if 'progress_bar' not in st.session_state:
        st.session_state['progress_bar'] = st.progress(0.0)

def main():
    st.set_page_config(page_title="Calcolo Function Point", layout="wide")
    st.title("Calcolo dei Function Point da ARU")

    initialize_session_state()

    # Disegna la sidebar con la navigazione degli step
    with st.sidebar:
        st.header("Navigazione")
        for i, step in enumerate(ALL_STEPS):
            # Verifica se il passo corrente è stato completato
            is_previous_completed = (i == 0 or ALL_STEPS[i - 1] in st.session_state['completed_steps'])
            is_current = step == st.session_state['current_step']
            
            # Definisce lo stile in base allo stato
            button_style = "font-weight: bold; background-color: #0056b3; color: white;" if is_current else \
                           "color: black;"

            # Controllo per mostrare il warning se il passo precedente non è completato
            if st.button(step, key=step, use_container_width=True):
                if is_previous_completed or step == "Interazioni Agenti":
                    st.session_state['current_step'] = step
                else:
                    st.warning(f"Completare lo step precedente: {ALL_STEPS[i - 1]}")
                    
            st.markdown(f"<style>.stButton button#{step} {{ {button_style} }}</style>", unsafe_allow_html=True)

    # Aggiornamento della barra di avanzamento
    update_progress()

    # Gestione dei diversi step
    if st.session_state['current_step'] == "Caricamento ARU":
        handle_caricamento_aru()
    elif st.session_state['current_step'] == "Validazione ARU":
        handle_validazione_aru()
    elif st.session_state['current_step'] == "Revisione ARU":
        handle_revisione_aru()
    elif st.session_state['current_step'] == "Calcolo FP":
        handle_calcolo_fp()
    elif st.session_state['current_step'] == "Rapporto Supervisore":
        handle_rapporto_supervisore()
    elif st.session_state['current_step'] == "Interazioni Agenti":
        handle_interazioni_agenti()

    # Aggiornamento finale della barra di avanzamento
    update_progress()

def handle_caricamento_aru():
    st.header("1. Carica il tuo documento ARU")
    uploaded_file = st.file_uploader("Scegli un file", type=["pdf", "doc", "docx", "txt"])
    if uploaded_file:
        with st.spinner("Caricamento in corso..."):
            aru_content = handle_uploaded_file(uploaded_file)
            st.session_state['aru_content'] = aru_content
            st.session_state['uploaded_file'] = uploaded_file.name
            time.sleep(1)
        st.success("Documento caricato con successo!")
        log_message("Documento ARU caricato")
        with st.expander("Visualizza ARU originale"):
            st.markdown(st.session_state['aru_content'], unsafe_allow_html=True)
        if "Caricamento ARU" not in st.session_state['completed_steps']:
            st.session_state['completed_steps'].append("Caricamento ARU")
        update_progress()

def handle_validazione_aru():
    if st.session_state.get('aru_content'):
        st.header("2. Validazione dell'ARU")
        if st.button("Esegui Validazione"):
            with st.spinner("Validazione in corso..."):
                valid, feedback = agent0_validate(st.session_state['aru_content'])
                st.session_state['aru_valid'] = valid
                st.session_state['agent0_feedback'] = feedback
                time.sleep(1)
            if valid:
                st.success("ARU valida! Puoi procedere al prossimo step.")
            else:
                st.warning("L'ARU potrebbe essere migliorata. Feedback informativo:")
                st.markdown(feedback, unsafe_allow_html=True)
            if "Validazione ARU" not in st.session_state['completed_steps']:
                st.session_state['completed_steps'].append("Validazione ARU")
            update_progress()
    else:
        st.warning("Prima di procedere, carica un documento ARU.")

def handle_revisione_aru():
    if st.session_state.get('aru_content'):
        st.header("3. Revisione dell'ARU")
        if st.button("Esegui Revisione"):
            with st.spinner("Revisione in corso..."):
                # Converti l'output del generatore in una lista
                results = list(agent1_process(st.session_state['aru_content']))
                aru_revised, agent1_logs, agent2_logs, approved = results
                st.session_state['aru_revised'] = aru_revised
                st.session_state['aru_approved'] = approved
                st.session_state['agent1_logs'] = agent1_logs
                st.session_state['agent2_logs'] = agent2_logs
                time.sleep(1)

            if approved:
                st.success("L'ARU è stata approvata.")
            else:
                st.warning("La revisione non è stata approvata. Consulta il feedback per ulteriori dettagli.")

            if "Revisione ARU" not in st.session_state['completed_steps']:
                st.session_state['completed_steps'].append("Revisione ARU")
            update_progress()

        if st.session_state.get('aru_revised'):
            with st.expander("Visualizza ARU Revisionata"):
                st.markdown(st.session_state['aru_revised'], unsafe_allow_html=True)
            docx_buffer = create_docx_from_markdown(st.session_state['aru_revised'])
            st.download_button(
                label="Scarica ARU Revisionata in formato DOCX",
                data=docx_buffer,
                file_name="ARU_revisionata.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            pdf_buffer = create_pdf_from_markdown(st.session_state['aru_revised'])
            st.download_button(
                label="Scarica ARU Revisionata in formato PDF",
                data=pdf_buffer,
                file_name="ARU_revisionata.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Prima di procedere, carica un documento ARU.")



def handle_calcolo_fp():
    if st.session_state.get('aru_revised') and st.session_state.get('aru_approved', False):
        st.header("4. Calcolo degli Unadjusted Function Points (UFP)")
        if st.button("Calcola UFP"):
            with st.spinner("Calcolo UFP in corso..."):
                ufp_results, agent3_logs, agent4_logs = agent3_process(st.session_state['aru_revised'])
                st.session_state['ufp_results'] = ufp_results
                st.session_state['agent3_logs'] = agent3_logs
                st.session_state['agent4_logs'] = agent4_logs
                time.sleep(1)

            log_message("Calcolo UFP completato")
            total_ufp = extract_total_ufp(ufp_results)
            st.session_state['total_ufp'] = total_ufp
            st.success(f"Calcolo UFP completato! Totale UFP: {total_ufp}")

            if "Calcolo FP" not in st.session_state['completed_steps']:
                st.session_state['completed_steps'].append("Calcolo FP")
            update_progress()

        if st.session_state.get('ufp_results'):
            with st.expander("Visualizza Risultati del Calcolo UFP"):
                st.markdown(st.session_state['ufp_results'], unsafe_allow_html=True)
    else:
        st.warning("Prima di procedere, esegui la revisione dell'ARU.")

def handle_rapporto_supervisore():
    if st.session_state.get('ufp_results'):
        st.header("5. Rapporto del Supervisore")
        if st.button("Genera Rapporto"):
            with st.spinner("Generazione del rapporto in corso..."):
                supervision_report = supervisor_process(
                    st.session_state['aru_revised'],
                    st.session_state['ufp_results']
                )
                st.session_state['supervision_report'] = supervision_report
                log_message("Rapporto del Supervisore generato")
                time.sleep(1)

            st.success("Rapporto del Supervisore generato con successo!")
            summary = agent_summary(st.session_state['aru_revised'])
            st.session_state['summary'] = summary

            if "Rapporto Supervisore" not in st.session_state['completed_steps']:
                st.session_state['completed_steps'].append("Rapporto Supervisore")
            update_progress()

        if st.session_state.get('supervision_report'):
            with st.expander("Visualizza Sommario"):
                st.markdown(st.session_state['summary'], unsafe_allow_html=True)
            with st.expander("Visualizza Rapporto del Supervisore"):
                st.markdown(st.session_state['supervision_report'], unsafe_allow_html=True)
            report_docx_buffer = create_docx_from_markdown(st.session_state['supervision_report'])
            st.download_button(
                label="Scarica Rapporto del Supervisore in formato DOCX",
                data=report_docx_buffer,
                file_name="Rapporto_Supervisore.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            report_pdf_buffer = create_pdf_from_markdown(st.session_state['supervision_report'])
            st.download_button(
                label="Scarica Rapporto del Supervisore in formato PDF",
                data=report_pdf_buffer,
                file_name="Rapporto_Supervisore.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Prima di procedere, calcola i Function Points.")

def handle_interazioni_agenti():
    st.header("Interazioni tra gli Agenti")
    if 'agent0_feedback' in st.session_state:
        st.subheader("Agente 0: Validazione ARU")
        with st.expander("Feedback dell'Agente 0"):
            st.markdown(st.session_state['agent0_feedback'], unsafe_allow_html=True)

    if 'agent1_logs' in st.session_state and 'agent2_logs' in st.session_state:
        st.subheader("Interazioni tra Agente 1 e Agente 2")
        with st.expander("Conversazioni"):
            st.markdown("**Agente 1 e Agente 2:**")
            st.markdown(st.session_state['agent1_logs'], unsafe_allow_html=True)
            st.markdown(st.session_state['agent2_logs'], unsafe_allow_html=True)

    if 'agent3_logs' in st.session_state and 'agent4_logs' in st.session_state:
        st.subheader("Interazioni tra Agente 3 e Agente 4")
        with st.expander("Conversazioni"):
            st.markdown("**Agente 3 e Agente 4:**")
            st.markdown(st.session_state['agent3_logs'], unsafe_allow_html=True)
            st.markdown(st.session_state['agent4_logs'], unsafe_allow_html=True)

def extract_total_ufp(ufp_results):
    try:
        data = json.loads(ufp_results)
        total_ufp = data.get('totale_UFP', 'Non disponibile')
        return total_ufp
    except json.JSONDecodeError:
        return "Non disponibile"

if __name__ == "__main__":
    main()
