from telebot import TeleBot
from dotenv import load_dotenv
from os import getenv
from DB import DB
from GPT import GPT
from SpeechKit import SpeechKit
from config import DB_NAME, TABLE_NAME, ASSISTANT_TEXT
from error import NonExistingUser
import requests
import time

load_dotenv()
token = getenv('TOKEN')
folder_id = getenv('FOLDER_ID')
db = DB(DB_NAME, TABLE_NAME)
gpt = GPT(100, 100,
          'mistralai/Mistral-7B-Instruct-v0.2', assistant=ASSISTANT_TEXT)
bot = TeleBot(token=token)
spkit = SpeechKit(folder_id, voice='alena')


def _create_new_iam_token():
    """
    Получает новый IAM-TOKEN и дату истечения его срока годности и
    записывает полученные данные в json
    """
    url = 'http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token'
    headers = {'Metadata-Flavor': 'Google'}

    try:
        response = requests.get(url, headers=headers)
        pass

    except Exception as e:
        print("Не удалось выполнить запрос:", e)
        print("Токен не получен")
        raise ConnectionError

    else:
        if response.status_code == 200:
            token_data = {
                "access_token": response.json().get("access_token"),
                "expires_in": response.json().get("expires_in") + time.time()
            }
            try:
                db.delete_user(111)
            except NonExistingUser:
                pass
            db.make_new_user(111, 'token')
            id = db.select_data(111)[0].id
            db.update_data(id, 'message', token_data['access_token'])
            db.update_data(id, 'gpt_tokens', token_data['expires_in'])

        else:
            print("Ошибка при получении ответа:", response.status_code)
            print("Токен не получен")


def get_iam_token() -> str:
    """
    Получает действующий IAM-TOKEN и возвращает его
    """
    try:
        iam_token = db.select_data(111)[0]
    except NonExistingUser:
        try:
            _create_new_iam_token()
            return db.select_data(111)[0].message
        except ConnectionError:
            raise ConnectionError

    if not iam_token.message or iam_token.gpt_tokens <= time.time():
        _create_new_iam_token()
        iam_token = db.select_data(111)[0]

    return iam_token.message

