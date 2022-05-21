import os
import numpy as np
import json
from multiprocessing import Pool
from flask import Flask, request, render_template, redirect, url_for

from api.file_manager import FileManager
from api.models import Faces, db, MetaData
from api.face_processing import FaceProcessing
from api.heap import Heap

app = Flask(__name__)
# replace postgres:pgh1h2 by your <username>:<password>
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:1234@localhost:5432/face_api"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './static'
app.config['DB_AUTO_COMMIT'] = True

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.mkdir(app.config['UPLOAD_FOLDER'])

db.init_app(app)
db.create_all(app=app)

image_manager = FileManager(app.config['UPLOAD_FOLDER'])
num_processors = 12
face_processor = FaceProcessing()

"""
Routes
"""


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/add_face', methods=['POST', 'GET'])
async def add_face():
    """
    Set input type to be 'file'.
    Form enctype='multipart/form-data'
    Input name for file as 'file'
    Input name for name as 'name'
    """
    if request.method == 'GET':
        return render_template('upload_image.html')
    image = request.files['file']
    name = request.form.get('name')
    assert 'image/' in image.content_type

    # save image to directory
    image_path = image_manager.saveImage(image)
    encoding, num_faces = face_processor.getByteEncoding(image)
    if num_faces > 0:
        img_f = Faces(path=image_path, name=str(name),
                      encoding=encoding, num_faces=num_faces)

        if app.config['DB_AUTO_COMMIT']:
            db.session.add(img_f)
            db.session.commit()
    else:
        return {
            'comments': 'faces not detected'
        }

    # return redirect(url_for('add_face'))
    return {
        'Status': 'Successfully uploaded'
    }, 200


def upload_images(rows):
    """
    Used in multiprocessing to upload images to DB
    """
    uploads = []
    cnt = 0
    for img in rows:
        cnt += 1
        encoding, num_faces = face_processor.getByteEncoding(img[1])
        if num_faces > 0:
            face = Faces(path=img[1], name=img[0],
                         encoding=encoding, num_faces=num_faces)
            uploads.append(face)
    return uploads


@app.route('/add_faces_in_bulk', methods=['POST', 'GET'])
def add_faces_in_bulk():
    """
    Set input type to be 'file'.
    And form enctype='multipart/form-data'
    Input name for file as 'file'
    """
    if request.method == 'GET':
        return render_template('upload_zip.html')
    print(request.files)
    compressed_file = request.files['file']

    # save images to dir
    images, total_images, path = image_manager.saveImagesFromZip(
        compressed_file)

    # split images into batches
    batch_size = int(np.ceil(total_images/num_processors))
    last_batch_size = total_images % batch_size
    batches = [images[-last_batch_size:]]

    for i in range(num_processors-1):
        batches.append(images[i*batch_size:(i+1)*batch_size])

    print('uploading to database....')

    # multiprocessing
    with Pool(num_processors) as p:
        res = p.map(upload_images, batches)

    print('bulk save....')
    if app.config['DB_AUTO_COMMIT']:
        for r in res:
            db.session.bulk_save_objects(r)
        db.session.commit()

    # return redirect(url_for('add_faces_in_bulk'))
    return {
        'Status': 'Successfully uploaded zip file'
    }, 200


@app.route('/search_faces', methods=['GET', 'POST'])
async def search_faces():
    """
    Set input type to be 'file'.
    And form enctype='multipart/form-data'
    Input image name as 'image'
    K parameter as 'k'
    confidence as 'confidence'
    """
    if request.method == 'GET':
        return render_template('search_faces.html')
    rows = Faces.query.all()
    image = request.files['image']
    k = int(request.form.get('k'))
    confidence = float(request.form.get('confidence'))
    assert 'image/' in image.content_type
    assert confidence <= 1 and confidence >= 0

    # get face encoding
    unknown_enc = face_processor.getFaceEncoding(image)
    heap = Heap()

    # search
    for row in rows:
        row: Faces
        known_encoding = np.frombuffer(
            row.encoding, dtype=float).reshape((row.num_faces, 128))
        match, distance = face_processor.compare(
            known_encoding, unknown_enc, 1-confidence)
        if match:
            heap.push({
                'id': row.face_id,
                'person_name': row.name,
                'path': f'file:///{row.path}',
                'distance': distance
            })

    # select top k
    matches = heap.select_k(k)

    return {
        'status': 'OK',
        'body': {
            'matches': matches
        }
    }


@app.route('/get_face_info/', methods=['GET', 'POST'])
def get_face_info():
    """
    And form enctype='multipart/form-data'
    Input name for id as 'id'
    """
    if request.method == 'GET':
        return render_template('get_face_info.html')

    id = None

    if request.content_type == 'application/json':
        id = int(json.loads(request.json).get('id'))
    else:
        id = int(request.form.get('id'))

    if not id:
        return {'Error': 'No ID given'}, 400

    # get face object
    img_obj: Faces = Faces.query.get(id)

    if not img_obj:
        return {'Error': 'No such ID present'}, 400

    # get metadata
    meta: MetaData = MetaData.query.get(id)

    date = None if not meta else meta.date
    location = None if not meta else meta.location
    version = None if not meta else meta.version_number

    link = f"file:///{img_obj.path}"
    result = {
        "id": img_obj.face_id,
        "image_path": link,
        "person_name": img_obj.name,
        'date': date,
        'location': location,
        'version': version
    }

    return result, 200


@app.route('/set_face_info', methods=['GET', 'POST'])
def set_face_info():
    """
    Input name for id as 'id'
    Input name for date as 'date'
    Input name for version as 'version'
    Input name for location as 'location'
    """
    if request.method == 'GET':
        return render_template('set_face_info.html')
    id = None
    date = None
    version = None
    location = None
    if request.content_type == 'application/json':
        id = int(json.loads(request.json).get('id'))
        date = str(json.loads(request.json).get('date'))
        version = str(json.loads(request.json).get('version'))
        location = str(json.loads(request.json).get('location'))
    else:
        id = int(request.form.get('id'))
        date = str(request.form.get('date'))
        version = str(request.form.get('version'))
        location = str(request.form.get('location'))

    # get image 
    img_obj: Faces = Faces.query.get(id)

    if not img_obj:
        return {'Error': 'No such ID present'}, 400

    # get meta data
    meta = MetaData.query.get(id)

    if meta:
        return {'Error': 'Metadata aleady set'}, 200

    metad: MetaData = MetaData(face_id=id, version=version, date=date, location=location)

    db.session.add(metad)
    if app.config['DB_AUTO_COMMIT']:
        db.session.commit()

    return {'STATUS': 'Meta data added'}, 200
