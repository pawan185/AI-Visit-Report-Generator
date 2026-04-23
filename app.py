import streamlit as st
from generate_ai import generate_scope_and_questions, generate_visit_report, generate_client_proposal
from export_utils import create_word_document
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Visit Report Generator", layout="centered")

api_key_input = os.environ.get("GEMINI_API_KEY", "")

def init_session_state():
    if "phase" not in st.session_state:
        st.session_state.phase = 1
    if "company_details" not in st.session_state:
        st.session_state.company_details = {}
    if "visit_purpose" not in st.session_state:
        st.session_state.visit_purpose = ""
    if "scope_and_questions" not in st.session_state:
        st.session_state.scope_and_questions = ""
    if "observations" not in st.session_state:
        st.session_state.observations = {}
    if "visit_report" not in st.session_state:
        st.session_state.visit_report = ""
    if "client_proposal" not in st.session_state:
        st.session_state.client_proposal = ""
    if "other_observations" not in st.session_state:
        st.session_state.other_observations = ""

def next_phase():
    st.session_state.phase += 1

def prev_phase():
    st.session_state.phase -= 1

init_session_state()

st.title("AI Visit Report Generator")

# Progress Tracker (now 6 phases)
st.progress((st.session_state.phase - 1) / 5)

phase_titles = [
    "Input Company Details",
    "Scope & Discovery Questions",
    "Field Observations",
    "Visit Report",
    "Client Proposal",
    "Export Final Package"
]
st.subheader(f"Phase {st.session_state.phase}: {phase_titles[st.session_state.phase - 1]}")

# ----------------- PHASE 1 -----------------
if st.session_state.phase == 1:
    with st.form("company_details_form"):
        company_name = st.text_input("Company Name", value=st.session_state.company_details.get("company_name", ""))
        industry = st.text_input("Industry / Type of Company", value=st.session_state.company_details.get("industry", ""))
        visit_date = st.date_input("Visit Date")
        primary_contact = st.text_input("Primary Contact")

        st.markdown("---")
        st.markdown("#### 🎯 Purpose of Visit")
        visit_purpose = st.text_area(
            "What is the main goal or purpose of this visit?",
            value=st.session_state.visit_purpose,
            placeholder="e.g. Understand their current HR software pain points and assess potential for our HRMS solution.",
            height=120,
            help="Be specific — the AI will use this to generate targeted, relevant discovery questions instead of generic ones."
        )
        
        submitted = st.form_submit_button("Next: Generate Scope & Questions")
        if submitted:
            if company_name and industry:
                if not visit_purpose.strip():
                    st.error("Please describe the purpose or main goal of this visit.")
                else:
                    st.session_state.company_details = {
                        "company_name": company_name,
                        "industry": industry,
                        "visit_date": str(visit_date),
                        "primary_contact": primary_contact
                    }
                    st.session_state.visit_purpose = visit_purpose.strip()
                    next_phase()
                    st.rerun()
            else:
                st.error("Please fill in at least the Company Name and Industry.")

# ----------------- PHASE 2 -----------------
elif st.session_state.phase == 2:
    if not api_key_input:
        st.warning("Please enter your Gemini API Key in the sidebar or .env file to proceed.")
        if st.button("Back"):
             prev_phase()
             st.rerun()
    else:
        st.info("Using AI to generate the Scope Document and targeted Discovery Questions...")
        
        if not st.session_state.scope_and_questions:
            with st.spinner("Generating document..."):
                try:
                    st.session_state.scope_and_questions = generate_scope_and_questions(
                        api_key_input,
                        st.session_state.company_details,
                        st.session_state.visit_purpose
                    )
                    st.success("Scope & Questions generated successfully!")
                except Exception as e:
                    st.error(f"Error communicating with AI service: {e}")
                
        if st.session_state.scope_and_questions:
            st.markdown("### Generated Document")
            st.markdown(st.session_state.scope_and_questions)
            
            # Distributed Download Button for just the Scope & Questions
            company = st.session_state.company_details.get("company_name", "Company")
            docx_stream = create_word_document(st.session_state.scope_and_questions)
            st.download_button(
                label="Download Scope Document & Questions (.docx)",
                data=docx_stream,
                file_name=f"{company}_Scope_and_Questions.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back"):
                st.session_state.scope_and_questions = "" # Reset if going back
                prev_phase()
                st.rerun()
        with col2:
            if st.session_state.scope_and_questions:
                if st.button("Next: Record Field Observations"):
                    next_phase()
                    st.rerun()

# ----------------- PHASE 3 -----------------
elif st.session_state.phase == 3:
    st.write("Provide your raw field notes and answers to the generated questions based on the client visit.")
    
    # Parse questions from the generated AI response text
    questions = []
    if st.session_state.scope_and_questions:
        import re
        lines = st.session_state.scope_and_questions.split('\n')
        for line in lines:
            line = line.strip()
            # Simple heuristic: extract lines ending with a question mark
            if line.endswith('?') and len(line) > 10:
                cleaned = re.sub(r'^[\d\.\-\*]+\s*', '', line)
                if cleaned not in questions:
                    questions.append(cleaned)
                    
    # Fallback single field if parser doesn't find any explicit questions
    if not questions:
        questions = ["Field Notes & Detailed Observations"]
    
    with st.form("observations_form"):
        # Dynamically render individual inputs for each extracted question
        for i, q in enumerate(questions):
            ans = st.text_area(f"**{q}**", 
                               value=st.session_state.observations.get(q, ""), 
                               key=f"obs_{i}")
            st.session_state.observations[q] = ans

        st.markdown("---")
        st.markdown("#### 📝 Other Observations")
        other_obs = st.text_area(
            "Any additional observations from the visit not covered by the questions above?",
            value=st.session_state.other_observations,
            placeholder="e.g. Noticed the office environment was disorganised, staff seemed undertrained, they mentioned an upcoming expansion plan...",
            height=150,
            key="other_obs_input",
            help="Use this space to capture anything you observed during the visit that didn't fit into a specific question."
        )
            
        submitted = st.form_submit_button("Next: Draft Visit Report")
        if submitted:
             st.session_state.other_observations = other_obs
             next_phase()
             st.rerun()
             
    if st.button("Back"):
        prev_phase()
        st.rerun()

# ----------------- PHASE 4 -----------------
elif st.session_state.phase == 4:
    if not api_key_input:
        st.warning("Please enter your Gemini API Key in the sidebar or .env file to proceed.")
        if st.button("Back"):
             prev_phase()
             st.rerun()
    else:
        st.info("Synthesizing your observations into a formal executive Visit Report...")
        
        if not st.session_state.visit_report:
            with st.spinner("Drafting report..."):
                try:
                    st.session_state.visit_report = generate_visit_report(
                        api_key_input,
                        st.session_state.company_details, 
                        st.session_state.observations,
                        st.session_state.other_observations
                    )
                except Exception as e:
                    st.error(f"Error communicating with AI service: {e}")
                
        if st.session_state.visit_report:
            st.text_area("Final Output Review (Review & Edit)", value=st.session_state.visit_report, height=350, key="edited_report")
            st.session_state.visit_report = st.session_state.edited_report # allow manual edits
            
            # Distributed Download Button for the Visit Report
            company = st.session_state.company_details.get("company_name", "Company")
            docx_stream = create_word_document(st.session_state.visit_report)
            st.download_button(
                label="Download Visit Report (.docx)",
                data=docx_stream,
                file_name=f"{company}_Visit_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back"):
                st.session_state.visit_report = ""
                prev_phase()
                st.rerun()
        with col2:
            if st.session_state.visit_report:
                if st.button("Next: Draft Client Proposal"):
                    next_phase()
                    st.rerun()

# ----------------- PHASE 5 -----------------
elif st.session_state.phase == 5:
    if not api_key_input:
        st.warning("Please enter your Gemini API Key to proceed.")
        if st.button("Back"):
             prev_phase()
             st.rerun()
    else:
        st.info("Drafting a formal Client Proposal based on the Scope Document and Visit Report...")
        
        if not st.session_state.client_proposal:
            with st.spinner("Drafting proposal..."):
                try:
                    st.session_state.client_proposal = generate_client_proposal(
                        api_key_input,
                        st.session_state.scope_and_questions,
                        st.session_state.visit_report
                    )
                except Exception as e:
                    st.error(f"Error communicating with AI service: {e}")
                
        if st.session_state.client_proposal:
            st.text_area("Client Proposal Review (Review & Edit)", value=st.session_state.client_proposal, height=350, key="edited_proposal")
            st.session_state.client_proposal = st.session_state.edited_proposal
            
            # Distributed Download Button for the Proposal
            company = st.session_state.company_details.get("company_name", "Company")
            docx_stream = create_word_document(st.session_state.client_proposal)
            st.download_button(
                label="Download Client Proposal (.docx)",
                data=docx_stream,
                file_name=f"{company}_Client_Proposal.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back"):
                st.session_state.client_proposal = ""
                prev_phase()
                st.rerun()
        with col2:
            if st.session_state.client_proposal:
                if st.button("Next: Export Integration"):
                    next_phase()
                    st.rerun()

# ----------------- PHASE 6 -----------------
elif st.session_state.phase == 6:
    st.success("Your Visit Report and Client Proposal are ready for download!")
    
    # Combine the report and proposal for export
    full_export_text = st.session_state.visit_report + "\n\n---\n\n" + st.session_state.client_proposal
    
    docx_stream = create_word_document(full_export_text)
    company = st.session_state.company_details.get("company_name", "Company")
    
    st.download_button(
        label="Download Final Package (.docx)",
        data=docx_stream,
        file_name=f"{company}_Visit_Report_and_Proposal.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    
    st.write("---")
    if st.button("Start New Engagement"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
