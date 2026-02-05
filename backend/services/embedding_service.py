"""
Embedding Service - Generate and search PDF embeddings using OpenAI
"""
import os
from typing import List, Tuple
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Embedding model (text-embedding-3-small is cost-effective)
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks


def chunk_text(text: str) -> List[str]:
    """
    Split text into overlapping chunks for embedding

    Args:
        text: Full PDF text

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + CHUNK_SIZE
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < text_len:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)

            if break_point > CHUNK_SIZE * 0.5:  # Don't break too early
                end = start + break_point + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = end - CHUNK_OVERLAP  # Overlap for context continuity

    return chunks


def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    """
    Generate embeddings for text chunks using OpenAI

    Args:
        chunks: List of text chunks

    Returns:
        List of embedding vectors
    """
    try:
        response = client.embeddings.create(
            input=chunks,
            model=EMBEDDING_MODEL
        )

        embeddings = [item.embedding for item in response.data]
        return embeddings

    except Exception as e:
        print(f"Embedding generation error: {e}")
        raise Exception("Failed to generate embeddings")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Similarity score (0 to 1)
    """
    a = np.array(vec1)
    b = np.array(vec2)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_chunks(
    query: str,
    chunks: List[str],
    embeddings: List[List[float]],
    top_k: int = 3
) -> List[Tuple[str, float]]:
    """
    Search for most relevant chunks using semantic similarity

    Args:
        query: User's search query
        chunks: List of text chunks
        embeddings: Corresponding embedding vectors
        top_k: Number of top results to return

    Returns:
        List of (chunk_text, similarity_score) tuples
    """
    try:
        # Generate embedding for query
        query_response = client.embeddings.create(
            input=[query],
            model=EMBEDDING_MODEL
        )
        query_embedding = query_response.data[0].embedding

        # Calculate similarities
        similarities = []
        for i, chunk_embedding in enumerate(embeddings):
            score = cosine_similarity(query_embedding, chunk_embedding)
            similarities.append((chunks[i], score))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    except Exception as e:
        print(f"Search error: {e}")
        raise Exception("Failed to search chunks")


def process_pdf_for_search(pdf_text: str) -> dict:
    """
    Process PDF text: chunk and generate embeddings

    Args:
        pdf_text: Extracted PDF text

    Returns:
        Dict with chunks and embeddings
    """
    chunks = chunk_text(pdf_text)
    embeddings = generate_embeddings(chunks)

    return {
        "chunks": chunks,
        "embeddings": embeddings,
        "chunk_count": len(chunks)
    }
