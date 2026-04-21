import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

with open('models_utf8.txt', 'w', encoding='utf-8') as f:
    for m in genai.list_models():
        f.write(m.name + '\n')
