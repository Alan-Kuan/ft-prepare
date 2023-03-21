import streamlit as st
from lib.utils import ParseStatus, get_parse_status, display_alert, alert

def ParseSection(title, req):
    st.header(title)

    if 'parse_alert' in st.session_state:
        display_alert('parse_alert')

    qna_url = st.text_input('Q&A URL')
    display_name = st.text_input('Display Name')

    st.button('Parse', on_click=parse_qna, args=(qna_url, display_name, req))
    st.button('Status', on_click=check_status, args=(req,))

    return qna_url

def parse_qna(qna_url, display_name, req):
    job_id = st.session_state.get('job_id')
    if job_id is not None:
        status_code, _ = get_parse_status(job_id, req)
        if status_code != ParseStatus.SUCCESS:
            alert('parse_alert', 'error', 'Still handling previous request')
            return

    if qna_url == '':
        alert('parse_alert', 'error', 'No URL was given')
        return

    res = req.patch('sources', [
        {
            'op': 'add',
            'value': {
                'displayName': display_name,
                'sourceUri': qna_url,
                'sourceKind': 'url',
                'source': qna_url
            }
        }
    ])

    alert('parse_alert', 'info', 'Request sent!')

    if res.status_code != 202:
        alert('parse_alert', 'error', res.reason)
        return

    op_loc = res.headers['operation-location']
    job_id = op_loc.split('/')[9].split('?')[0]
    st.session_state['job_id'] = job_id

def check_status(req):
    job_id = st.session_state.get('job_id')
    if job_id is None:
        alert('parse_alert', 'error', 'Have not sent any request!')
        return

    status_code, status_msg = get_parse_status(job_id, req)
    if status_code == ParseStatus.ERROR:
        alert_type = 'error'
    elif status_code == ParseStatus.PROCESSING:
        alert_type = 'info'
    else:
        alert_type = 'success'

    alert('parse_alert', alert_type, status_msg)
