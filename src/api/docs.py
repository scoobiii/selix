from flask import send_from_directory
import os

@app.route('/v1/docs', methods=['GET'])
def api_docs():
    return send_from_directory('/root/selix/docs', 'api_docs.yaml')
