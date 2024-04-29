import logging


logging.basicConfig(filename='errors.log', encoding='utf-8', level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_NAME = 'sqlite'
TABLE_NAME = 'users'
ASSISTANT_TEXT = 'Давай пообщаемся: '
