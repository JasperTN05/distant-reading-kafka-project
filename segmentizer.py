import pandas as pd
import spacy
from typing import List, Dict, Any

# Deutsches spaCy-Modell laden
# Falls noch nicht installiert:
# python -m spacy download de_core_news_sm
nlp = spacy.load("de_core_news_sm")


def segment_text_by_sentences(
    text: str,
    target_tokens: int = 1000,
    min_tokens: int = 700
) -> List[Dict[str, Any]]:
    """
    Segmentiert einen Text satzweise in ungefähr gleich große (1000 Tokens) Segmente.
    Sätze werden dabei niemals zerschnitten..
    """
    if not isinstance(text, str) or not text.strip():
        return []

    doc = nlp(text)

    sentences = list(doc.sents)
    if not sentences:
        return []

    segments = []
    current_sents = []
    current_token_count = 0

    for sent in sentences:
        # Tokens ohne Spaces zählen
        sent_token_count = sum(1 for tok in sent if not tok.is_space)
        sent_text = sent.text.strip()

        # Leere Sätze überspringen
        if not sent_text:
            continue

        if not current_sents:
            current_sents.append(sent_text)
            current_token_count = sent_token_count
            continue

        projected_count = current_token_count + sent_token_count

        if current_token_count >= min_tokens and projected_count > target_tokens:
            segment_text = " ".join(current_sents).strip()
            segments.append({
                "segment_text": segment_text,
                "segment_token_count": current_token_count,
                "segment_sentence_count": len(current_sents)
            })

            current_sents = [sent_text]
            current_token_count = sent_token_count
        else:
            current_sents.append(sent_text)
            current_token_count = projected_count

    # Restsegment anhängen
    if current_sents:
        segment_text = " ".join(current_sents).strip()
        segments.append({
            "segment_text": segment_text,
            "segment_token_count": current_token_count,
            "segment_sentence_count": len(current_sents)
        })

    return segments


def segment_dataframe(
    df: pd.DataFrame,
    text_col: str = "text",
    id_col: str = "id",
    corpus_col: str = "corpus",
    genre_col: str = "genre",
    target_tokens: int = 1000,
    min_tokens: int = 700
) -> pd.DataFrame:
    """
    Wendet die satzbasierte Segmentierung auf ein ganzes DataFrame an.
    """
    rows = []

    for idx, row in df.iterrows():
        text = row.get(text_col, None)
        if not isinstance(text, str) or not text.strip():
            continue

        text_id = row[id_col] if id_col in df.columns else None
        corpus = row[corpus_col] if corpus_col in df.columns else None
        genre = row[genre_col] if genre_col in df.columns else None

        segments = segment_text_by_sentences(
            text=text,
            target_tokens=target_tokens,
            min_tokens=min_tokens
        )

        for seg_idx, seg in enumerate(segments, start=1):
            out = {
                "source_id": text_id,
                "corpus": corpus,
                "segment_id": f"{text_id}_{seg_idx}",
                "segment_index": seg_idx,
                "segment_text": seg["segment_text"],
                "token_count": seg["segment_token_count"],
                "sentence_count": seg["segment_sentence_count"]
            }

            if genre_col in df.columns:
                out["genre"] = genre

            rows.append(out)

    return pd.DataFrame(rows)