import pytest
from main import app
import json


@pytest.fixture
def start():
    app.testing = True
    app.config['DB_AUTO_COMMIT'] = False


def test_image_search(start):
    with app.test_client() as client:
        values = {'k': 4, 'confidence': 0.5, 'image': open(
            './testing_articles/collin_powell/download_1.jpg', 'rb')}
        resp = client.post('/search_faces', data=values)
        response = json.loads(resp.data)
        print(response)
        assert resp.status_code == 200
        assert len(response['body']['matches']) > 0


def test_zip_upload(start):
    with app.test_client() as client:
        values = {'file': open(
            './testzip.zip', 'rb')}
        resp = client.post('/add_faces_in_bulk', data=values)
        assert resp.status_code == 200


def test_image_upload(start):
    with app.test_client() as client:
        values = {
            'name': 'Collin_Powell',
            'file': open('testing_articles/collin_powell/download_1.jpg', 'rb')}
        resp = client.post('/add_face', data=values)
        assert resp.status_code == 200

def test_get_info(start):
    with app.test_client() as client:
        values = {'id': 250}
        resp = client.post('/get_face_info/', json=json.dumps(values))
        print(resp.data)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get('id')
        assert data.get('image_path')
        assert data.get('person_name')

def test_set_info(start):
    with app.test_client() as client:
        values = {'id': 30,'date':'1/2/2000','version':2, 'location':'usa'}
        resp = client.post('/set_face_info', json=json.dumps(values))
        print(resp.data)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        print(data)