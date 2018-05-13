from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup
import requests
import datetime
from parserapp.bot_settings import url_token

from parserapp import celery_app as app
from parserapp.models import Category, CategorySubscriber, Advert, Chat

def find_subscribers(category_id):
    sub_arr = []
    sub = CategorySubscriber.objects.filter(category_id=category_id).values()
    sub_arr = [s['chat_id'] for s in sub]
    return sub_arr

def initialize_tasks():
    schedule = {}
    categories = Category.objects.all().values()
    for i in categories:
         schedule[i['name']] = {
         'task': 'parserapp.tasks.page_parser',
         'schedule': datetime.timedelta(seconds=60),
         'args': (i['id'],)
         }
    schedule['telegram_sender'] = {
        'task': 'parserapp.tasks.find_new_ads',
         'schedule': datetime.timedelta(seconds=60),
         'args': None
    }
    app.conf.update(CELERYBEAT_SCHEDULE=schedule)

def price_check(price):
    try:
        return price.text
    except:
        pass
    return ""

@app.task
def find_new_ads():
    sub = Advert.objects.filter(is_sent=False, \
    category__categorysubscriber__chat_id__isnull=False)\
    .values('category__categorysubscriber__chat__telegram_chat_id', \
    'title', 'price')

    for s in sub:
        text = '%s %s' %(s['title'], s['price'])
        send_message.delay(s['category__categorysubscriber__chat__telegram_chat_id'], text)
    sub.update(is_sent=True)


@app.task
def send_message(chat_id, text):
    URL = url_token + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(URL, json=answer)
    return r.json()



@app.task
def page_parser(category_id):
    ads = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
    category_url = Category.objects.get(id=category_id).url
    url = "https://www.avito.ru/rostov-na-donu/%s?s=104&view=list" %(category_url)
    req = requests.get(url, headers=headers)
    page_text = req.text.encode('utf8')
    soup = BeautifulSoup(page_text)
    results = soup.find_all('div', {'class': 'js-catalog-item-enum'})
    for item in results:
        price_class = item.find('div', {'class': 'price'})
        price = price_class.find('span', {'class': 'c-2'})

        if price:
            price_text = price.text
        else:
            price_text = price_class.find('p').text

        title_class = item.find('div', {'class': 'description-title'}).find('a')
        title_text = title_class['title']
        title_id = title_class['id']
        title_href = "https://www.avito.ru/" + title_class['href']

        ads.append({
        'avito_id': title_class['id'],
        'title': "%s. Ссылка - %s" %(title_text, title_href),
        'price': price_text
        })

    filter_ads(ads, category_id)

def filter_ads(ads_dict, category_id):
    avito_ids = [int(a['avito_id']) for a in ads_dict]
    adverts = Advert.objects.filter(category_id=category_id, avito_id__in=avito_ids).values()
    sent_ads = [a['avito_id'] for a in adverts]
    res = list(set(avito_ids) - set(sent_ads))
    for item in ads_dict:
        if int(item['avito_id']) in res:
            new_ad = Advert(avito_id=item['avito_id'], category_id=category_id,\
                            title=item['title'], price=item['price'])
            new_ad.save()

initialize_tasks()
