from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup
import requests
import datetime

from parserapp import celery_app as app
from parserapp.models import Category, CategorySubscriber, Advert

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
         'schedule': datetime.timedelta(seconds=20),
         'args': (i['id'],)
         }
    app.conf.update(CELERYBEAT_SCHEDULE=schedule)

def price_check(price):
    try:
        return price.text
    except:
        pass
    return ""



@app.task
def page_parser(category_id):
    category_url = Category.objects.get(id=category_id).url
    url = "https://www.avito.ru/rostov-na-donu/%s" %(category_url)
    req = requests.get(url)
    page_text = req.text.encode('utf8')
    soup = BeautifulSoup(page_text)
    results = soup.find_all('div', {'class': 'js-catalog-item-enum'})
    ads = [
        {
        'avito_id': r['id'][1:],
        'title': r.find('a', {'class': 'item-description-title-link'}).text,
        'price': price_check(r.find('div', {'class': 'about '}))
        } for r in results]
    filter_ads(ads, category_id)

def filter_ads(ads_dict, category_id):
    avito_ids = [int(a['avito_id']) for a in ads_dict]
    adverts = Advert.objects.filter(category_id=category_id, avito_id__in=avito_ids).values()
    sent_ads = [a['avito_id'] for a in adverts]
    res = list(set(avito_ids) - set(sent_ads))
    for item in ads_dict:
        if int(item['avito_id']) in res:
            print (item['price'])
            new_ad = Advert(avito_id=item['avito_id'], category_id=category_id,\
                            title=item['title'], price=item['price'])
            new_ad.save()

initialize_tasks()
