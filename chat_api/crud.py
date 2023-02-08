import json
import requests
import redis
import toml
from requests.adapters import HTTPAdapter, Retry
from main import logger

config = toml.load('config.toml')

redis_client = redis.Redis(host=config['redis']['host'], port=config['redis']['port'], db=0)
token = config['project']['token']
block_user = config['project']['block_user']
wa_instance = config['project']['wa_instance']
api_url = f"https://api.green-api.com/waInstance{wa_instance}/"
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}


def requests_retry_session(
    retries=5,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504, 400, 401, 404),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset({'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PUT', 'TRACE', 'POST'}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def send_message(phone, text):
    if len(phone) == 10:
        phone = '7' + phone
    url = api_url + 'sendMessage/' + token
    payload = {"chatId": phone + '@c.us',
               "message": text}
    try:
        response = requests_retry_session().post(url, headers=headers, data=json.dumps(payload), timeout=120)
        logger.error(f'Отправлено сообщение оператором через omni клиенту {phone} - {response.text} с текстом: {text}')
        return ""
    except Exception as x:
        logger.error('Ошибка отправки сообщения от оператора :(', x.__class__.__name__)
        return ""


def send_client_to_db(phone: str):
    redis_client.set(phone + 'block', '', ex=block_user)
