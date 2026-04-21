# AI Visit Report Generator

## Overview
The **AI Visit Report Generator** is a Python-based web application built with [Streamlit](https://streamlit.io/) that automates the generation of professional company visit reports. By leveraging the **Google Gemini API**, the application assists business consultants and professionals in preparing for client visits, collecting structured insights, and automatically synthesizing them into polished executive reports.

## Features
- **Dynamic Question Generation:** Automatically generates targeted, strategic interview questions based on the target company and its industry.
- **Guided Workflow:** A smooth, 5-phase interactive UI that guides the user from initial data entry to final document export.
- **AI-Powered Synthesis:** Converts rough field notes and observations into a highly professional executive summary.
- **One-Click Export:** Instantly exports the fully formatted report into a downloadable Microsoft Word (`.docx`) document.

## Project Structure
- `app.py`: The main Streamlit application containing the UI logic, session state management, and the 5-phase workflow.
- `generate_ai.py`: Handles all integrations and prompt engineering with the Google Gemini AI model to generate questions and synthesize text.
- `export_utils.py`: Utility functions utilizing `python-docx` to parse the AI-generated text and dynamically generate a `.docx` file in memory.
- `requirements.txt`: Lists all necessary Python dependencies to run the application.

## Application Workflow

The application guides the user through a structured five-phase pipeline:

1. **Phase 1: Input Company Details**
   - The user inputs core context about the target company, including Company Name, Industry, Visit Date, and Primary Contact.

2. **Phase 2: Generate Interview Questions**
   - *Requires a valid Gemini API key.*
   - The AI generates 5 insightful, industry-specific interview questions tailored to the provided company context to help guide the visit.

3. **Phase 3: Collect Observations**
   - Provides a dynamic form where the user can input raw field notes, answers, and observations corresponding to each of the generated questions from the visit.

4. **Phase 4: Report Synthesis**
   - *Requires a valid Gemini API key.*
   - The AI processes the company details alongside the user's raw notes to draft a formal executive report. 
   - The generated report typically includes sections like an Executive Summary, Key Considerations, and Action Items. The user is provided with a text area to manually review and edit the draft.

5. **Phase 5: Export Report**
   - The final, synthesized report text is converted into a structured Word Document (`.docx`) and made available for immediate download. The user can then start a brand new report, resetting the workflow.

## Getting Started

### Prerequisites
- Python 3.8+ installed on your system.
- An active **Google Gemini API Key** (or you can add it to a local `.env` file).

### Installation
1. Open up your terminal and navigate to this project directory:
   ```bash
   cd d:\nothing
   ```
2. Activate your virtual environment (if used) and install the core dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
1. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```
2. Your default web browser will open (usually to `http://localhost:8501`).
3. Proceed through the setup and provide your **Gemini API Key** when prompted by the application.

## Usage Note
If you prefer not to enter your Gemini API key every time, you can create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_api_key_here
```
The application will automatically detect and load it on startup.
