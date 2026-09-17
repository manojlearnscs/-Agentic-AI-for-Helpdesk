import json
import os
import re
from typing import List, Dict, Any, Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class RAGEngine:
    """
    RAG (Retrieval-Augmented Generation) Knowledge Base Engine for IT Helpdesk.
    Combines TF-IDF vector similarity search with keyword search fallback.
    """

    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "data", "kb_articles.json")
        self.data_path = data_path
        self.articles: List[Dict[str, Any]] = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_kb()

    def load_kb(self) -> bool:
        """Load Knowledge Base articles from JSON and index vectors."""
        if not os.path.exists(self.data_path):
            self.articles = []
            return False
        
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.articles = json.load(f)
            self._reindex()
            return True
        except Exception as e:
            print(f"Error loading KB data: {e}")
            self.articles = []
            return False

    def save_kb(self) -> bool:
        """Save Knowledge Base articles to JSON."""
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.articles, f, indent=2)
            self._reindex()
            return True
        except Exception as e:
            print(f"Error saving KB data: {e}")
            return False

    def _reindex(self):
        """Re-index documents for vector search."""
        if not self.articles or not SKLEARN_AVAILABLE:
            return

        corpus = []
        for doc in self.articles:
            # Combine title, summary, tags, and content for rich embedding context
            text = f"{doc.get('title', '')} {doc.get('category', '')} {' '.join(doc.get('tags', []))} {doc.get('summary', '')} {doc.get('content', '')}"
            corpus.append(text.lower())

        if corpus:
            self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 3, min_score: float = 0.05) -> List[Dict[str, Any]]:
        """
        Search Knowledge Base for relevant IT SOP articles.
        Returns top-k matching articles with similarity scores.
        """
        if not self.articles:
            return []

        results = []

        # 1. Vector Search via TF-IDF (if available)
        if SKLEARN_AVAILABLE and self.vectorizer and self.tfidf_matrix is not None:
            try:
                query_vec = self.vectorizer.transform([query.lower()])
                scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
                
                top_indices = np.argsort(scores)[::-1][:top_k]
                for idx in top_indices:
                    score = float(scores[idx])
                    if score >= min_score:
                        doc = dict(self.articles[idx])
                        doc["similarity_score"] = round(score, 4)
                        results.append(doc)
            except Exception as e:
                print(f"Vector search failed, falling back to keyword search: {e}")
                results = []

        # 2. Fallback Keyword Match if vector search yielded no results or sklearn unavailable
        if not results:
            query_words = set(re.findall(r'\w+', query.lower()))
            scored_docs = []
            for doc in self.articles:
                text = f"{doc.get('title', '')} {doc.get('category', '')} {' '.join(doc.get('tags', []))} {doc.get('summary', '')} {doc.get('content', '')}".lower()
                doc_words = set(re.findall(r'\w+', text))
                overlap = len(query_words.intersection(doc_words))
                if overlap > 0:
                    score = overlap / (len(query_words) + 1e-5)
                    doc_copy = dict(doc)
                    doc_copy["similarity_score"] = round(score, 4)
                    scored_docs.append(doc_copy)

            scored_docs.sort(key=lambda x: x["similarity_score"], reverse=True)
            results = scored_docs[:top_k]

        return results

    def add_article(self, title: str, category: str, tags: List[str], summary: str, content: str) -> Dict[str, Any]:
        """Add a new article to the Knowledge Base."""
        new_id = f"KB{len(self.articles) + 1:03d}"
        article = {
            "id": new_id,
            "title": title,
            "category": category,
            "tags": tags,
            "summary": summary,
            "content": content
        }
        self.articles.append(article)
        self.save_kb()
        return article
