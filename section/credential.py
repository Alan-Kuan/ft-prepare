import streamlit as st
from lib.utils import Req

def CredentialSection(title):
    st.header(title)

    api_key = st.text_input('API Key', type='password')
    endpoint = st.text_input('API Endpoint')
    project = st.text_input('Project Name')

    return Req(
        base_url=f'{endpoint}/language/query-knowledgebases/projects/{project}',
        headers={
            'Ocp-Apim-Subscription-Key': api_key,
            'Content-Type': 'application/json'
        },
        params={ 'api-version': '2021-10-01' }
    )
