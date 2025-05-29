from langchain.schema import Document as LcDocument
from docx import Document

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

def group_as_speaker_pairs(transcript):
    """
    Groups transcript into speaker pairs: a turn and the reply.
    """
    grouped_docs = []
    
    def flatten_turns(turns):
        text = "\n".join([f"{t['speaker_id']}: {t['text']}" for t in turns])
        return text, turns[0]['start'], turns[-1]['end']

    i = 0
    while i < len(transcript):
        # Collect all turns from one speaker
        first_speaker = transcript[i]['speaker_id']
        first_turn = []
        while i < len(transcript) and transcript[i]['speaker_id'] == first_speaker:
            first_turn.append(transcript[i])
            i += 1

        # Collect the reply (other speaker)
        second_turn = []
        if i < len(transcript):
            second_speaker = transcript[i]['speaker_id']
            while i < len(transcript) and transcript[i]['speaker_id'] == second_speaker:
                second_turn.append(transcript[i])
                i += 1

        all_turns = first_turn + second_turn
        if all_turns:
            content, start, end = flatten_turns(all_turns)
            doc = LcDocument(
                page_content=content,
                metadata={
                    'start': start,
                    'end': end,
                }
            )
            grouped_docs.append(doc)

    return grouped_docs
    