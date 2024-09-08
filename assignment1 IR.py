import streamlit as st
import re
from collections import defaultdict
from PyPDF2 import PdfReader

def tokenize(text):
    """Tokenize the input text into a set of lowercase words."""
    return set(re.findall(r'\b\w+\b', text.lower()))

def build_inverted_index(docs):
    """
    Build an inverted index from a collection of documents.
    """
    index = defaultdict(set)
    for doc_id, text in docs.items():
        words = tokenize(text)
        for word in words:
            index[word].add(doc_id)
    return index

def boolean_retrieval(index, query):
    """
    Perform Boolean retrieval based on the inverted index.
    """
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    result_docs = set(index.keys())
    
    if 'and' in tokens:
        terms = query.split(' and ')
        result_docs = set(index.get(terms[0].strip(), set()))
        for term in terms[1:]:
            term = term.strip()
            result_docs = result_docs.intersection(index.get(term, set()))
    elif 'or' in tokens:
        terms = query.split(' or ')
        result_docs = set()
        for term in terms:
            term = term.strip()
            result_docs = result_docs.union(index.get(term, set()))
    elif 'not' in tokens:
        terms = query.split(' not ')
        if len(terms) == 2:
            term_to_exclude = terms[1].strip()
            result_docs = result_docs.difference(index.get(term_to_exclude, set()))
    else:
        result_docs = set()
        for token in tokens:
            result_docs = result_docs.union(index.get(token, set()))
    
    return result_docs

# Streamlit app
st.title("PDF Boolean Retrieval System")

documents = {}
doc_counter = 1

# Input PDFs until the user stops
uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True, type=["pdf"])

if uploaded_files:
    for uploaded_file in uploaded_files:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        documents[f"doc{doc_counter}"] = text
        doc_counter += 1

if st.button("Build Inverted Index"):
    if documents:
        inverted_index = build_inverted_index(documents)
        st.success("Inverted index built successfully!")
    else:
        st.warning("No documents uploaded!")

query = st.text_input("Enter your Boolean query:")

if query and 'inverted_index' in locals():
    results = boolean_retrieval(inverted_index, query)
    st.write(f"Results for query '{query}':")
    for doc_id in results:
        st.write(f"- {doc_id}: {documents[doc_id][:200]}...")
