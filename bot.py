from main import gpt, db, bot, spkit, iam_token
from DB import Answer
from error import NonExistingUser, TooLongTask
from config import SYSTEM_FOR_GPT, GPT_TOKENS
from validators import is_user_have_gpt_tokens, is_stt_block_limit, is_tts_symbol_limit

IS_SEND_GPT_STATUS_CODE = False


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Привет. Я бот который поможет скоротать тебе время. Нужна будет помощь пиши /help')


@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Долг зовёт Крепыш вперёд.'
                              'Сейчас я тебе всё объясню.'
                              'При отпраке')



@bot.message_handler(commands=['status_code'])
def change_value_of_variable(message):
    user_id = message.chat.id
    global IS_SEND_GPT_STATUS_CODE
    IS_SEND_GPT_STATUS_CODE = not IS_SEND_GPT_STATUS_CODE
    bot.send_message(user_id, 'Вы видите статус коды.' if IS_SEND_GPT_STATUS_CODE else 'Вы не видите статус коды.')


@bot.message_handler(commands=['text'])
def for_text(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Отправь мне текст.')
    bot.register_next_step_handler(message, text)


# @bot.message_handler(content_types=['text'])
def text(message):
    user_id = message.chat.id
    if message.text == '/end':
        bot.send_message(user_id, 'Вы закончили диалог.')
        return
    db.make_new_user(user_id, 'user')
    db.make_new_user(user_id, 'assistant')
    data = db.return_data_from_db(db.select_data(user_id), 'user')
    bot.send_message(user_id, ask_gpt(data.id, message.text))
    if IS_SEND_GPT_STATUS_CODE:
        bot.send_message(user_id, f'Статус код: {gpt.status_code}')
    bot.register_next_step_handler(message, text)


@bot.message_handler(commands=['audio'])
def for_audio(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Отправьте мне аудио.')
    bot.register_next_step_handler(message, audio)


@bot.message_handler(commands=['stt'])
def stt(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Отправьте мне аудио.')
    bot.register_next_step_handler(message, speach_to_text)


@bot.message_handler(commands=['tts'])
def tts(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Отправьте мне текст.')
    bot.register_next_step_handler(message, text_to_speech)


def text_to_speech(message, new_user: bool = True, own: bool = True, system_text: str = ''):
    user_id = message.chat.id
    text = message.text if not system_text else system_text

    if new_user:
        db.make_new_user(user_id, 'user')

    tts_val = is_tts_symbol_limit(user_id, text)

    if tts_val[0] is True:
        data = db.return_data_from_db(db.select_data(user_id), 'user')
        db.update_data(data.id, 'symbols', tts_val[1])
        if own:
            bot.send_message(user_id, text)
        return 11111
    else:
        if own:
            bot.send_message(user_id, tts_val[1])
        return tts_val[1]


def speach_to_text(message, new_user: bool = True, own: bool = True):
    user_id = message.chat.id
    if not message.voice:
        bot.send_message(user_id, "Это не голосовое сообщение.")
        return

    stt_val = validate_stt_message(user_id, message.voice.duration)
    if stt_val[0] is True:
        if new_user:
            db.make_new_user(user_id, 'user')
            db.make_new_user(user_id, 'assistant')
        data = db.return_data_from_db(db.select_data(user_id), 'user')
        db.update_data(data.id, 'blocks', stt_val[1])
        if own:
            bot.send_message(user_id, 'all ok')
        else:
            return 'all ok', data.id
    else:
        if own:
            bot.send_message(user_id, stt_val[1])
        else:
            return stt_val[1]


def audio(message):
    user_id = message.chat.id
    if message.text == '/end':
        bot.send_message(user_id, 'Вы закончили диалог.')
        return

    stt_val = speach_to_text(message, True, False)
    try:
        stt_val[1]
    except IndexError:
        bot.send_message(user_id, stt_val)
        return
    answer = ask_gpt(stt_val[1], stt_val[0])
    if answer != 'no tokens':
        tts_val = text_to_speech(message, False, False, answer)
        if isinstance(tts_val, str):
            bot.send_message(user_id, tts_val)
            return
        bot.send_message(user_id, tts_val)
        if IS_SEND_GPT_STATUS_CODE:
            bot.send_message(user_id, f'Статус код: {gpt.status_code}')
        bot.register_next_step_handler(message, audio)
    else:
        bot.send_message(user_id, answer)


def text_into_db(text: str, gpt_tokens: int, id_user: int):
    try:
        last_note = db.select_data(is_id=True, id=id_user - 2)
        db.update_data(id_user, 'gpt_tokens', last_note.gpt_tokens + gpt_tokens)
        db.update_data(id_user, 'message', f'{last_note.message} ' + text)
    except NonExistingUser:
        db.update_data(id_user, 'gpt_tokens', gpt_tokens)
        db.update_data(id_user, 'message', text)


def assistant_content(id_user: int) -> str:
    try:
        assistant_data = db.select_data(is_id=True, id=id_user)
        return assistant_data.message
    except NonExistingUser:
        return ''


def assistant_into_db(text: str, id_user: int):
    try:
        last_note = db.select_data(is_id=True, id=id_user - 1)
        db.update_data(id_user + 1, 'message', f'{last_note.message} ' + text)
    except NonExistingUser:
        db.update_data(id_user + 1, 'message', text)


def _ask_gpt(text: str, id_user: int, max_tokens: int):
    assistant = assistant_content(id_user)
    answer = gpt.question(SYSTEM_FOR_GPT, text,
                          20 if max_tokens > 20 else max_tokens, assistant)
    return answer


def validate_gpt_tokens(user_id, function):
    try:
        have, tokens = function(user_id)
    except NonExistingUser:
        have = True
        tokens = GPT_TOKENS
    return have, tokens


def validate_stt_message(user_id, duration):
    value = is_stt_block_limit(user_id, duration)
    if isinstance(value, int):
        return True, value

    else:
        return value, None


def ask_gpt(id_user, text):
    have, tokens = validate_gpt_tokens(id_user - 2, is_user_have_gpt_tokens)
    print(f'have: {have}, tokens: {tokens}')
    if have:
        text_into_db(text, 100, id_user)

        answer = _ask_gpt(text, id_user - 1, tokens)

        assistant_into_db(answer, id_user)

        return answer
    else:
        db.delete_user_by_id(id_user)
        db.delete_user_by_id(id_user + 1)
        return 'У вас не хватает токенов.'


if __name__ == "__main__":
    try:
        db.delete_user(2065585729)
    except NonExistingUser:
        pass
    bot.infinity_polling()
