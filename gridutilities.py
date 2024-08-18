from bots.common.settings import settings
import requests


def get_all_sessions():
    sessions = []
    response = requests.get(f'{settings.HUB_URL}/status')
    nodes = response.json()['value']['nodes']

    for node in nodes:
        slots = node.get('slots')
        for slot in slots:
            session = slot.get('session')
            if not session:
                continue
            session_id = session.get('sessionId')
            sessions.append(session_id)

    return sessions

def delete_session(session: str):
    response = requests.delete(f'{settings.HUB_URL}/session/{session}')
    return response.json()

def delete_all_sessions():
    sessions = get_all_sessions()
    for session in sessions:
        delete_session(session)
