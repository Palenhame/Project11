import logging


logging.basicConfig(filename='errors.log', encoding='utf-8', level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_NAME = 'sqlite'
TABLE_NAME = 'users'
ASSISTANT_TEXT = 'Давай пообщаемся: '
SYSTEM_FOR_GPT = 'Отвечай коротко и ёмко.'
GPT_TOKENS = 500
MAX_USER_STT_BLOCKS = 20
MAX_USER_TTS_SYMBOLS = 2000
MAX_TTS_SYMBOLS = 1500

