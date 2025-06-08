__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from modules.openai_client import OpenAIClient
import time
import pandas as pd
import os
from modules.prompts import EVIDENCE_PROMPT, FEEDBACK_PROMPT
from modules.helpers import extract_table, load_chroma_db, open_ended_feedback

api_key = st.secrets["openai_api_key"]
hf_api_key = st.secrets["hf_api_key"]

st.set_page_config(
    page_title="LLM‐Driven Document Generator",
    layout="wide",
    initial_sidebar_state="auto"
)

st.title("LLM‐Driven Document Generator")
st.subheader("Insert prompts for checklist (section 1 & 2) and open-ended feedback(section 3) respectively\n")

st.markdown("---")

st.write("Please note the following time that it will take to process checklist portion based on model selected: \n")

time_dict = {
    "Model name": ["gpt-4.1-mini", "gpt-4.1", "o4-mini"],
    "Average time taken to complete": ["~234 seconds", "~270 seconds", "~1096 seconds"]
}

st.table(time_dict)

# Add dropdown for choosing the type of model
MODEL = st.selectbox(
    "Select model (only for checklist):",
    ["gpt-4.1-mini", "gpt-4.1", "o4-mini"]
)

# Text area for the system prompt template
EVIDENCE_PROMPT = st.text_area(
    label="Prompt for checklist evidence generation",
    value=(
        EVIDENCE_PROMPT
    ),
    height=450
)

st.markdown("---")

st.write("Open ended feedback uses o4-mini by default, the latest OpenAI reasoning model.")

# Text area for the system prompt template
FEEDBACK_PROMPT = st.text_area(
    label="Prompt for open-ended generation",
    value=(
        FEEDBACK_PROMPT
    ),
    height=450
)

uploaded_audio = "assets/muthu.wav"
uploaded_doc = "assets/checklist.docx"


if st.button("Process Document"):
    if not EVIDENCE_PROMPT:
        st.error("Please enter the system prompt template.")
    elif not uploaded_audio or not uploaded_doc:
        st.error("Upload both audio and DOCX files.")
    else:
        transcript = ""
        with open("assets/transcript.txt", "r") as f:
            for line in f.readlines():
                transcript += line
            f.close()

        kb = load_chroma_db()

        llm_client = OpenAIClient(api_key, EVIDENCE_PROMPT, FEEDBACK_PROMPT, model=MODEL, transcript=transcript)
        llm_open_feedback = OpenAIClient(api_key, EVIDENCE_PROMPT, FEEDBACK_PROMPT, transcript=transcript, kb_store=kb)

        st.subheader("Checklist (Section 1 & 2)")

        start = time.time()
        table_data = extract_table(uploaded_doc, llm_client)
        elapsed = time.time() - start

        st.success(f"Checklist processed in {elapsed:.2f}s")
        df = pd.DataFrame(table_data)
        # st.dataframe(df, use_container_width=True)
        st.dataframe(df)
        
        st.markdown("---")

        st.subheader("Open-ended feedback (Section 3)")
        open_ended_feedback(llm_open_feedback)

        st.markdown("---")
        st.subheader("Transcription:\n")
        with open("assets/transcript.txt", "r") as f:
            for line in f.readlines():
                st.write(line)
