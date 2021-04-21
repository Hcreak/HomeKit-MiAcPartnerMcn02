# coding=utf-8

from flask import Flask, request, jsonify, render_template
from sqldata import get_energy_count_month, get_energy_count_day, get_load_power

import decimal
import flask.json
class MyJSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to strings.
            return float(obj)
        return super(MyJSONEncoder, self).default(obj)

app = Flask(__name__)
app.json_encoder = MyJSONEncoder

@app.route('/', methods=['GET'])
def index():
    return render_template("webshow.html")

@app.route('/month', methods=['GET'])
def res_month():
    return jsonify(get_energy_count_month())

@app.route('/day', methods=['GET'])
def res_day():
    return jsonify(get_energy_count_day(request.args['month']))

@app.route('/each', methods=['GET'])
def res_each():
    return jsonify(get_load_power(request.args['day']))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)