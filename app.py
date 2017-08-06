# -*- coding: utf-8 -*-
import json
from flask import Flask
from flask import Response
from flask import stream_with_context
from flask import Flask, request, send_from_directory, render_template
from flask import jsonify

import math
import logging
logging.basicConfig()

from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

import s2sphere

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


app = Flask(__name__)

def cell_id_to_json(cellid):
#  cellid = s2sphere.CellId(cellid_l)
  cell = s2sphere.Cell(cellid)

  def get_vertex(v):
    vertex = s2sphere.LatLng.from_point(cell.get_vertex(v))

    return {
      'lat': vertex.lat().degrees,
      'lng': vertex.lng().degrees
    }

  shape = [get_vertex(v) for v in range(0, 4)]
  return {
    'id': str(cellid.id()),
    'id_signed': cellid.id(),
    'token': cellid.to_token(),
    'pos': cellid.pos(),
    'face': cellid.face(),
    'level': cellid.level(),
    'll': {
      'lat': cellid.to_lat_lng().lat().degrees,
      'lng': cellid.to_lat_lng().lng().degrees
    },
    'shape': shape
  }

from functools import wraps
from flask import request, current_app

S2S = "89c259a84,89c259afc,89c2584ac,89c2584b4,89c259abc,89c2584ec,89c258544,89c25855c,89c258554,89c259a94,89c259b14,89c259b0c,89c259a8c,89c259ac4,89c2584cc,89c259a54,89c258564,89c259b34,89c259aa4,89c259b54,89c258ff4,89c258504,89c258524,89c259b74,89c259ad4,89c2584bc,89c25851c,89c25854c,89c2584d4,89c259b2c,89c25853c,89c259b6c,89c259bac,89c259b4c,89c259004,89c2584fc,89c259a9c,89c259a5c,89c2584dc,89c259acc,89c259aac,89c2584c4,89c258ffc,89c259af4,89c259adc,89c259aec,89c259ae4,89c2584e4,89c259ab4,89c259b04,89c259b24,89c258574,89c258514,89c259b5c,89c259074,89c25900c,89c259b44,89c259b64,89c258534,89c258f8c,89c259b1c,89c259b3c,89c25856c,89c25852c,89c25850c"

def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

@app.route('/api/s2cover', methods=['GET', 'POST'])
def s2cover():
    ids = S2S.split(",")
    return jsonify({'cells': [cell_id_to_json(s2sphere.CellId.from_token(id.decode("ascii"))) for id in ids]})
    #return "89c25997,89c25999"

@app.route('/api/s2cells', methods=['GET', 'POST'])
def s2cells():
    import pdb
#    pdb.set_trace()
    ids = request.form["cell_ids"].split(",")
    return jsonify({'cells': [cell_id_to_json(s2sphere.CellId.from_token(id.decode("ascii"))) for id in ids]})
    #return "89c25997,89c25999"
    
@app.route('/api/s2info', methods=['GET', 'POST'])
@jsonp
def s2info():
  # need to make this work for GET and POST
  ids = request.args.get("id") or request.form['id'] or ''
  return jsonify({'cells': [cell_id_to_json(s2sphere.CellId(long(id))) for id in ids.split(',')]})

@nocache
@app.route('/<path:path>')
def send_app(path):
 print 'trying to send ' + path
 return send_from_directory('.', path)

if __name__ == '__main__':
#    print "cellid %s" % s2sphere.CellId.from_token("951977d377e723ab".decode("ascii"))
    app.run(debug=True, use_reloader=True)
