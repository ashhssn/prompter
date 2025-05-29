import streamlit as st
from docx import Document
from modules.transcribe import Transcriber
from modules.openai_client import OpenAIClient
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document as LcDocument
import time
import pandas as pd
import os
from modules.prompts import EVIDENCE_PROMPT
from modules.helpers import group_as_speaker_pairs

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

api_key = st.secrets["openai_api_key"]
hf_api_key = api_key = st.secrets["hf_api_key"]

st.set_page_config(
    page_title="LLM‐Driven Document Evidence Generator",
    layout="wide",
    initial_sidebar_state="auto"
)

st.title("LLM‐Driven Document Evidence Generator")
st.subheader("How to use: Simply insert the system prompt into the text area below and click 'Process Document'. Note that \
             the whole process may take up to two minutes")

# Text area for the system prompt template
PROMPT = st.text_area(
    label="System prompt template (PROMPT)",
    value=(
        EVIDENCE_PROMPT
    ),
    height=450
)

uploaded_audio = "assets/muthu.wav"
uploaded_doc = "assets/checklist.docx"


def extract_table(doc_path, llm):
    doc = Document(doc_path)
    table = doc.tables[0]
    rows = []
    for row in table.rows[1:]:
        desc = row.cells[0].text
        res  = llm.generate_evidence(desc)
        if 'NIL' not in res and len(res) > 1:
            mark = "X"
            evidence = res
        else:
            mark = ""
            evidence = ""
        rows.append({
            "Description": desc,
            "Check": mark,
            "Evidence": evidence
        })
    return rows


if st.button("Process Document"):
    if not PROMPT:
        st.error("Please enter the system prompt template.")
    elif not uploaded_audio or not uploaded_doc:
        st.error("Upload both audio and DOCX files.")
    else:
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        if not os.path.isdir('transcript_store'):
            # transcribe audio
            transcriber = Transcriber(hf_api_key)
            result = transcriber.transcribe(audio_file=uploaded_audio)
            docs = group_as_speaker_pairs(result)
            transcript_store = Chroma.from_documents(docs, embedding=embeddings, persist_directory="transcript_store")
        else:
            transcript_store = Chroma(embedding_function=embeddings, persist_directory="transcript_store")

        llm_client = OpenAIClient(api_key, transcript_store, PROMPT)

        st.write("Processing prompt and reading/writing document...")

        start = time.time()
        table_data = extract_table(uploaded_doc, llm_client)
        elapsed = time.time() - start

        st.success(f"Processed in {elapsed:.2f}s")
        df = pd.DataFrame(table_data)
        # st.dataframe(df, use_container_width=True)
        st.table(df)
        st.subheader("Transcription:\n")
        with open("assets/transcription.txt", "r") as f:
            for line in f.readlines():
                st.write(line)
