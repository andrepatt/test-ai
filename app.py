import streamlit as st
from aru_manager import handle_uploaded_file
from fp_calculator import calculate_function_points
from output_generator import create_docx_from_markdown, create_pdf_from_markdown
from logger import configure_logging, log_message
from agents.supervisor_agent import supervise_process
import time

# Configura il logging
configure_logging()

# Definisci gli step e la loro descrizione
steps = {
    "Caricamento ARU": "Carica il tuo documento ARU",
    "Revisione ARU": "Rivedi l'ARU",
    "Calcolo FP": "Calcola i Function Points",
    "Rapporto Supervisore": "Visualizza il Rapporto del Supervisore",
}

def main():
    st.set_page_config(page_title="Calcolo Function Point", layout="wide")
    st.title("Calcolo dei Function Point da ARU")

    # Step attuale e layout radio button in orizzontale
    current_step = st.radio("Scegli uno step", list(steps.keys()), horizontal=True)

    # Mostra il titolo dello step corrente
    st.subheader(steps[current_step])

    # Step 1: Caricamento ARU
    if current_step == "Caricamento ARU":
        st.header("1. Carica il tuo documento ARU")
        uploaded_file = st.file_uploader("Scegli un file", type=["pdf", "doc", "docx", "txt"])
        if uploaded_file is not None:
            # Spinner durante l'upload e la lettura del file
            with st.spinner("Caricamento in corso..."):
                aru_content = handle_uploaded_file(uploaded_file)
                st.session_state['aru_content'] = aru_content
                time.sleep(1)  # Simula un'attesa

            st.success("Documento caricato con successo!")
            log_message("Documento ARU caricato")

            # Visualizza il contenuto dell'ARU in un box apribile/chiudibile
            with st.expander("Visualizza ARU originale"):
                st.text_area("Contenuto ARU:", st.session_state['aru_content'], height=300)

    # Step 2: Revisione ARU
    elif current_step == "Revisione ARU":
        if 'aru_content' in st.session_state:
            st.header("2. Revisione dell'ARU")
            if st.button("Esegui Revisione"):
                # Spinner durante l'operazione
                with st.spinner("Revisione ARU in corso..."):
                    aru_text, total_ufp = calculate_function_points(st.session_state['aru_content'])
                    st.session_state['aru_ristrutturato'] = aru_text
                    st.session_state['total_ufp'] = total_ufp
                    time.sleep(1)

                log_message("Revisione ARU completata")
                st.success("Revisione completata!")

            # Mostra l'ARU revisionato in un box apribile/chiudibile
            if st.session_state.get('aru_ristrutturato'):
                with st.expander("Visualizza ARU Revisionato"):
                    st.markdown(st.session_state['aru_ristrutturato'], unsafe_allow_html=True)

                # Aggiungi pulsanti di download DOCX e PDF
                docx_buffer = create_docx_from_markdown(st.session_state['aru_ristrutturato'])
                st.download_button(
                    label="Scarica ARU Revisionato in formato DOCX",
                    data=docx_buffer,
                    file_name="ARU_revisionato.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

                pdf_buffer = create_pdf_from_markdown(st.session_state['aru_ristrutturato'])
                st.download_button(
                    label="Scarica ARU Revisionato in formato PDF",
                    data=pdf_buffer,
                    file_name="ARU_revisionato.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Prima di procedere, carica un documento ARU.")

    # Step 3: Calcolo FP
    elif current_step == "Calcolo FP":
        if 'aru_ristrutturato' in st.session_state:
            st.header("3. Calcolo degli Unadjusted Function Points (UFP)")
            if st.button("Calcola UFP"):
                # Spinner durante il calcolo
                with st.spinner("Calcolo UFP in corso..."):
                    ufp_text, total_ufp = calculate_function_points(st.session_state['aru_ristrutturato'])
                    st.session_state['ufp_results'] = ufp_text
                    st.session_state['total_ufp'] = total_ufp
                    time.sleep(1)

                log_message("Calcolo UFP completato")
                st.success("Calcolo UFP completato!")

            # Mostra i risultati UFP in un box apribile/chiudibile
            if st.session_state.get('ufp_results'):
                with st.expander("Visualizza Risultati del Calcolo UFP"):
                    st.markdown(st.session_state['ufp_results'], unsafe_allow_html=True)
                st.success(f"**Totale UFP:** {st.session_state['total_ufp']}")
        else:
            st.warning("Prima di procedere, esegui la revisione dell'ARU.")

    # Step 4: Rapporto Supervisore
    elif current_step == "Rapporto Supervisore":
        if 'ufp_results' in st.session_state:
            st.header("4. Rapporto del Supervisore")
            if st.button("Genera Rapporto"):
                # Spinner durante la generazione del rapporto
                with st.spinner("Generazione del rapporto in corso..."):
                    # Chiamata all'agente supervisore
                    supervisor_generator = supervise_process(
                        st.session_state['aru_ristrutturato'],
                        st.session_state['ufp_results'],
                        st.session_state['total_ufp']
                    )
                    st.session_state['supervision_report'] = ''.join([chunk for chunk in supervisor_generator])
                    log_message("Rapporto del Supervisore generato")
                    time.sleep(1)

            if st.session_state.get('supervision_report'):
                st.markdown(st.session_state['supervision_report'], unsafe_allow_html=True)

                # Aggiungi pulsanti di download del rapporto
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

if __name__ == "__main__":
    main()
