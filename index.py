from dataclasses import dataclass
import streamlit as st
import requests
import json
import os

app_name = 'ft-prepare'

st.set_page_config(
    page_title=app_name
)

st.title(app_name)

# Utils
# -------------------------------------- #

@dataclass
class Req:
    base_url: str
    headers: dict
    params: dict

    def get(self, route, params=dict()):
        params.update(self.params)
        return requests.get(f'{self.base_url}/{route}', headers=self.headers, params=params)

    def patch(self, route, data):
        return requests.patch(f'{self.base_url}/{route}', headers=self.headers, params=self.params, json=data)

def display_alert(alert_loc):
    alert = st.session_state[alert_loc]
    alert_type = alert['type']
    alert_msg = alert['msg']

    if alert_type == 'info':
        st.info(alert_msg)
    elif alert_type == 'success':
        st.success(alert_msg)
    elif alert_type == 'warning':
        st.warning(alert_msg)
    elif alert_type == 'error':
        st.error(alert_msg)

def alert(alert_loc, alert_type, alert_msg):
    st.session_state[alert_loc] = {
        'type': alert_type,
        'msg': alert_msg
    }

def get_parse_status(job_id):
    res = req.get(f'sources/jobs/{job_id}')
    if not res.ok:
        return 0, res.reason
    data = res.json()
    status_code = 2 if data['status'] == 'succeeded' else 1
    return status_code, data['status']

# Credentials
# -------------------------------------- #

st.header('Cognitive Services Credentials')

api_key = st.text_input('API Key', type='password')
endpoint = st.text_input('API Endpoint')
project = st.text_input('Project Name')

req = Req(
    base_url=f'{endpoint}/language/query-knowledgebases/projects/{project}',
    headers={
        'Ocp-Apim-Subscription-Key': api_key,
        'Content-Type': 'application/json'
    },
    params={ 'api-version': '2021-10-01' }
)

# Parse
# -------------------------------------- #

st.header('Parse')

if 'parse_alert' in st.session_state:
    display_alert('parse_alert')

qna_url = st.text_input('Q&A URL')
display_name = st.text_input('Display Name')

def parse_qna():
    if 'job_id' in st.session_state:
        job_id = st.session_state['job_id']
        if job_id != '':
            status_code, _ = get_parse_status(job_id)
            if status_code == 0:
                alert('parse_alert', 'error', 'Still handling previous request')
                return

    if qna_url == '':
        alert('parse_alert', 'error', 'No URL was given')
        return

    data = [
        {
            'op': 'add',
            'value': {
                'displayName': display_name,
                'sourceUri': qna_url,
                'sourceKind': 'url',
                'source': qna_url
            }
        }
    ]

    res = req.patch('sources', data)

    alert('parse_alert', 'info', 'Request sent!')

    if res.status_code != 202:
        alert('parse_alert', 'error', res.reason)
        return

    op_loc = res.headers['operation-location']
    st.session_state['job_id'] = op_loc.split('/')[9].split('?')[0]

st.button('Parse', on_click=parse_qna)

def check_status():
    if 'job_id' not in st.session_state:
        alert('parse_alert', 'error', 'Have not sent any request!')
        return
    job_id = st.session_state['job_id']
    status_code, status_msg = get_parse_status(job_id)
    if status_code == 0:
        alert_type = 'error'
    elif status_code == 1:
        alert_type = 'info'
    else:
        alert_type = 'success'
    alert('parse_alert', alert_type, status_msg)

st.button('Status', on_click=check_status)

# Convert
# -------------------------------------- #

st.header('Convert')

if 'convert_alert' in st.session_state:
    display_alert('convert_alert')

def fetch():
    if 'job_id' in st.session_state:
        job_id = st.session_state['job_id']
        status_code, status_msg = get_parse_status(job_id)

        if status_code == 0:
            alert('convert_alert', 'error', status_msg)
            return
        elif status_code == 1:
            alert('convert_alert', 'warning', 'Still handling previous request')
            return

    res = req.get('qnas', { 'source': qna_url })

    if not res.ok:
        alert('convert_alert', 'error', res.reason)
        return

    st.session_state['origin_qnas'] = res.json()
    alert('convert_alert', 'success', 'Fetched')

st.button('Fetch', on_click=fetch)

if 'origin_qnas' in st.session_state:
    data = st.session_state['origin_qnas']
    preview = { 'value': data['value'][:1] }
    st.text('Preview first element:')
    st.json(preview)

def convert():
    if 'origin_qnas' not in st.session_state:
        alert('convert_alert', 'error', 'Did not fetch first')
        return

    data = st.session_state['origin_qnas']

    converted_data = []
    for qna_set in data['value']:
        for question in qna_set['questions']:
            converted_data.append({
                'prompt': question,
                'completion': qna_set['answer']
            })

    with open('output.json', 'w', encoding='utf8') as f:
        json.dump(converted_data, f, ensure_ascii=False)

    if os.path.isfile('output_prepared.jsonl'):
        os.remove('output_prepared.jsonl')

    os.system('yes | openai tools fine_tunes.prepare_data -f output.json')

    final_data = ''
    with open('output_prepared.jsonl', 'r') as f:
        for line in f:
            final_data += line

    st.session_state['converted_qnas'] = final_data
    alert('convert_alert', 'success', 'Converted')

st.button('Convert', on_click=convert)

if 'converted_qnas' in st.session_state:
    st.caption('*All recommended remedies by `openai` were applied')

    data = st.session_state['converted_qnas']
    preview = data.split('\n')[0]
    st.text('Preview first element')
    st.markdown(f'```json\n{preview}\n```')

    st.download_button(
        label='Download',
        data=data,
        file_name='output_prepared.jsonl',
        mime='application/jsonl'
    )
