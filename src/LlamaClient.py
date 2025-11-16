from ollama import chat
from config import OLLAMA_MODEL

class LlamaClient:
    def __init__(self, model=OLLAMA_MODEL):
        self.model = model

    def generate_img_response(self, img_prompt):
        response = chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': 'You are a photography expert. Think step by step and analyze photos looking at perspective, lighting, content, and focus to answer questions.'
            },
            {
                'role':'user',
                'content': 'Describe the content, emomtion, and general vibe of this photo using words that could also be used to describe music. Take that description and condense it down to 10-15 words about the mood vibe and location',
                'images': [img_prompt] if isinstance(img_prompt, str) else img_prompt
            },
            ])
        return response['message']['content']
    
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
            ])
        return response['message']['content']
    
    def generate_playlist_values(self, keywords):
        response = chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': 'You are a spotify music expert that generates values from descriptions to be used to create spotify playlists.'
            },
            {
                'role':'user', 
                'content': f'Take these values that represent danceability, energy, liveness, loudness, and valence and provide a list of 20 songs that match these values. Display their score for danceability,energy,liveness, loudness, and valence: {keywords}'
            },
            ])
        return response['message']['content']
    
def main():
    client = LlamaClient()
    # Example usage of LlamaClient
    img_prompt = "../testImages/SunnyBeach.jpeg"
    print("Generating description for image...")
    description = client.generate_img_response(img_prompt)
    print("Image Description:", description)
    print("Generating keywords from description...")
    keywords = client.generate_keywords(description)
    print("Keywords:", keywords)
    print("Generating playlist values from keywords...")
    playlist_values = client.generate_playlist_values(keywords)
    print("Image Description:", playlist_values)  

main()