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

import telebot
from telebot import types
import requests

options = {'Question': 'Ask a question', 'Statistics': 'Statistics of the current db'}

TELEGRAM_ID_ADMIN = os.getenv('TELEGRAM_ID_ADMIN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

keyboard = types.ReplyKeyboardMarkup()
keyboard.row(options['Question'], options['Statistics'])

def get_answer(q):
    answers = requests.get('http://arxiv-qa:5018/query?question='+q).json()
    return answers

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Please choose an option', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == options['Question'].lower():
        # bot.send_message(message.chat.id, 'Processing...')
        answers = get_answer(message.text)
        for answer in answers:
            print(answer['context'])
            bot.send_message(message.chat.id, answer['context'])
    # elif message.text.lower() == options['Statistics'].lower():
    #     bot.send_message(message.chat.id, 'Processing...')
    #     bot.send_message(message.chat.id, get_stats(), parse_mode="Markdown")
    # elif message.text.lower() == options['Languages'].lower():
    #     bot.send_message(message.chat.id, 'Processing...')
    #     bot.send_photo(message.chat.id, get_image_link())
    # elif message.text.lower() == options['URL'].lower():
    #     bot.send_message(message.chat.id, f'Site URL - https://paper2code.com')
    else:
        bot.send_message(message.chat.id, 'Sorry, I did not understand this command')
        # bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIBkl6pr4kVOGisB5LUX54w8USsN6hWAAL5AANWnb0KlWVuqyorGzYZBA')

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_ID_ADMIN, text=f'polling {e}')
