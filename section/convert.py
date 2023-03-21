import streamlit as st
from lib.prepare import apply_remediations
from lib.utils import ParseStatus, get_parse_status, display_alert, alert

def ConvertSection(title, qna_url, req):
    st.header(title)

    if 'convert_alert' in st.session_state:
        display_alert('convert_alert')

    st.button('Fetch', on_click=fetch, args=(qna_url, req))

    origin_qnas = st.session_state.get('origin_qnas')
    if origin_qnas is not None:
        preview = { 'value': origin_qnas['value'][:1] }
        st.text('First element of the original data:')
        st.json(preview)

    st.button('Convert', on_click=convert)

    converted_qnas = st.session_state.get('converted_qnas')
    if converted_qnas is not None:
        st.caption('*All recommended remediations by `openai` were applied')

        converted_qnas_list = converted_qnas.split('\n')
        preview_lines = min(3, len(converted_qnas_list))
        preview = '\n'.join(converted_qnas_list[0:preview_lines])
        st.text(f'First {preview_lines} line(s) of the converted data:')
        st.markdown(f'```json\n{preview}\n```')

        st.download_button(
            label='Download',
            data=converted_qnas,
            file_name='output_prepared.jsonl',
            mime='application/jsonl'
        )

def fetch(qna_url, req):
    job_id = st.session_state.get('job_id')
    if job_id is not None:
        status_code, status_msg = get_parse_status(job_id, req)

        if status_code == ParseStatus.ERROR:
            alert('convert_alert', 'error', status_msg)
            return
        elif status_code == ParseStatus.PROCESSING:
            alert('convert_alert', 'warning', 'Still handling previous request')
            return

    res = req.get('qnas', { 'source': qna_url })

    if not res.ok:
        alert('convert_alert', 'error', res.reason)
        return

    st.session_state['origin_qnas'] = res.json()
    alert('convert_alert', 'success', 'Fetched')

def convert():
    origin_qnas = st.session_state.get('origin_qnas')
    if origin_qnas is None:
        alert('convert_alert', 'error', 'Should click "fetch" button first')
        return

    converted_data = []
    for qna_set in origin_qnas['value']:
        for question in qna_set['questions']:
            converted_data.append({
                'prompt': question,
                'completion': qna_set['answer']
            })

    final_data = apply_remediations(converted_data)
    st.session_state['converted_qnas'] = final_data
    alert('convert_alert', 'success', 'Converted')
