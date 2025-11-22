from ollama import chat
from config import OLLAMA_MODEL
from ChromaClient import query_chroma
import json

class LlamaClient:
    def __init__(self, model=OLLAMA_MODEL):
        self.model = model

    # Generate image description response
    # @param img_prompt: The image input (file path or image data)
    # @return: Description text of the image
    def generate_img_response(self, img_prompt):
        response = chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': 'You are a photography expert. Think step by step and analyze photos looking at perspective, lighting, content, and focus to answer questions.'
            },
            {
                'role':'user',
                'content': 'Describe the content, emomtion, and general vibe of this photo using words that could also be used to describe music: Be detailed but brief.',
                'images': [img_prompt] if isinstance(img_prompt, str) else img_prompt
            },
            ])
        return response['message']['content']
    
    # Generate keywords from text prompt
    # @param text_prompt: The text input to extract keywords from
    # @return: Keywords string
    def generate_keywords(self, text_prompt):
        response = chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': 'You are a helpful assistant that generates keywords for music playlists based on photo descriptions.'
            },
            {
                'role':'user', 
                'content': f'Distill this information down to 10 to 15 key words about the vibe and location. Only give me the 10-15 key words that could also be used to describe music. Do not give any other response: {text_prompt}'
            },
            {
                'role':'assistant',
                'content':'Provide the keywords as a comma-separated list.'
            }
            ])
        return response['message']['content']
    
    # Generate playlist values from keywords
    # @param keywords: The keywords input to generate playlist values from
    # @return: JSON string with playlist values
    def generate_playlist_values(self, keywords):
        response = chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': 'You are a spotify music expert that generates values from descriptions to be used to create spotify playlists.'
            },
            {
                'role':'user', 
                'content': f'Take these descriptive words and generate a set of 4 values between 0 and 1 with a precision of 2. These values will represent danceability, energy, acousticness, liveness, and valence. Also generate a suggested tempo. Provide the values and nothing else: {keywords}'
            },
            {
                'role':'assistant',
                'content':'Format your response as a JSON object with the following structure: {"danceability": float, "energy": float, "acousticness": float, "liveness": float, "valence": float, "tempo": integer'
            }
            ])
        return response['message']['content']

    # Pipeline method to process image and generate playlist
    # @param img_prompt: The image input (file path or image data)
    # @return: Tuple of (playlist results as list of dicts, keywords as list of strings)
    def pipeline(self, img_prompt):
        print("Generating description for image...")
        description = self.generate_img_response(img_prompt)
        print("Image Description:", description)
        print("Generating keywords from description...")
        keywords = self.generate_keywords(description)
        print("Keywords:", keywords)
        print("Generating playlist values from keywords...")
        playlist_values = self.generate_playlist_values(keywords)
        print("Playlist values:\n", playlist_values)
        chroma_query = query_chroma(playlist_values, 15)
        format_query = json.dumps(chroma_query, indent=2)
        print("Chroma Query Results:\n", format_query)

        # Return the list of songs and keywords as a list
        # Clean up keywords - remove numbering like "1.", "2.", etc.
        import re
        if ',' in keywords:
            keywords_list = [re.sub(r'^\d+\.\s*', '', k.strip()) for k in keywords.split(',') if k.strip()]
        else:
            # Split by whitespace and remove numbers
            keywords_list = [re.sub(r'^\d+\.\s*', '', k.strip()) for k in keywords.split() if k.strip()]

        # Filter out any remaining empty strings
        keywords_list = [k for k in keywords_list if k]

        return chroma_query, keywords_list[:3]