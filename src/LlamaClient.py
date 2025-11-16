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
                'content': f'Take these descriptive words and generate a set of 4 values between 0 and 1 with a precision of 2. These values will represent danceability, energy, liveness, and valence. Also generate a suggested tempo. Provide the values and nothing else: {keywords}'
            },
            {
                'role':'assistant',
                'content':'Format your response as a JSON object with the following structure: {"danceability": float, "energy": float, "liveness": float, "valence": float, "tempo": integer'
            }
            ])
        return response['message']['content']
    
def main():
    client = LlamaClient()
    # Example usage of LlamaClient
    img_prompt = "testImages/SunnyBeach.jpeg"
    print("Generating description for image...")
    description = client.generate_img_response(img_prompt)
    print("Image Description:", description)
    print("Generating keywords from description...")
    keywords = client.generate_keywords(description)
    print("Keywords:", keywords)
    print("Generating playlist values from keywords...")
    playlist_values = client.generate_playlist_values(keywords)
    print("Image Description:\n", playlist_values)  

main()