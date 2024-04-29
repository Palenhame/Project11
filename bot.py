from main import gpt, db, bot


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    db.make_new_user(user_id, 'user')
    bot.send_message(user_id, 'start')


@bot.message_handler(commands=['text'])
def for_text(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'send me text')
    bot.register_next_step_handler(message, )


@bot.message_handler(content_types=['text'])
def text(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'text')


if __name__ == "__main__":
    bot.infinity_polling()
