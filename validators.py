from main import db
import math
from config import GPT_TOKENS, MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS, MAX_TTS_SYMBOLS
from error import NonExistingUser


def is_user_have_gpt_tokens(id_user):
    try:
        data = db.select_data(is_id=True, id=id_user)
        if data.gpt_tokens < GPT_TOKENS:
            return True, GPT_TOKENS - data.gpt_tokens
        return False, 0
    except NonExistingUser:
        return True, GPT_TOKENS


def count_all_blocks(user_id: int):
    try:
        data = db.return_data_from_db(db.select_data(user_id), 'user')
        return data.blocks
    except NonExistingUser:
        return 0


def count_all_symbol(user_id):
    try:
        data = db.return_data_from_db(db.select_data(user_id), 'user')
        return data.symbols
    except NonExistingUser:
        return 0


def is_stt_block_limit(user_id, duration) -> str | int:
    audio_blocks = math.ceil(duration / 15)
    all_blocks = count_all_blocks(user_id) + audio_blocks
    print(all_blocks, audio_blocks)

    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        return msg

    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        return msg

    return all_blocks


def is_tts_symbol_limit(user_id, text) -> (bool, str):
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        return None, msg

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        return None, msg
    return True, all_symbols
