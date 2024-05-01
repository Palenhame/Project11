from main import gpt, db, bot
from DB import Answer
from error import NonExistingUser


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    db.make_new_user(user_id, 'user')
    bot.send_message(user_id, 'start')


@bot.message_handler(commands=['text'])
def for_text(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'send me text')
    bot.register_next_step_handler(message, text)


@bot.message_handler(content_types=['text'])
def text(message):
    user_id = message.chat.id
    data = return_data_from_db(db.select_data(user_id), 'user')
    db.update_data(data.id, 'message', message.text)
    bot.send_message(user_id, 'text')


@bot.message_handler(commands=['audio'])
def for_text(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'send me audio')
    bot.register_next_step_handler(message, audio)


@bot.message_handler(content_types=['voice'])
def audio(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'voice')


def ask_gpt(text: str, user_id: int):
    if False:
        bot.send_message(user_id, 'error')
    return gpt.question()


def return_data_from_db(data: list[Answer], string: str) -> Answer | None:
    user_data = None
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
