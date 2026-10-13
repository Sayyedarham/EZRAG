from rag_core import bm25_scores, rank_chunks


CHUNKS = [
    {"id": "one", "source": "guide", "text": "The support team handles billing questions."},
    {"id": "two", "source": "guide", "text": "Engineers own the deployment pipeline."},
]


def test_bm25_ranks_matching_chunk_first() -> None:
    scores = bm25_scores("Who handles billing?", CHUNKS)
    assert scores[0] > scores[1]


def test_bm25_omits_non_matching_evidence() -> None:
    ranked, _ = rank_chunks("cafeteriaqz", CHUNKS, "BM25", None, 5)
    assert ranked == []
