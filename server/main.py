#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sept 11 13:23:10 2020
@author: paper2code
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/query')
def torch():
    id = request.args.get('q')
    return jsonify(id)


if "__main__"==__name__:
    app.run(host='0.0.0.0', port='5006')

