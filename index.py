import streamlit as st
from section.credential import CredentialSection
from section.parse import ParseSection
from section.convert import ConvertSection

app_name = 'ft-prepare'

st.set_page_config(
    page_title=app_name
)

st.title(app_name)

req = CredentialSection('Cognitive Services Credentials')
qna_url = ParseSection('Parse', req)
ConvertSection('Convert', qna_url, req)
