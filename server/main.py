#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sept 11 13:23:10 2020
@author: paper2code
"""
import json

from flask import Flask, jsonify, request

from haystack import Finder
from haystack.indexing.cleaning import clean_wiki_text
from haystack.indexing.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
from haystack.reader.transformers import TransformersReader
from haystack.utils import print_answers

from haystack.database.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever

data  = []
with open("/opt/data/arxiv-metadata-oai.json", 'r') as f:
    for line in f:
        data.append(json.loads(line))

data = pd.DataFrame(data)

document_store = ElasticsearchDocumentStore(host="elastic", username="", password="", index="arxiv-qa")
document_store.write_documents(data[['title', 'abstract']].rename(columns={'title':'name','abstract':'text'}).to_dict(orient='records'))

retriever = ElasticsearchRetriever(document_store=document_store)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True, context_window_size=500)

finder = Finder(reader, retriever)

app = Flask(__name__)

@app.route('/query')
def query():
    question = request.args.get('question')
    prediction = finder.get_answers(question=question, top_k_retriever=10, top_k_reader=2)
    result = print_answers(prediction, details="minimal")
    return jsonify(result)

if "__main__"==__name__:
    app.run(host='0.0.0.0', port='5006')

