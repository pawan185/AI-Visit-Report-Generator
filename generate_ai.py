from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15), reraise=True)
def generate_scope_and_questions(api_key: str, company_details: dict) -> str:
    client = get_gemini_client(api_key)
    
    name = company_details.get("company_name", "the target company")
    industry = company_details.get("industry", "its industry")
    contact = company_details.get("primary_contact", "Unknown")
    
    prompt = f"""You are an expert. Based on the provided company details, output a two-part response.
Part 1: A 'Scope Document' with exact headers: Industry Visited, Type of Industry, Short Details/Background, Anticipated Challenges, and Expected Customer Expectations.
Part 2: 'Discovery Questions'. Generate 5 open-ended, polite questions to uncover operational challenges and software needs.

STRICT RULE: Do not ask highly sensitive financial questions regarding direct revenue or private margins, and no hard questions. NEVER mention that you are an AI, an assistant, or use the word 'Gemini'.

Company Context:
- Company Name: {name}
- Industry: {industry}
- Primary Contact: {contact}
"""
    
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt
    )
    return response.text

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15), reraise=True)
def generate_visit_report(api_key: str, company_details: dict, user_notes: dict) -> str:
    client = get_gemini_client(api_key)
    
    name = company_details.get("company_name", "the target company")
    industry = company_details.get("industry", "its industry")
    
    obs_text = "OBSERVATIONS FROM THE VISIT:\n"
    for q, a in user_notes.items():
        obs_text += f"- Question: {q}\n"
        obs_text += f"- Answer/Notes: {a}\n\n"
        
    prompt = f"""You are an executive consultant. Synthesize the raw field notes into a formal Visit Report.

STRICT RULE: Do NOT invent, assume, or output a 'Project Name' anywhere in this report. NEVER mention that you are an AI, an assistant, or use the word 'Gemini'.
Format the output using clean markdown subheadings (e.g., ### Executive Summary, ### Key Observations, ### Action Items).

Company: {name}
Industry: {industry}

{obs_text}"""
    
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt
    )
    return response.text

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=15), reraise=True)
def generate_client_proposal(api_key: str, scope_document: str, visit_report: str) -> str:
    client = get_gemini_client(api_key)
    
    prompt = f"""Based on the Scope Document context and the Post-Visit Report findings, draft a formal Client Proposal. 
The proposal should outline a recommended solution that addresses the specific pain points identified in the report, highlighting value propositions and proposed next steps.
Format with professional markdown headers.
STRICT RULE: NEVER mention that you are an AI, an assistant, or use the word 'Gemini'.

--- SCOPE DOCUMENT ---
{scope_document}

--- POST-VISIT REPORT ---
{visit_report}"""
    
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt
    )
    return response.text
