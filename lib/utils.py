from dataclasses import dataclass
import streamlit as st
import requests

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

def get_parse_status(job_id, req):
    res = req.get(f'sources/jobs/{job_id}')
    if not res.ok:
        return 0, res.reason
    data = res.json()
    status_code = 2 if data['status'] == 'succeeded' else 1
    return status_code, data['status']

