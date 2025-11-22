import chromadb as chroma
import os
from sentence_transformers import SentenceTransformer


# Load the same embedding model used during initialization
embed_model = SentenceTransformer("all-mpnet-base-v2")

# Query function to get playlist from ChromaDB
# @param query_text: The text input to be embedded and queried
# @param top_k: Number of top results to return
# @return: List of songs with their metadata
def query_chroma(query_text, top_k=5):
    # Use the same persistent client path as chromaInit.py
    db_path = os.path.join(os.path.dirname(__file__), "..", "chromadb_db")
    client = chroma.PersistentClient(path=db_path)
    collection = client.get_collection(name="spotify_songs_collection")

    # Embed the query text using the same model as initialization
    query_embedding = embed_model.encode([query_text], convert_to_numpy=True)

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
        include=["metadatas", "distances"]
    )

    playlist = []
    # results is a dict with keys: 'ids', 'distances', 'metadatas', 'embeddings', 'documents'
    # metadatas is a list of lists, where each inner list contains metadata dicts
    for metadata in results['metadatas'][0]:  # [0] because we queried with one query text
        song_info = {
            "name": metadata["name"],
            "artists": metadata["artists"],
            "danceability": metadata.get("danceability"),
            "energy": metadata.get("energy"),
            "acousticness": metadata.get("acousticness"),
            "liveness": metadata.get("liveness"),
            "valence": metadata.get("valence"),
            "tempo": metadata.get("tempo")
        }
        playlist.append(song_info)

    return playlist