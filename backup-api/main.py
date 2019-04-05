from flask import Flask, render_template, request, jsonify,send_file, Response
from werkzeug.utils import secure_filename
from core import Spaces, LoggerConfig
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)
import magic
import logging
import logging.config


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'xlsx', 'docx', 'jpeg', 'gif','png'])
logger_conf = LoggerConfig()
logging.config.dictConfig(logger_conf.get_logger_config())
logger = logging.getLogger(__name__)
spaces = Spaces(logger_conf)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__, instance_relative_config=True)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!

jwt = JWTManager(app)

clients=[{
    'client_app': 'CuroVindico',
    'access_key_id': 'CuroVindico',
    'secret_acces_key': 'CuroVindico'
}]

@app.route('/token', methods=['POST'])
def login():
    print( app.config['JWT_PUBLIC_KEY'])
    access_key_id = request.json.get('access_key_id', None)
    secret_acces_key = request.json.get('secret_acces_key', None)
    client_app = request.json.get('client_app', None)

    client = next((item for item in clients if item.get("client_app") and item["client_app"] == client_app), None)
    
    if client != None:
        if access_key_id != client['access_key_id'] or secret_acces_key != client['secret_acces_key']:
            return jsonify({"msg": "Bad Access Keys"}), 401
    else:
        return jsonify({"msg": "Unregistered Client"}), 401

    # Use create_access_token() and create_refresh_token() to create our
    # access and refresh tokens
    ret = {
        'access_token': create_access_token(identity=client_app),
        'refresh_token': create_refresh_token(identity=client_app)
    }
    return jsonify(ret), 200

@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    client_app = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=client_app)
    }
    return jsonify(ret), 200

@app.route("/api/files/",defaults={'key': None}, methods=['POST'])
@app.route("/api/files/<key>", methods=['GET', 'DELETE'])
@jwt_required
def index(key):
    if request.method == 'POST':
        return "POST"
    elif request.method == 'GET':
        buffer=spaces.get_file(key)
        raw_mtype = magic.from_buffer(buffer, mime=True)
        mtype='application/octet-stream'
        if raw_mtype != None:
            mtype = raw_mtype
        return Response(
            buffer,
            mimetype=mtype,
            headers={"Content-Disposition": "attachment;filename="+key}
        )
    elif request.method == 'DELETE':
        buffer=spaces.delete_file(key)
        return jsonify({'status':'OK'}), 200

    # print("*****************")
    # if request.method == 'POST':
    #     # There is no file selected to upload
    #     if "user_file" not in request.files:
    #         return "No user_file key in request.files"

    #     file = request.files["user_file"]

    #     # There is no file selected to upload
    #     if file.filename == "":
    #         return "Please select a file"

    #     # File is selected, upload to S3 and show S3 URL
    #     if file and allowed_file(file.filename):
    #         file.filename = secure_filename(file.filename)
    #         output = spaces.upload_file(file)
    #         return str(output)
    # else:
    #     return render_template("index.html")