from flask import Flask, request
import redis
import json

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6457, db=0)

# set方法
@app.route('/set', methods=['POST'])
def set_redis():
    key = request.form['key']
    value = request.form['value']
    r.set(key, value)
    return 'Set successfully'

# get方法
@app.route('/get', methods=['GET'])
def get_redis():
    key = request.args.get('key')
    value = r.get(key)
    if value is None:
        return 'Key not found'
    else:
        return value.decode('utf-8')

# exists方法
@app.route('/exists', methods=['GET'])
def exists_redis():
    key = request.args.get('key')
    if r.exists(key):
        return 'Key exists'
    else:
        return 'Key not found'

if __name__ == '__main__':
    app.run(debug=True)
