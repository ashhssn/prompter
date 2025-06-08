__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from docx import Document
import streamlit as st
import concurrent.futures
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def _run_with_timeout(func, arg, timeout=2):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(func, arg)
        try:
            result = future.result(timeout=timeout)
            return result
        except concurrent.futures.TimeoutError:
            print("Skipping current iter: took too long!")
            return "NIL"

def extract_table(doc_path, llm):
    doc = Document(doc_path)
    rows = []
    for it, table in enumerate(doc.tables):
        p_bar = st.progress(0, text=f"Processing table {it+1}")
        for it2, row in enumerate(table.rows[1:]):
            p_bar.progress((it2+1)/len(table.rows[1:]), text=f"Processing table {it+1} row {it2+1}/{len(table.rows[1:])}")
            desc = row.cells[0].text
            res  = _run_with_timeout(lambda x: llm.generate_evidence(x), desc, timeout=45)
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

def load_chroma_db():
    current_dir = os.path.dirname(__file__)
    persist_directory = os.path.abspath(os.path.join(current_dir, "..", "data", "chroma_db"))
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

def open_ended_feedback(llm, k: int = 4):
    questions = [ # questions required in section 3 of the report
    {
        "question": "How did the officer handle challenging moments?",
    },
    {
        "question": "Did the officer show signs of being triggered?",
    },
    {
        "question": "What early warning signs (if any) did the officer miss?",
    },
    {
        "question": "Were there any missed opportunities for better engagement?",
    },
    {
        "question": "Any additional observations and suggestions for improvement",
    }
]
    p_bar = st.progress(0)
    for it, q in enumerate(questions):
        p_bar.progress((it+1)/len(questions), text=f"Processing question {it+1}/{len(questions)}")
        # Compose input for LLM using existing feedback function
        st.write(f"***{q['question']}***")
        feedback = llm.generate_feedback(question=q["question"], k=k)
        st.write(feedback)