from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from parserapp.models import Chat, Category, CategorySubscriber
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json
import re

from . import bot_settings


def parse_command(message):
    pattern = r'/\w+'
    command = re.search(pattern, message)
    if command:
        return command.group()[1:]
    return ''

@method_decorator(csrf_exempt, name='dispatch')
class HomePage(View):
    def post(self, request):
        body_json = json.loads(request.body.decode('utf-8'))
        chat_id = body_json['message']['chat']['id']
        message = body_json['message']['text']
        chat_obj = Chat.objects.get_or_create(telegram_chat_id=int(chat_id))
        command = parse_command(message)
        category = Category.objects.filter(cmd__iexact=command)
        if category:
            try:
                sub = CategorySubscriber.objects.get(chat_id=chat_obj[0].id, category_id=category.values()[0]['id'])
                print("Вы уже подписаны на категорию %s" %(category.values()[0]['name']))
                #send_message(вы уже подписаны!)
            except:
                sub = CategorySubscriber(chat_id=chat_obj[0].id, category_id=category.values()[0]['id'])
                sub.save()
                print ("Вы подписались на категорию %s" %(category.values()[0]['name']))
                #send_message(вы подписались!)
        else:
            print(bot_settings.categories_help)
            #send_message(Доступные команды)

        return JsonResponse({})
