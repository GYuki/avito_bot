from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup
import requests
import datetime

from parserapp import celery_app as app
from parserapp.models import Category, CategorySubscriber

def find_subscribers(category_id):
    sub_arr = []
    sub = CategorySubscriber.objects.filter(category_id=category_id).values()
    sub_arr = [s['chat_id'] for s in sub]
    return sub_arr

price_check = lambda x: x.text if x is not None else 'Цена не указана'
"""
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    categories = Category.objects.all()
    print (categories)
    for c in [0,1,2]:
        sender.add_periodic_task(10.0, page_parser.s(c['id']), name=c['cmd'])
"""
@app.task
def page_parser(category_id):
    #category_url = Category.objects.get(id=category).url
    category_url='rabota'
    url = "https://www.avito.ru/rostov-na-donu/%s" %(category_url)
    req = requests.get(url)
    page_text = req.text.encode('utf8')
    soup = BeautifulSoup(page_text)
    results = soup.find_all('div', {'class': 'js-catalog-item-enum'})
    ads = [
        {
        'avito_id': r['id'][1:],
        'title': r.find('a', {'class': 'item-description-title-link'}).text,
        'price': price_check(r.find('a', {'class': 'about '}))
        } for r in results]
    print (ads)

app.conf.update(
    CELERYBEAT_SCHEDULE={
        'parse-each-10-seconds': {
            'task': 'parserapp.tasks.page_parser',
            'schedule': datetime.timedelta(seconds=3),
            'args': (1,)
        },
    },
)
