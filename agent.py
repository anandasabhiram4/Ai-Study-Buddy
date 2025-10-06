import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def ask_gemini(prompt, context=""):
    """
    Ask the Gemini model a question.
    `prompt` : the user question or instruction
    `context`: optional additional text (like PDF content)
    """
    # Combine context + user prompt if context exists
    full_prompt = context + "\n\n" + prompt if context else prompt

    # Create the model
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Generate the response
    response = model.generate_content(full_prompt)

    return response.text
