from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from parserapp.models import Chat, Category, CategorySubscriber
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json
import re

from parserapp.bot_settings import categories_help
from . import tasks


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
                tasks.send_message.delay(chat_id,  "Вы уже подписаны на категорию %s" %(category.values()[0]['name']))
            except CategorySubscriber.DoesNotExist:
                sub = CategorySubscriber(chat_id=chat_obj[0].id, category_id=category.values()[0]['id'])
                sub.save()
                tasks.send_message.delay(chat_id, "Вы подписались на категорию %s" %(category.values()[0]['name']))

        else:
            tasks.send_message.delay(chat_id, categories_help)

        return JsonResponse({})
