"""FAISS Vector Store for Bhagavad Gita Verse Retrieval"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional

# Try to import FAISS and sentence-transformers
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False


class GitaVectorStore:
    """
    FAISS-powered semantic search over Bhagavad Gita verses.
    Falls back to keyword search if FAISS/sentence-transformers unavailable.
    """

    def __init__(self, data_path: str = None, embeddings_dir: str = None):
        base = Path(__file__).parent.parent.parent
        self.data_path = data_path or str(base / "data" / "gita_verses.csv")
        self.embeddings_dir = embeddings_dir or str(base / "data" / "embeddings")
        self.index_path = os.path.join(self.embeddings_dir, "gita_faiss.index")
        self.meta_path = os.path.join(self.embeddings_dir, "gita_meta.pkl")

        self.verses_df = None
        self.index = None
        self.model = None
        self.verse_metadata = []

        os.makedirs(self.embeddings_dir, exist_ok=True)
        self._load_data()

        if FAISS_AVAILABLE and ST_AVAILABLE:
            self._setup_faiss()
        else:
            print("[WARNING] FAISS/sentence-transformers not available. Using keyword search.")

    def _load_data(self):
        """Load verses CSV."""
        try:
            self.verses_df = pd.read_csv(self.data_path)
            print(f"[OK] Loaded {len(self.verses_df)} Gita verses.")
        except Exception as e:
            print(f"[ERROR] Could not load verses CSV: {e}")
            self.verses_df = pd.DataFrame()

    def _setup_faiss(self):
        """Build or load FAISS index."""
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "rb") as f:
                    self.verse_metadata = pickle.load(f)
                print(f"[OK] Loaded FAISS index with {self.index.ntotal} vectors.")
                return
            except Exception as e:
                print(f"[WARNING] Could not load FAISS index: {e}. Rebuilding...")

        self._build_index()

    def _build_index(self):
        """Build FAISS index from verses."""
        if self.verses_df is None or self.verses_df.empty:
            return

        print("[BUILDING] Building FAISS index...")
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"❌ Could not load sentence transformer: {e}")
            return

        # Build text for embedding: english + keywords
        texts = []
        self.verse_metadata = []

        for _, row in self.verses_df.iterrows():
            text = f"{row.get('english', '')} {row.get('keywords', '')} {row.get('topic', '')}"
            texts.append(text)
            self.verse_metadata.append({
                "chapter": int(row.get("chapter", 0)),
                "verse": int(row.get("verse", 0)),
                "sanskrit": row.get("sanskrit", ""),
                "transliteration": row.get("transliteration", ""),
                "english": row.get("english", ""),
                "hindi": row.get("hindi", ""),
                "marathi": row.get("marathi", ""),
                "topic": row.get("topic", ""),
                "keywords": row.get("keywords", "")
            })

        embeddings = self.model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype=np.float32)

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner product (cosine after normalization)
        self.index.add(embeddings)

        # Save
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.verse_metadata, f)

        print(f"✅ FAISS index built with {self.index.ntotal} vectors.")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant verses."""
        if self.index is not None and FAISS_AVAILABLE and ST_AVAILABLE:
            return self._faiss_search(query, top_k)
        return self._keyword_search(query, top_k)

    def _faiss_search(self, query: str, top_k: int) -> List[Dict]:
        """FAISS semantic search."""
        try:
            if self.model is None:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')

            query_vec = self.model.encode([query], show_progress_bar=False)
            query_vec = np.array(query_vec, dtype=np.float32)
            faiss.normalize_L2(query_vec)

            scores, indices = self.index.search(query_vec, top_k)
            results = []
            for idx, score in zip(indices[0], scores[0]):
                if idx < len(self.verse_metadata) and score > 0.1:
                    verse = dict(self.verse_metadata[idx])
                    verse["score"] = float(score)
                    results.append(verse)
            return results
        except Exception as e:
            print(f"[WARNING] FAISS search failed: {e}. Falling back to keyword search.")
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """Fallback keyword-based search."""
        if self.verses_df is None or self.verses_df.empty:
            return []

        query_lower = query.lower()
        query_words = set(query_lower.split())

        scores = []
        for _, row in self.verses_df.iterrows():
            searchable = (
                str(row.get("english", "")) + " " +
                str(row.get("keywords", "")) + " " +
                str(row.get("topic", ""))
            ).lower()

            score = sum(1 for word in query_words if word in searchable)

            # Boost common life problem keywords
            boosts = {
                "anxiety": ["anxiety", "stress", "tension", "worry", "fear"],
                "career": ["career", "work", "job", "duty", "action"],
                "grief": ["grief", "loss", "death", "sorrow", "sadness"],
                "study": ["study", "education", "exam", "learning", "knowledge"],
                "money": ["money", "financial", "wealth", "poverty"],
                "anger": ["anger", "frustration", "conflict"],
                "relationship": ["relationship", "love", "family", "friend"],
                "purpose": ["purpose", "meaning", "life", "goal", "direction"]
            }
            for category, words in boosts.items():
                if any(w in query_lower for w in words):
                    if any(w in searchable for w in words):
                        score += 2

            scores.append((score, row))

        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, row in scores[:top_k]:
            if score > 0:
                results.append({
                    "chapter": int(row.get("chapter", 0)),
                    "verse": int(row.get("verse", 0)),
                    "sanskrit": row.get("sanskrit", ""),
                    "transliteration": row.get("transliteration", ""),
                    "english": row.get("english", ""),
                    "hindi": row.get("hindi", ""),
                    "marathi": row.get("marathi", ""),
                    "topic": row.get("topic", ""),
                    "keywords": row.get("keywords", ""),
                    "score": float(score)
                })

        # If no match, return most universal verses (2:47, 6:5, 18:66)
        if not results:
            universal = [
                r for _, r in scores
                if int(r.get("chapter", 0)) in [2, 6, 18]
            ][:top_k]
            for row in universal:
                results.append({
                    "chapter": int(row.get("chapter", 0)),
                    "verse": int(row.get("verse", 0)),
                    "sanskrit": row.get("sanskrit", ""),
                    "transliteration": row.get("transliteration", ""),
                    "english": row.get("english", ""),
                    "hindi": row.get("hindi", ""),
                    "marathi": row.get("marathi", ""),
                    "topic": row.get("topic", ""),
                    "keywords": row.get("keywords", ""),
                    "score": 0.5
                })
        return results

    def get_verse(self, chapter: int, verse: int) -> Optional[Dict]:
        """Get a specific verse by chapter and verse number."""
        if self.verses_df is None:
            return None
        match = self.verses_df[
            (self.verses_df["chapter"] == chapter) &
            (self.verses_df["verse"] == verse)
        ]
        if not match.empty:
            row = match.iloc[0]
            return {
                "chapter": int(row["chapter"]),
                "verse": int(row["verse"]),
                "sanskrit": row.get("sanskrit", ""),
                "transliteration": row.get("transliteration", ""),
                "english": row.get("english", ""),
                "hindi": row.get("hindi", ""),
                "marathi": row.get("marathi", "")
            }
        return None
