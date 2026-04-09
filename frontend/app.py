# app.py
# This is the Streamlit frontend — the visual interface users interact with.
# Streamlit turns Python code into a web app automatically.
# No HTML, CSS, or JavaScript needed — pure Python.

import streamlit as st
import requests

# The URL of our FastAPI backend
API_URL = "http://localhost:8000"

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Legal Document Analyser",
    page_icon="⚖️",
    layout="wide"
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("⚖️ Legal Document Analyser")
st.markdown("Upload a legal document and ask questions about it in plain English.")
st.divider()

# ── Session State ─────────────────────────────────────────────────────────────
# Streamlit reruns the entire script on every interaction.
# session_state persists data between reruns — like a memory for the app.
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "filename" not in st.session_state:
    st.session_state.filename = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Layout: Two Columns ───────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 2])

# ── LEFT COLUMN: Upload Section ───────────────────────────────────────────────
with left_col:
    st.subheader("📄 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload any legal document — contract, NDA, terms of service, etc."
    )
    
    if uploaded_file is not None:
        # Only process if it's a new file
        if st.session_state.filename != uploaded_file.name:
            with st.spinner("Processing document... this may take a moment"):
                try:
                    # Send the PDF to our FastAPI /upload endpoint
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    response = requests.post(f"{API_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Save document_id in session state for later use
                        st.session_state.document_id = data["document_id"]
                        st.session_state.filename = uploaded_file.name
                        st.session_state.chat_history = []  # Reset chat for new doc
                        st.success(f"✅ Document processed!")
                        st.info(f"📊 Split into **{data['chunk_count']}** chunks")
                    else:
                        st.error(f"Error: {response.json()['detail']}")
                except Exception as e:
                    st.error(f"Could not connect to backend: {str(e)}")
    
    # Show current document info
    if st.session_state.document_id:
        st.divider()
        st.markdown("**Current Document:**")
        st.markdown(f"📁 {st.session_state.filename}")
        st.markdown(f"🔑 ID: `{st.session_state.document_id}`")
        
        # Button to list all stored documents
        if st.button("📚 View All Documents"):
            response = requests.get(f"{API_URL}/documents")
            if response.status_code == 200:
                docs = response.json()["documents"]
                st.markdown(f"**{len(docs)} document(s) stored:**")
                for doc in docs:
                    st.markdown(f"- `{doc}`")

# ── RIGHT COLUMN: Q&A Section ─────────────────────────────────────────────────
with right_col:
    st.subheader("💬 Ask Questions")
    
    if not st.session_state.document_id:
        st.info("👈 Upload a document first to start asking questions")
    else:
        # Display chat history
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])
                # Show sources in an expandable section
                with st.expander("📖 View Source Excerpts"):
                    for i, source in enumerate(chat["sources"]):
                        st.markdown(f"**Excerpt {i+1}:**")
                        st.markdown(f"> {source[:300]}...")
                        st.divider()
        
        # Question input
        question = st.chat_input("Ask anything about the document...")
        
        if question:
            # Show the user's question immediately
            with st.chat_message("user"):
                st.write(question)
            
            # Call FastAPI /ask endpoint
            with st.chat_message("assistant"):
                with st.spinner("Analysing document..."):
                    try:
                        payload = {
                            "question": question,
                            "document_id": st.session_state.document_id,
                            "top_k": 5
                        }
                        response = requests.post(f"{API_URL}/ask", json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.write(data["answer"])
                            
                            # Save to chat history
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": data["answer"],
                                "sources": data["sources"]
                            })
                            
                            # Show sources
                            with st.expander("📖 View Source Excerpts"):
                                for i, source in enumerate(data["sources"]):
                                    st.markdown(f"**Excerpt {i+1}:**")
                                    st.markdown(f"> {source[:300]}...")
                                    st.divider()
                        else:
                            st.error(f"Error: {response.json()['detail']}")
                    except Exception as e:
                        st.error(f"Could not connect to backend: {str(e)}")