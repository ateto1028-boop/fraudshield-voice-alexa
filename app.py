"""FraudShield Voice — a clearly labeled simulated Alexa+ experience."""
import json
import streamlit as st
from engine import EXAMPLES
from agentic import triage, follow_up_advice
st.set_page_config(page_title='FraudShield Voice • Alexa+ Simulation', page_icon='🛡️', layout='centered')
st.title('🛡️ FraudShield Voice')
st.caption('Alexa+–style simulated experience · Hackathon prototype · No Amazon/Alexa connection')
st.info('This is an independently built *simulation*, not an official Amazon Alexa+ skill. It is a rule-based tool-using agent, not a trained AI model.')

with st.sidebar:
    st.header('About the demo')
    st.write('1. Choose a sample or paste a suspicious message.\n\n2. Ask the simulated assistant to inspect it.\n\n3. Review the tools, risk signals and safety guidance.')
    st.warning('For education only. A low score does not mean a message is safe. Do not paste passwords, codes, or private financial data.')
    st.caption('No API keys, cloud services, paid accounts, or external URL fetches.')

if 'chat' not in st.session_state:
    st.session_state.chat = []
if 'sample' not in st.session_state:
    st.session_state.sample = EXAMPLES['Code theft attempt']

st.subheader('Voice assistant simulation')
st.markdown('**You:** “Alexa, ask FraudShield whether this message looks suspicious.”')
selected = st.selectbox('Demo scenarios', ['Write my own message'] + list(EXAMPLES), index=3)
default = st.session_state.sample if selected == 'Write my own message' else EXAMPLES[selected]
message = st.text_area('Message or URL to inspect', value=default, height=130, max_chars=8000)
run = st.button('🔎 Ask FraudShield', type='primary', use_container_width=True)
if run:
    result = triage(message)
    if 'error' in result:
        st.error(result['error'])
    else:
        st.session_state.chat.insert(0, {'user': message, 'result': result})

if st.session_state.chat:
    latest = st.session_state.chat[0]
    report = latest['result']
    st.markdown('### Simulated Alexa+ response')
    if report['risk_level'] == 'High':
        st.error(f"Potential scam warning: {report['risk_level']} risk ({report['risk_score']}/100)")
    elif report['risk_level'] == 'Medium':
        st.warning(f"Proceed cautiously: {report['risk_level']} risk ({report['risk_score']}/100)")
    else:
        st.success(f"No strong predefined indicators: {report['risk_level']} risk ({report['risk_score']}/100)")
    st.markdown('**Assistant:** “I inspected your message for suspicious requests and link patterns. Here is what I found.”')
    st.progress(report['risk_score'] / 100)
    st.markdown('**Signals identified**')
    for item in report['signals']:
        st.write('• ' + item)
    st.markdown('**Recommended next steps**')
    for item in report['actions']:
        st.write('• ' + item)
    with st.expander('Agent tool trace — see what executed'):
        for i, tool in enumerate(report['tools_called'], 1):
            st.code(f'{i}. {tool}(...)')
        st.json({'links_detected': report['links_detected'], 'scope': report['scope']})
    st.markdown('**Follow-up conversation (optional)**')
    question = report.get('follow_up')
    if question:
        st.write(question['question'])
        answer = st.radio('Choose an answer (do not enter sensitive information)',
                          question['choices'], key=f"followup_{len(st.session_state.chat)}_{report['agent_route']}")
        st.info(follow_up_advice(report, answer))
    st.download_button('Download analysis as JSON' , json.dumps(report, indent=2), file_name='fraudshield_analysis.json', mime='application/json')

st.divider()
st.caption('Prototype built for Build, Ship, Shape: Amazon Developer Hackathon 2026 · Alexa+ simulated-experience route.')
st.caption('No real Alexa device, Amazon SDK, MCP runtime or third-party threat intelligence is used in this version.')
