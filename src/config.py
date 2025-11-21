from dotenv import load_dotenv
import os

load_dotenv()

# Llama model to use
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2-vision")