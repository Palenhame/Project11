from telebot import TeleBot
from dotenv import load_dotenv
from os import getenv
from DB import DB
from GPT import GPT
from SpeechKit import SpeechKit
from config import DB_NAME, TABLE_NAME, ASSISTANT_TEXT


load_dotenv()
token = getenv('TOKEN')
folder_id = getenv('FOLDER_ID')
db = DB(DB_NAME, TABLE_NAME)
gpt = GPT(100, 100,
          'mistralai/Mistral-7B-Instruct-v0.2', assistant=ASSISTANT_TEXT)
bot = TeleBot(token=token)
spkit = SpeechKit(folder_id, voice='alena')

iam_token = ("t1.9euelZqelo2TlpOTnsuOmceWyZ6Tze"
             "3rnpWanJCVjYzKjpKdlczHjMrJipfl8_cRYy"
             "FO-e94GF8Y_d3z91ERH07573gYXxj9zef1656V"
             "mpGbnpGNl5aWnpaVjouay52U7_zF656VmpGb"
             "npGNl5aWnpaVjouay52UveuelZqayY2UjYnGz8"
             "aQkZqbi4nLkrXehpzRnJCSj4qLmtGLmdKckJKP"
             "ioua0pKai56bnoue0oye.z16Wet3vyurKgvDgiN"
             "G2am_GhBsJ6kg90Vtu8eR9KkH7WcVlUThbUzagss"
             "RYigAZA3k6HWWummUHMnX-fpXWCQ")


