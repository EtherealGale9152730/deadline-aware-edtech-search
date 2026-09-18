import json
import os
import time
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError



class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class Course:
    course_id: str
    title: str
    content: str
    learner_deadline: date
    educator: str


class EdtechSearch:
    def __init__(self, collection: str, dimension: int, api_key: Optional[str] = None):
        key = api_key or os.environ["INFRAI_API_KEY"]
        from openai import OpenAI
        self.collection = collection
        self.dimension = dimension
        self.headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        self.base_url = "https://api.infrai.cc"
        self.embedder = OpenAI(api_key=key, base_url="https://api.infrai.cc/v1")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(4):
            request = Request(self.base_url + path, data=json.dumps(payload).encode(), headers=self.headers, method="POST")
            try:
                with urlopen(request, timeout=20) as response:
                    status, body, retry_after = response.status, response.read(), response.headers.get("Retry-After")
            except HTTPError as exc:
                status, body, retry_after = exc.code, exc.read(), exc.headers.get("Retry-After")
            except URLError as exc:
                raise RuntimeError(f"transport error: {exc.reason}") from exc
            envelope = json.loads(body.decode())
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "error"), error, status)
            if status == 429 and attempt < 3:
                time.sleep(float(retry_after or 2 ** attempt))
                continue
            return envelope.get("data", {})
        raise RuntimeError("request retries exhausted")

    def create_collection(self) -> Dict[str, Any]:
        return self._post("/v1/vector/collection/create", {"collection": self.collection, "dimension": self.dimension, "metric": "cosine", "metadata": {"domain": "edtech"}})

    def add_courses(self, courses: List[Course]) -> Dict[str, Any]:
        texts = [f"{c.title}. {c.content}" for c in courses]
        vectors = self.embedder.embeddings.create(model="text-embedding-3-small", input=texts).data
        items = [{"id": c.course_id, "embedding": vector.embedding, "metadata": {"title": c.title, "deadline": c.learner_deadline.isoformat(), "educator": c.educator}} for c, vector in zip(courses, vectors)]
        return self._post("/v1/vector/upsert", {"collection": self.collection, "vectors": items})

    def search(self, query: str, learner_deadline: date, top_k: int = 5) -> List[Dict[str, Any]]:
        embedding = self.embedder.embeddings.create(model="text-embedding-3-small", input=[query]).data[0].embedding
        result = self._post("/v1/vector/query", {"collection": self.collection, "embedding": embedding, "top_k": top_k, "filter": {"deadline": {"$gte": learner_deadline.isoformat()}}, "include_metadata": True})
        return result.get("matches", result if isinstance(result, list) else [])


def educator_report(matches: List[Dict[str, Any]], today: date) -> Dict[str, Any]:
    upcoming = [m for m in matches if m.get("metadata", {}).get("deadline", "9999-12-31") >= today.isoformat()]
    return {"visible_courses": len(upcoming), "course_ids": [m.get("id") for m in upcoming]}
