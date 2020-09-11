from datetime import date
import requests

def get_stats():
    latest_stats = requests.get('https://qa-skills.herokuapp.com/get_statistics').json()
    stats = '\n'.join([f"{stat['title']} - {stat['count']} ({stat['percent']})" for stat in latest_stats['stats']])
    positions = '\n'.join([f"{position['title']} - {position['count']}" for position in latest_stats['positions']])
    ways = '\n'.join([f"{way['title']} - {way['count']}" for way in latest_stats['ways']])
    text = '\n\n'.join([f'*Statistics by day*: \n{stats}',
                        f'*Positions by day*: \n{positions}',
                        f'*Ways by day*: \n{ways}',
                        f'More info you can find [here](https://qa-skills.herokuapp.com)'])
    return text

def get_image_link():
    # To make sure image created
    trigger_image = requests.get('https://qa-skills.herokuapp.com/get_language_comparison').json()
    url = trigger_image['image'].replace('/app', 'https://qa-skills.herokuapp.com')
    return url
