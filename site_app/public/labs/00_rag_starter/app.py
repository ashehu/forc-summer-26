#!/usr/bin/env python3
"""A retrieval-first Streamlit interface for the starter corpus."""

from __future__ import annotations

import streamlit as st
from retrieve import RetrievalError, load_index, rank_passages


@st.cache_resource
def cached_index() -> dict:
    return load_index()


st.set_page_config(page_title="RAG Starter", page_icon="🔎", layout="wide")
st.title("RAG Starter: inspect retrieval first")
st.caption("Fictional 20-page graduate-program corpus · evidence view only")

try:
    index = cached_index()
except RetrievalError as error:
    st.error(str(error))
    st.stop()

question = st.text_input(
    "Question",
    "I have no Python experience. What should I attend first, and where can I get help?",
)
top_k = st.slider("Passages to retrieve", min_value=1, max_value=8, value=4)

if st.button("Retrieve evidence", type="primary") and question.strip():
    try:
        ranked = rank_passages(question, index, top_k)
    except RetrievalError as error:
        st.error(str(error))
        st.stop()
    st.subheader("Evidence packet")
    for rank, item in enumerate(ranked, start=1):
        st.markdown(f"### {rank}. {item['title']} · page {item['page']}")
        st.caption(
            f"{item['filename']} · {item['document_type']} · similarity {item['score']:.3f}"
        )
        st.write(item["text"])
        st.divider()

st.info(
    "Similarity search always returns something. A high-ranked passage is evidence to inspect, "
    "not proof that the corpus answers the question."
)
