from celery import shared_task
import requests
from celery.utils.log import get_task_logger
import plotly.graph_objects as go
import plotly
from django.core.mail import EmailMessage
from django.conf import settings
import plotly.io as pio
import os

logger = get_task_logger(__name__)


def get_covid_data(user, country_code=None, date_range=None):
    if not country_code:
        country_code=user.country_code.code
    if not date_range:
        date_range=15
    r = requests.get('http://corona-api.com/countries/{}'.format(country_code))
    response = r.json()
    timeline = response['data']['timeline'][:int(date_range)]
    response['data']['timeline'] = timeline
    return response


@shared_task
def test_task_job():
    logger.info("celery working")
    return None


@shared_task()
def send_data_email(data, to_email):
    fig=go.Figure()
    values = []
    dates = []
    names = ['deaths', 'confirmed', 'recovered', 'new_confirmed', 'new_recovered', 'new_deaths', 'active']
    for i in data.get('data',{}).get('timeline',[]):
        dates.append(i.get('date'))
        values.append([i.get('deaths'), i.get('confirmed'), i.get('recovered'), i.get('new_confirmed'), i.get('new_recovered'), i.get('new_deaths'), i.get('active')])
    
    for i, j in enumerate(values[:7]):
        fig.add_traces(go.Bar(x=dates[:7], y=j, name = names[i]))
    logger.info("usage report created for")
    
    if not os.path.exists("images"):
        os.mkdir("images")
    
    fig.write_image("images/fig1.jpeg")
    
    email = EmailMessage(
        'Covid data',
        '<strong>We have attached data in foam of chart. Please find it attached. Thank You</strong>',
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
    )
    email.attach_file('images/fig1.jpeg')
    email.content_subtype = "html"
    email.send()
    os.remove('images/fig1.jpeg')
    return
    
