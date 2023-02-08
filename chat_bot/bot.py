import logging
from transitions import Machine
import redis
import requests
import json
import toml
from languages import all_languages
from requests.adapters import HTTPAdapter, Retry
import pickle

logging.basicConfig(filename='errors.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)

logger = logging.getLogger(__name__)


def requests_retry_session(
    retries=5,
    backoff_factor=1,
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


class Client:
    steps = {
        "s0": [all_languages,
               {"1": "s0_1", "2": "s0_2", "3": "s0_3", "4": "s0_4", "5": "s0_5", "6": "s0_6", "7": "s0_7",
                "8": "s0_8", "9": "s0_9", "10": "s0_10", "11": "s0_11"}],
        "s0_1": [all_languages, {"1": "s0_1_1", "2": "s0_1_2", "3": "s0"}],
        "s0_1_1": [all_languages, {"1": "s0"}],
        "s0_1_2": [all_languages, {"1": "s0"}],
        "s0_2": [all_languages, {"1": "s0_2_1", "2": "s0"}],
        "s0_2_1": [all_languages, {"1": "s0"}],
        "s0_3": [all_languages, {"1": "s0_3_1", "2": "s0_3_2", "3": "s0"}],
        "s0_3_1": [all_languages, {"1": "s0_3_1_1", "2": "s0_3_1_2", "3": "s0_3_1_3", "4": "s0_3_1_4", "5": "s0_3_1_5",
                                   "6": "s0_3_1_6", "7": "s0_3_1_7", "8": "s0_3_1_8", "9": "s0_3_1_9",
                                   "10": "s0_3_1_10",
                                   "11": "s0_3_1_11", "12": "s0_3_1_12", "13": "s0_3_1_13", "14": "s0_3_1_14",
                                   "15": "s0_3_1_15", "16": "s0_3_1_16", "17": "s0_3_1_17", "18": "s0_3_1_18",
                                   "19": "s0_3_1_19", "20": "s0_3_1_20", "21": "s0_3_1_21"}],
        "s0_3_1_1": [all_languages, {"1": "s0"}],
        "s0_3_1_2": [all_languages, {"1": "s0"}],
        "s0_3_1_3": [all_languages, {"1": "s0"}],
        "s0_3_1_4": [all_languages, {"1": "s0"}],
        "s0_3_1_5": [all_languages, {"1": "s0"}],
        "s0_3_1_6": [all_languages, {"1": "s0"}],
        "s0_3_1_7": [all_languages, {"1": "s0"}],
        "s0_3_1_8": [all_languages, {"1": "s0"}],
        "s0_3_1_9": [all_languages, {"1": "s0"}],
        "s0_3_1_10": [all_languages, {"1": "s0"}],
        "s0_3_1_11": [all_languages, {"1": "s0"}],
        "s0_3_1_12": [all_languages, {"1": "s0"}],
        "s0_3_1_13": [all_languages, {"1": "s0"}],
        "s0_3_1_14": [all_languages, {"1": "s0"}],
        "s0_3_1_15": [all_languages, {"1": "s0"}],
        "s0_3_1_16": [all_languages, {"1": "s0"}],
        "s0_3_1_17": [all_languages, {"1": "s0"}],
        "s0_3_1_18": [all_languages, {"1": "s0"}],
        "s0_3_1_19": [all_languages, {"1": "s0"}],
        "s0_3_1_20": [all_languages, {"1": "s0"}],
        "s0_3_1_21": [all_languages, {"1": "s0"}],
        "s0_3_2": [all_languages, {"1": "s0"}],
        "s0_4": [all_languages, {"1": "s0_4_1", "2": "s0_4_2"}],
        "s0_4_1": [all_languages, {"1": "s0_4_1_1", "2": "s0"}],
        "s0_4_1_1": [all_languages, {"1": "s0_3_1", "2": "s0_3_2", "3": "s0"}],
        "s0_4_2": [all_languages, {"1": "s0_3_1", "2": "s0_3_2", "3": "s0"}],
        "s0_5": [all_languages, {"1": "s0"}],
        "s0_6": [all_languages, {"1": "s0"}],
        "s0_7": [all_languages, {"1": "s0"}],
        "s0_8": [all_languages, {"1": "s0"}],
        "s0_9": [all_languages, {"1": "s0_3_1_1", "2": "s0_3_1_2", "3": "s0_3_1_3", "4": "s0_3_1_4", "5": "s0_3_1_5",
                                 "6": "s0_3_1_6", "7": "s0_3_1_7", "8": "s0_3_1_8", "9": "s0_3_1_9", "10": "s0_3_1_10",
                                 "11": "s0_3_1_11", "12": "s0_3_1_12", "13": "s0_3_1_13", "14": "s0_3_1_14",
                                 "15": "s0_3_1_15",
                                 "16": "s0_3_1_16", "17": "s0_3_1_17", "18": "s0_3_1_18", "19": "s0_3_1_19",
                                 "20": "s0_3_1_20",
                                 "21": "s0_3_1_21"}],
        "s0_10": [all_languages, {"1": "s0"}],
        "s0_11": [all_languages,
                  {"1": "s0_11_1", "2": "s0_11_1", "3": "s0_11_1", "4": "s0_11_1", "5": "s0_11_1", "6": "s0_11_1",
                   "7": "s0_11_1", "8": "s0_11_1"}],
        "s0_11_1": [all_languages, {"1": "s0"}],
    }

    states = list(steps.keys())

    def __init__(self, phone):
        self.state = None
        self.language = '1'
        self.prev_state = 's0'
        self.phone = phone
        self.machine = Machine(model=self, states=Client.states, initial='s0_11')
        self.machine.add_transition('s0', '*', 's0')
        self.machine.add_transition('s0_1', 's0', 's0_1')
        self.machine.add_transition('s0_2', 's0', 's0_2')
        self.machine.add_transition('s0_3', 's0', 's0_3')
        self.machine.add_transition('s0_4', 's0', 's0_4')
        self.machine.add_transition('s0_5', 's0', 's0_5')
        self.machine.add_transition('s0_6', 's0', 's0_6')
        self.machine.add_transition('s0_7', 's0', 's0_7')
        self.machine.add_transition('s0_8', 's0', 's0_8')
        self.machine.add_transition('s0_9', 's0', 's0_3_1')
        self.machine.add_transition('s0_10', 's0', 's0_10')
        self.machine.add_transition('s0_11', 's0', 's0_11')
        self.machine.add_transition('s0_1_1', 's0_1', 's0_1_1')
        self.machine.add_transition('s0_1_2', 's0_1', 's0_1_2')
        self.machine.add_transition('s0_2_1', 's0_2', 's0_2_1')
        self.machine.add_transition('s0_3_1', 's0_3', 's0_3_1')
        self.machine.add_transition('s0_3_2', 's0_3', 's0_3_2')
        self.machine.add_transition('s0_3_1_1', 's0_3_1', 's0_3_1_1')
        self.machine.add_transition('s0_3_1_2', 's0_3_1', 's0_3_1_2')
        self.machine.add_transition('s0_3_1_3', 's0_3_1', 's0_3_1_3')
        self.machine.add_transition('s0_3_1_4', 's0_3_1', 's0_3_1_4')
        self.machine.add_transition('s0_3_1_5', 's0_3_1', 's0_3_1_5')
        self.machine.add_transition('s0_3_1_6', 's0_3_1', 's0_3_1_6')
        self.machine.add_transition('s0_3_1_7', 's0_3_1', 's0_3_1_7')
        self.machine.add_transition('s0_3_1_8', 's0_3_1', 's0_3_1_8')
        self.machine.add_transition('s0_3_1_9', 's0_3_1', 's0_3_1_9')
        self.machine.add_transition('s0_3_1_10', 's0_3_1', 's0_3_1_10')
        self.machine.add_transition('s0_3_1_11', 's0_3_1', 's0_3_1_11')
        self.machine.add_transition('s0_3_1_12', 's0_3_1', 's0_3_1_12')
        self.machine.add_transition('s0_3_1_13', 's0_3_1', 's0_3_1_13')
        self.machine.add_transition('s0_3_1_14', 's0_3_1', 's0_3_1_14')
        self.machine.add_transition('s0_3_1_15', 's0_3_1', 's0_3_1_15')
        self.machine.add_transition('s0_3_1_16', 's0_3_1', 's0_3_1_16')
        self.machine.add_transition('s0_3_1_17', 's0_3_1', 's0_3_1_17')
        self.machine.add_transition('s0_3_1_18', 's0_3_1', 's0_3_1_18')
        self.machine.add_transition('s0_3_1_19', 's0_3_1', 's0_3_1_19')
        self.machine.add_transition('s0_3_1_20', 's0_3_1', 's0_3_1_20')
        self.machine.add_transition('s0_3_1_21', 's0_3_1', 's0_3_1_21')
        self.machine.add_transition('s0_4_1', 's0_4', 's0_4_1')
        self.machine.add_transition('s0_4_2', 's0_4', 's0_3')
        self.machine.add_transition('s0_4_1_1', 's0_4_1', 's0_3')
        self.machine.add_transition('s0_11_1', 's0_11', 's0', before='change_language')

    def get_state_text(self):
        return Client.steps[self.state][0].get(self.state)[int(self.language) - 1]

    def change_state(self, answer):
        eval(f'self.{self.steps[self.state][1].get(answer)}(language={answer})')

    def change_language(self, language):
        self.language = language


class OmnideskIntegration:
    """Integration with the Omnidesk service"""

    with open('config.toml', mode="r", encoding="utf-8") as conf_file:
        config = toml.load(conf_file)

    def __init__(self):
        self.auth = (self.config['omnidesk']['login'], self.config['omnidesk']['token'])
        self.domain = self.config['omnidesk']['domain']
        self.login = self.config['omnidesk']['login']
        self.token = self.config['omnidesk']['token']
        self.channel = self.config['omnidesk']['channel']
        self.user_id = None
        self.case_id = None
        self.phone = None
        self.nickname = None
        self.headers = {'Content-Type': 'application/json'}

    def create_case(self, phone, nickname, text):
        """Creating a user case if it does not exist"""

        url = f"https://{self.domain}.omnidesk.ru/api/cases.json/"
        payload = {"case": {
            "channel": self.channel,
            "subject": phone,
            "content": text,
            "status": "open",
            "user_custom_id": phone,
            "user_phone": phone,
            "user_full_name": nickname}}
        try:
            response = requests.post(url, headers=self.headers, auth=self.auth, data=json.dumps(payload))
            response = response.json()
            self.user_id = response['case']['user_id']
            self.case_id = response['case']['case_id']
            self.phone = phone
            self.nickname = nickname
        except:
            logger.error(f"Ошибка создания обращения {phone}, {nickname}")

    def check_case_status(self):
        """Checking the status of user's case"""

        if self.case_id:
            url = f'https://{self.domain}.omnidesk.ru/api/cases/{self.case_id}.json'
            response = requests.get(url, headers=self.headers, auth=self.auth)
            response = response.json()
            case_status = response.get("case", {}).get("status") if response.get("case") else None
            if case_status == "closed" or case_status is None:
                return False
            return True
        logger.error("Отсутствует case_id")
        return False

    def send_message(self, text, redis_client=None):
        """Duplicating a message from a client to the Omnidesk service"""

        if self.check_case_status():
            url = f"https://{self.domain}.omnidesk.ru/api/cases/{self.case_id}/messages.json/"
            payload = {"message": {
                "user_id": self.user_id,
                "content": text}}
            try:
                response = requests.post(url, headers=self.headers, auth=self.auth, data=json.dumps(payload))
                if response.status_code != requests.codes.created:
                    logger.error(f'Ошибка: отправки сообщения в omnidesk {response.status_code}, {response.text}, {response.headers}, {response.url}')
            except:
                logger.error(f'Ошибка: отправки сообщения в omnidesk: {text}')

        else:
            self.create_case(self.phone, self.nickname, text)
            client_omni_pickled = pickle.dumps(self)
            redis_client.set(self.phone + '_omni', client_omni_pickled)


class Bot:
    def __init__(self, wa_instance, token):
        self.session = requests.session()
        self.redis_client = None
        self.api_url = f"https://api.green-api.com/waInstance{wa_instance}/"
        self.token = token
        self.headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        self.all_clients = {}

    def get_notifications(self):
        """Checking incoming Whatsapp messages in the Green-api service"""

        url = self.api_url + 'ReceiveNotification/' + self.token
        payload = {}

        try:
            response = requests_retry_session(session=self.session).get(url, headers=self.headers, data=payload, timeout=120)
            if response.text:
                if response.text == 'Unauthorized':
                    logger.error("Нет авторизации green api, проверьте токен")
                    return None
                return response.json()
        except:
            logger.error("Ошибка получения сообщений в green-api")
            return None

    def del_notifications(self, receipt):
        """Deleting processed Whatsapp messages in the Green-api service"""

        url = self.api_url + 'DeleteNotification/' + self.token + "/" + str(receipt)
        payload = {}
        headers = {}
        response = self.session.delete(url, headers=headers, data=payload, timeout=120)
        print(f'Удалено сообщение с id {receipt} клиента - {response.text}')

    def del_all_notifications(self):
        """Deleting all accumulated Whatsapp messages in the Green-api service, used at the start of the application."""

        while True:
            json_data = self.get_notifications()
            if json_data is None:
                break
            receipt = json_data.get('receiptId')
            if receipt:
                self.del_notifications(receipt)

    def get_message(self):
        """Receiving incoming Whatsapp messages in the Green-api service"""

        # self.del_all_notifications()
        while True:
            response = self.get_notifications()
            if response is None:
                continue
            if "typeWebhook" in response.get("body", "***"):
                if response.get("body", {}).get("messageData", {}).get("typeMessage") not in ['textMessage', 'quotedMessage', 'extendedTextMessage', 'imageMessage', 'audioMessage', 'videoMessage', 'documentMessage']:
                    self.del_notifications(response['receiptId'])
                    continue
                print(f'Принято входящее сообщение в бот - {response["receiptId"]}')
                self.init_client(response)
                self.del_notifications(response['receiptId'])

    def init_client(self, response):
        """Message parsing, client creation."""

        try:
            phone = response["body"]["senderData"]['chatId'].replace('@c.us', '')
            nickname = response["body"]["senderData"]["senderName"]

            if response["body"]["messageData"]["typeMessage"] == "textMessage":
                message = response["body"]["messageData"]["textMessageData"]["textMessage"]

            elif response["body"]["messageData"]["typeMessage"] == "quotedMessage":
                message = f"""> {response.get("body").get("messageData").get("quotedMessage").get("textMessage", "Цитата медиафайла")}
                
                
                          {response["body"]["messageData"]["extendedTextMessageData"]["text"]}"""

            elif response["body"]["messageData"]["typeMessage"] == "extendedTextMessage":
                message = response["body"]["messageData"]["extendedTextMessageData"]["text"]

            elif response["body"]["messageData"]["typeMessage"] in ["imageMessage", "audioMessage", "videoMessage", "documentMessage"]:
                message = response["body"]["messageData"]["fileMessageData"]["downloadUrl"]
        except:
            phone = "000"
            nickname = "***"
            message = "Ошибка, обратитесь к администратору, входящее сообщение не распознано."
            logger.error(f"Входящее сообщение не распознано. {response}")

        if self.redis_client.get(phone) is not None:
            client = pickle.loads(self.redis_client.get(phone))
            client_omni = pickle.loads(self.redis_client.get(phone + '_omni'))
            if self.redis_client.get(phone + 'block') is None:
                if self.validate_message(client, client_omni, self.redis_client, message):
                    client.prev_state = client.state
                    client.change_state(message)
                    client_omni.send_message(f"{phone}: {message}", redis_client=self.redis_client)
                    self.send_message(phone, client.get_state_text())
                    client_omni.send_message(f"Бот: {client.get_state_text()}", redis_client=self.redis_client)
                    client_pickled = pickle.dumps(client)
                    self.redis_client.set(phone, client_pickled, ex=604800)
                    client_omni_pickled = pickle.dumps(client_omni)
                    self.redis_client.set(phone + '_omni', client_omni_pickled, ex=604800)
            else:
                client_omni.send_message(f"{phone}: {message}", redis_client=self.redis_client)
        else:
            client = Client(phone)
            client_omni = OmnideskIntegration()
            self.send_message(phone, f'Hello, {nickname}.')
            self.send_message(phone, client.get_state_text())
            client_omni.create_case(phone, nickname, f"{phone}: {message}")
            client_omni.send_message(f"Бот: Hello, {nickname}", redis_client=self.redis_client)
            client_omni.send_message(f"Бот: {client.get_state_text()}", redis_client=self.redis_client)
            self.del_notifications(response['receiptId'])
            client_pickled = pickle.dumps(client)
            self.redis_client.set(phone, client_pickled)
            client_omni_pickled = pickle.dumps(client_omni)
            self.redis_client.set(phone + '_omni', client_omni_pickled)

    def validate_message(self, client, client_omni, redis_client, message):
        """Message validation, the logic of blocking the bot's response to the client
        if the client has chosen to communicate with the operator."""

        current_state = client.state
        step = client.steps.get(current_state)
        if step is None:
            logger.error(f'Такого значения в степсах нет {current_state}')
        else:
            aval_answers = step[1].keys()
            if message not in aval_answers:
                if not message.isdigit():
                    redis_client.set(client.phone + 'block', '', ex=604800)
                    client_omni.send_message(f"{client.phone}: {message}", redis_client=redis_client)
                    return False
                elif client.state == "s0_8":
                    client_omni.send_message(f"{client.phone}: {message}", redis_client=redis_client)
                    return False
                else:
                    self.send_message(client.phone,
                                      f"{all_languages['valid_answer'][int(client.language) - 1]} {len(aval_answers)}: ")
                    client_omni.send_message(f"{client.phone}: {message}", redis_client=redis_client)
                    return False
        return True

    def send_message(self, phone, text):
        """Sending a message to a client in Whatsapp"""

        if len(phone) == 10:
            phone = '7' + phone
        url = self.api_url + 'sendMessage/' + self.token
        payload = {"chatId": phone + '@c.us',
                   "message": text}
        try:
            requests_retry_session(session=self.session).post(url, headers=self.headers, data=json.dumps(payload))
            print(f'Отправлено сообщение клиенту {phone}')
        except:
            logger.error(f'Ошибка отправки сообщения в green-api {phone}')
            return ""
        return ""

    def start_bot(self):
        self.get_message()


def main():
    """Initialization of the bot and settings."""

    with open('config.toml', mode="r", encoding="utf-8") as conf_file:
        config = toml.load(conf_file)
    bot = Bot(config['green_api']['wa_instance'], config['green_api']['token'])
    bot.redis_client = redis.Redis(host=config['redis']['host'], port='6379', db=0)
    bot.start_bot()


# if __name__ == "__main__":
#     main()
