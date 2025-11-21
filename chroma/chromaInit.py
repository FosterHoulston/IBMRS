import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np
import json
import os


# Createds a ChromaDB persistent client, embeds spotify songs from CSV, and stores them in ChromaDB
def initialize_chroma_db():
    # Load CSV
    spotify_data = "chroma/spotify_songs.csv"
    df = pd.read_csv(spotify_data)

    # Expected Numeric Columns
    expected_columns = ['danceability', 'energy', 'acousticness', 'liveness', 'tempo', 'valence']

    #Check Columns
    for c in expected_columns:
        if c not in df.columns:
            raise ValueError(f"Column '{c}' not found in the CSV.")

    # Build text for embedding (based only on volumes)
    def build_track_text(row):
        return (
            f"with danceability: {row['danceability']},"
            f"energy: {row['energy']},"
            f"acousticness: {row['acousticness']},"
            f"liveness: {row['liveness']},"
            f"tempo: {row['tempo']},"
            f"valence: {row['valence']}"
        )

    # Corrected: Create the 'text' column here, outside the function definition
    df["text"] = df.apply(build_track_text, axis=1)

    # File paths for saved embeddings
    embedding_file = "spotify_embeddings.npy"
    ids_file= "spotify_ids.json"
    metadata_file = "spotify_metadata.json"

    # Check if embeddings already exist
    if os.path.exists(embedding_file) and os.path.exists(ids_file) and os.path.exists(metadata_file):
        print("Loading existing embeddings...")
        embeddings = np.load(embedding_file)
        with open(ids_file, "r") as f:
            ids = json.load(f)
        with open(metadata_file, "r") as f:
            metadatas = json.load(f)
    else:
        print("Creating embedding model and computing embeddings...")
        embed_model = SentenceTransformer("all-mpnet-base-v2")
        embeddings = embed_model.encode(
            df["text"].tolist(),
            show_progress_bar=True,
            convert_to_numpy=True
        )

        #IDs and metadata
        ids = [str(i) for i in range(len(df))]
        metadatas = df[["name", "artists"] + expected_columns].to_dict(orient="records")


    # # Embed all rows 
    # print("Embedding texts...")
    # embeddings = embed_model.encode(
    #     df["text"].tolist(),
    #     show_progress_bar= True,
    #     convert_to_numpy=True)

    #Save embeddings to a .npy file
    np.save("spotify_embeddings.npy", embeddings)
    with open(ids_file, "w") as f:
        json.dump(ids, f)
    with open(metadata_file, "w") as f:
        json.dump(metadatas, f)
    print("Embeddings, IDs, and metadata saved to spotify_embeddings.npy.")


    # Create a local Chroma client and persistent directory
    # Updated to use chromadb.PersistentClient as per the error message
    client = chromadb.PersistentClient(path="./chromadb_db")

    # Delete old collection if it exists
    try:
        client.delete_collection("spotify_songs_collection")
    except:
        pass


    # Create new collection
    collection = client.get_or_create_collection("spotify_songs_collection")

    # # IDs
    # ids = [str(i) for i in range(len(df))]

    # # metadats = all numeric fields + name + artist
    # metadatas = df[["name", "artists"] + expected_columns].to_dict(orient="records")

    # Add to Chroma in batches
    batch_size = 200  # recommended batc size is 50-250
    documents = df["text"].tolist()
    embeddings_list = embeddings.tolist()

    print(f"Adding {len(ids)} tracks to Chroma in batches of {batch_size}...")
    for i in range(0, len(ids), batch_size):
        end_idx = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end_idx],
            embeddings=embeddings_list[i:end_idx],
            metadatas=metadatas[i:end_idx],
            documents=documents[i:end_idx]
        )
        print(f"Added batch {i//batch_size + 1}: records {i} to {end_idx}")

    # Persist DB (Note: PersistentClient auto-persists, but keeping for compatibility)
    print("Chroma created with", len(ids), "tracks.")