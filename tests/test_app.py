from fastapi.testclient import TestClient

from main import app
from quiz_module import clean_json_block

client = TestClient(app)


def test_home_page():
    response = client.get('/')
    assert response.status_code == 200
    assert 'EduGenie' in response.text


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_validation_rejects_empty_text():
    response = client.post('/qa', json={'text': ''})
    assert response.status_code == 422


def test_clean_json_block():
    raw = '```json\n{"questions": []}\n```'
    assert clean_json_block(raw) == '{"questions": []}'
