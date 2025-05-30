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
    
    def flatten_turns(first, second):
        # get output as: [start_time -> end_time] SPEAKER_ID: text
        first_text = f"\n[{first[0]['start']} -> {first[-1]['end']}] {first[0]['speaker_id']}: " + " ".join([f['text'] for f in first])
        second_text = f"[{second[0]['start']} -> {second[-1]['end']}] {second[0]['speaker_id']}: " + " ".join([s['text'] for s in second])
        # combine to process a speaker-pair document
        text = first_text + "\n" + second_text
        return text

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

        if first_turn and second_turn:
            content = flatten_turns(first_turn, second_turn)
            doc = LcDocument(
                page_content=content
            )
            grouped_docs.append(doc)

    return grouped_docs
    