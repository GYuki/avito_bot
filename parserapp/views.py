from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from parserapp.models import Chat, Category, CategorySubscriber
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json
import re
# Create your views here.

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
        command = parse_command(message)
        print (chat_id, command)
        return JsonResponse({})
