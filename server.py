from flask import Flask, request, Response
from utils import read_data, check_data, update_data


app = Flask(__name__)


@app.route('/api/<string:dev_id>', methods=['GET'])
def get(dev_id):
    if request.get_json():
        try:
            current_status = read_data(dev_id)
            resp = Response(current_status, status=200)
        except FileNotFoundError:
            resp = Response(status=404)
    else:
        resp = Response(status=404)
    return resp

@app.route('/api/<string:dev_id>', methods=['POST'])
def post(dev_id):
    data = request.get_json()
    if data:
        is_valid = check_data(dev_id, data)
    else:
        is_valid = False
    if is_valid:
        update_data(dev_id, data)
        resp = Response("Updated", status=200)
    else:
        resp = Response(status=404)
    return resp


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4465, debug=False)
    
    
        
