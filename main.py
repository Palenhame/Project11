from telebot import TeleBot
from dotenv import load_dotenv
from os import getenv
from DB import DB
from GPT import GPT
from config import DB_NAME, TABLE_NAME, ASSISTANT_TEXT


load_dotenv()
token = getenv('TOKEN')
folder_id = getenv('FOLDER_ID')
db = DB(DB_NAME, TABLE_NAME)
gpt = GPT(100, 100,
          'mistralai/Mistral-7B-Instruct-v0.2', assistant=ASSISTANT_TEXT)
bot = TeleBot(token=token)


