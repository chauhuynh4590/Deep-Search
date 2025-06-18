"""
Streamlit app for Agentic Deep Researcher: a web UI for uploading files, entering research queries,
calling the backend API, and displaying/formatting results (including PDF download).
"""

import os
import io
import re
import json
import tempfile
import requests
import streamlit as st
import markdown
from typing import Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# =============================
# Constants and Configurations
# =============================
API_URL = os.getenv("RESEARCH_API_URL", "http://localhost:8000/query")
SUPPORTED_FILE_TYPES = ["png", "jpg", "jpeg", "pdf", "docx"]
PAGE_TITLE = "🔍 Agentic Deep Researcher"

st.set_page_config(page_title=PAGE_TITLE, layout="wide")

# =============================
# Utility Functions
# =============================
def reset_chat() -> None:
    """Reset the chat history in session state."""
    st.session_state.messages = []

def extract_file_text(uploaded_file) -> str:
    """Extract text from uploaded file using DocumentConverter."""
    from docling.document_converter import DocumentConverter
    with tempfile.NamedTemporaryFile(delete=False, suffix='_' + uploaded_file.name) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    converter = DocumentConverter()
    result = converter.convert(tmp_path)
    return result.document.export_to_markdown()

def call_research_api(user_content: str) -> str:
    """Call the backend research API and return the result or error message."""
    try:
        resp = requests.post(API_URL, json={"input": user_content})
        resp.raise_for_status()
        response_json = resp.json()
        return response_json.get("result", "No result returned from API.")
    except Exception as e:
        error_message = str(e)
        user_message = None
        try:
            match = re.search(r'\{.*\}', error_message)
            if match:
                error_json = json.loads(match.group(0))
                user_message = error_json.get('error', {}).get('message')
        except Exception:
            pass
        if not user_message:
            quoted = re.findall(r'"([^"]+)"', error_message)
            if quoted:
                user_message = quoted[-1]
        if not user_message:
            user_message = "An error occurred while contacting backend API. Please try again later."
        return user_message

def generate_pdf_from_markdown(markdown_text: str) -> io.BytesIO:
    """Generate a PDF from markdown text and return as BytesIO buffer."""
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    left_margin = 40
    right_margin = 40
    top_margin = height - 50
    bottom_margin = 50
    line_height = 16
    max_width = width - left_margin - right_margin
    font_name = "Helvetica"
    font_size = 12
    y = top_margin
    textobject = c.beginText(left_margin, y)
    textobject.setFont(font_name, font_size)
    for line in markdown_text.split('\n'):
        words = line.split()
        if not words:
            if y <= bottom_margin:
                c.drawText(textobject)
                c.showPage()
                y = top_margin
                textobject = c.beginText(left_margin, y)
                textobject.setFont(font_name, font_size)
            textobject.textLine("")
            y -= line_height
            continue
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if c.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line = test_line
            else:
                if y <= bottom_margin:
                    c.drawText(textobject)
                    c.showPage()
                    y = top_margin
                    textobject = c.beginText(left_margin, y)
                    textobject.setFont(font_name, font_size)
                textobject.textLine(current_line)
                y -= line_height
                current_line = word
        if current_line:
            if y <= bottom_margin:
                c.drawText(textobject)
                c.showPage()
                y = top_margin
                textobject = c.beginText(left_margin, y)
                textobject.setFont(font_name, font_size)
            textobject.textLine(current_line)
            y -= line_height
    c.drawText(textobject)
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# =============================
# UI Layout and Logic
# =============================
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    pass  # Add sidebar content here if needed

col1, col2 = st.columns([6, 1])
with col1:
    st.markdown(f"<h2 style='color: #0066cc;'>{PAGE_TITLE}</h2>", unsafe_allow_html=True)
with col2:
    st.button("Clear ↺", on_click=reset_chat)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.form("query_form"):
    text_input = st.text_area("Enter your question (optional)")
    uploaded_file = st.file_uploader(
        "Upload a file (image, PDF, DOCX) (optional)", type=SUPPORTED_FILE_TYPES)
    submit = st.form_submit_button("Submit")

file_text = ""
if submit:
    if uploaded_file:
        with st.spinner("Processing file... This may take a moment..."):
            file_text = extract_file_text(uploaded_file)
    user_content = text_input.strip() if text_input else ""
    if file_text:
        user_content += f"\n\n[file content]:\n{file_text}"
    if user_content:
        st.session_state.messages.append({"role": "user", "content": user_content})
        with st.chat_message("user"):
            st.markdown(user_content)
        with st.spinner("Researching... This may take a moment..."):
            response = call_research_api(user_content)
        with st.chat_message("assistant"):
            html_report = markdown.markdown(response)
            st.components.v1.html(html_report, height=600, scrolling=True)
            pdf_buffer = generate_pdf_from_markdown(response)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_buffer,
                file_name="report.pdf",
                mime="application/pdf"
            )
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.warning("Please enter a question or upload a file.")
