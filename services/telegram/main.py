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

import telebot
from telebot import types
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
handler = RotatingFileHandler('../logs/arxiv-tg.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

options = {'Question': 'Ask a question'}

TELEGRAM_ID_ADMIN = os.getenv('TELEGRAM_ID_ADMIN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

keyboard = types.ReplyKeyboardMarkup()
keyboard.row(options['Question'])

def dedup(answers):
    seen = set()
    filtered_answers = []
    for d in answers:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            filtered_answers.append(d)
    return filtered_answers

def get_answer(message):
    answers = requests.get('http://arxiv-qa:5018/query?question='+message.text).json()
    for answer in dedup(answers):
        logger.info('Send answer to %s(%s): %s', message.from_user.first_name, message.from_user.username, answer['answer'])
        bot.send_message(message.chat.id, "Answer: "+ answer['answer'])
        bot.send_message(message.chat.id, "Context: "+ answer['context'])

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Please choose an option', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == options['Question'].lower():
        echo = bot.send_message(chat_id=message.chat.id,
                               text='What would you want me to answer from arxiv knowledge base, sir?')
        bot.register_next_step_handler(message=echo, callback=get_answer)
    else:
        bot.send_message(message.chat.id, 'Sorry, I did not understand this command')

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_ID_ADMIN, text=f'polling {e}')
