from main import gpt, db, bot
from DB import Answer
from error import NonExistingUser
from config import SYSTEM_FOR_GPT


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'start')


@bot.message_handler(commands=['text'])
def for_text(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'send me text')
    bot.register_next_step_handler(message, text)


# @bot.message_handler(content_types=['text'])
def text(message):
    user_id = message.chat.id

    if len(message.text) < 100:
        text_into_db(user_id, message.text, 100)

    bot.send_message(user_id, ask_gpt(message.text, user_id))
    bot.register_next_step_handler(message, text)


@bot.message_handler(commands=['audio'])
def for_audio(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'send me audio')
    bot.register_next_step_handler(message, audio)


# @bot.message_handler(content_types=['voice'])
def audio(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'voice')
    bot.register_next_step_handler(message, audio)


def text_into_db(user_id: int, text: str, gpt_tokens: int):
    try:
        data = return_data_from_db(db.select_data(user_id), 'user')
        db.make_new_user(user_id, 'user')
        id_user = data.id + 2
    except NonExistingUser:
        db.make_new_user(user_id, 'user')
        data = return_data_from_db(db.select_data(user_id), 'user')
        id_user = data.id

    db.update_data(id_user, 'message', text)
    db.update_data(id_user, 'gpt_tokens', data.gpt_tokens + gpt_tokens)
    assistant_data = return_data_from_db(db.select_data(user_id), 'assistant')
    print(assistant_data)
    db.make_new_user(user_id, 'assistant')
    db.update_data(assistant_data.id + 2, 'message',
                   f'{assistant_data.message} {text}' if assistant_data.message else text)


def assistant_content(user_id: int) -> str:
    try:
        assistant_data = return_data_from_db(db.select_data(user_id), 'assistant')
        return assistant_data.message
    except NonExistingUser:
        return ''


def ask_gpt(text: str, user_id: int):
    if False:
        return 'error'
    print(text)
    assistant = assistant_content(user_id)
    print(assistant)
    answer = gpt.question(SYSTEM_FOR_GPT, text, 100, assistant)
    return answer


def return_data_from_db(data: list[Answer], string: str) -> Answer | None:
    user_data = Answer(0)
    for i in data:
        if i.role == string:
            user_data = i
            break
    return user_data


if __name__ == "__main__":
    try:
        db.delete_user(2065585729)
    except NonExistingUser:
        pass
    bot.infinity_polling()
