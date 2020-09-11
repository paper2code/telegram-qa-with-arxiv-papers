#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sept 11 13:23:10 2020
@author: paper2code
"""
import os
import json

import click

import tqdm
import numpy as np  # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import telebot
from telebot import types

from data import get_stats, get_image_link

from flask import Flask, jsonify, request

from haystack import Finder
from haystack.indexing.cleaning import clean_wiki_text
from haystack.indexing.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
from haystack.reader.transformers import TransformersReader
from haystack.utils import print_answers

from haystack.database.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever

options = {'Question': 'Ask a question', 'Statistics': 'Statistics of the current db'}

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

keyboard = types.ReplyKeyboardMarkup()
keyboard.row(options['Question'], options['Statistics'])

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Please choose an option', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == options['Statistics'].lower():
        bot.send_message(message.chat.id, 'Processing...')
        bot.send_message(message.chat.id, get_stats(), parse_mode="Markdown")
    elif message.text.lower() == options['Languages'].lower():
        bot.send_message(message.chat.id, 'Processing...')
        bot.send_photo(message.chat.id, get_image_link())
    elif message.text.lower() == options['URL'].lower():
        bot.send_message(message.chat.id, f'Site URL - https://paper2code.com')
    else:
        bot.send_message(message.chat.id, 'Sorry, I did not understand this command')
        # bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIBkl6pr4kVOGisB5LUX54w8USsN6hWAAL5AANWnb0KlWVuqyorGzYZBA')



data  = []
with tqdm.tqdm(total=os.path.getsize("../data/arxiv-metadata-oai.json")) as pbar:
    with open("../data/arxiv-metadata-oai.json", 'r') as f:
        for line in f:
            # pbar.update(f.tell() - pbar.n)
            pbar.update(len(line))
            data.append(json.loads(line))

data = pd.DataFrame(data)


document_store = ElasticsearchDocumentStore(host="elastic", username="", password="", index="arxiv-qa")
document_store.write_documents(data[['title', 'abstract']].rename(columns={'title':'name','abstract':'text'}).to_dict(orient='records'))

retriever = ElasticsearchRetriever(document_store=document_store)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True, context_window_size=500)

finder = Finder(reader, retriever)

app = Flask(__name__)

# Local
# bot.remove_webhook()
# bot.polling(none_stop=True)

@app.route('/query')
def query():
    question = request.args.get('question')
    prediction = finder.get_answers(question=question, top_k_retriever=10, top_k_reader=2)
    result = print_answers(prediction, details="minimal")
    return jsonify(result)

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '!', 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://paper2code.com/qa/?token=" + TELEGRAM_TOKEN)
    return "!", 200

@click.command()
@click.option("--host", default="0.0.0.0", help="Server host.")
@click.option("--port", default="5006", help="The person to greet.")
def server(host, port):
    """Run the paper2code arXiv-QA server."""
    app.run(host=host, port=port)

if __name__ == '__main__':
    server()
