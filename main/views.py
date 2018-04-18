import time

import json

from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from main.external_api import telegram_api, trello_api


def send_message_to_telegram(telegram_user_id, text):
    return telegram_api.call(
        'sendMessage',
        data={
            'chat_id': telegram_user_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }
    )


@csrf_exempt
def telegram_webhook(request):
    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    if not data.get('message'):
        return HttpResponse()

    telegram_user_id = data['message']['from']['id']

    try:
        voice = data['message']['voice']
    except KeyError:
        send_message_to_telegram(telegram_user_id, 'This bot is expecting only voice messages')
        return HttpResponse()

    try:
        voice_file_path = telegram_api.call(
            'getFile',
            data={
                'file_id': voice['file_id'],
            }
        ).json()['result']['file_path']
    except (ValueError, KeyError):
        send_message_to_telegram(telegram_user_id, 'Failed to get info about voice file')
        return HttpResponse()

    try:
        voice_file = telegram_api.get_file(voice_file_path)
    except:
        send_message_to_telegram(telegram_user_id, 'Failed to get file')
        return HttpResponse()

    list_id = settings.TRELLO_LIST_ID

    filename = str(int(time.time()))

    try:
        response = trello_api.call(
            'post',
            'cards',
            data={
                'name': filename,
                'idList': list_id
            }
        )
    except ValueError:
        send_message_to_telegram(telegram_user_id, 'Failed to create card')
        return HttpResponse()

    card_url = response.get('url')

    try:
        trello_api.call(
            'post',
            'cards',
            response['id'],
            'attachments',
            files={
                'file': (filename + '.ogg', voice_file.content, voice['mime_type'])}
        )
    except ValueError:
        send_message_to_telegram(telegram_user_id, 'Failed to upload file to trello')
        return HttpResponse()

    send_message_to_telegram(telegram_user_id, 'Card created.\n{}'.format(card_url))

    return HttpResponse()
