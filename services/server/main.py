#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sept 11 13:23:10 2020
@author: paper2code
"""
import os
import json

import logging
from logging.handlers import RotatingFileHandler

import click

import tqdm
import numpy as np  # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

from flask import Flask, jsonify, request

from haystack import Finder
from haystack.indexing.cleaning import clean_wiki_text
from haystack.indexing.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
from haystack.reader.transformers import TransformersReader
from haystack.utils import print_answers

from haystack.database.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever

document_store = ElasticsearchDocumentStore(host="elasticsearch", username="", password="", index="arxiv-qa")

def filter_answers(results: dict, details: str = "all"):
    answers = results["answers"]
    if details != "all":
        if details == "minimal":
            keys_to_keep = set(["answer", "context"])
        elif details == "medium":
            keys_to_keep = set(["answer", "context", "score"])
        else:
            keys_to_keep = answers.keys()

        # filter the results
        filtered_answers = []
        for ans in answers:
            filtered_answers.append({k: ans[k] for k in keys_to_keep})
        return filtered_answers
    else:
        return results

def train_model(input_file='../data/arxiv-metadata-oai.json'):
    print("training the model...")
    data  = []
    with tqdm.tqdm(total=os.path.getsize(input_file)) as pbar:
        with open(input_file, 'r') as f:
            for line in f:
                pbar.update(len(line))
                data.append(json.loads(line))
    data = pd.DataFrame(data)
    document_store.write_documents(data[['title', 'abstract']].rename(columns={'title':'name','abstract':'text'}).to_dict(orient='records'))

retriever = ElasticsearchRetriever(document_store=document_store)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True, context_window_size=500)
finder = Finder(reader, retriever)

app = Flask(__name__)

@app.route('/query')
def query():
    question = request.args.get('question')
    prediction = finder.get_answers(question=question, top_k_retriever=20, top_k_reader=1)
    result = filter_answers(prediction, details="minimal")
    app.logger.info('question: %s', question)
    app.logger.info('result: %s', result)
    return jsonify(result)

@click.command()
@click.option("--host", default="0.0.0.0", help="Server host.")
@click.option("--port", default="5006", help="Server port.")
@click.option("--train", default=False, is_flag=True, help="Train the model.")
def service(host, port, train):
    """Run the paper2code arXiv-QA server."""
    if train:
        train_model()
    handler = RotatingFileHandler('../logs/arxiv-qa.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host=host, port=port)

if __name__ == '__main__':
    service()
