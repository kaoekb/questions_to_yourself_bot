# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import SessionLocal, User
from question import question0, question1, question2, question3, question4, question5, question6, question7, question8, question9, question10, question11, question12, question13
from random import shuffle
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = FastAPI()
bot = TeleBot(os.getenv('TOKEN'))

class StartPayload(BaseModel):
    user_id: int

class TopicPayload(BaseModel):
    user_id: int
    topic: str


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()

    if not user:
        user = User(user_id=user_id)
        db.add(user)
        db.commit()

    markup = InlineKeyboardMarkup()
    start_button = InlineKeyboardButton('Начать игру', callback_data='start_game')
    markup.row(start_button)

    # Попытка удалить команду /start
    try:
        bot.delete_message(chat_id=user_id, message_id=message.message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

    # Отправка сообщения
    message = bot.send_message(user_id, 'Добро пожаловать! Нажмите "Начать игру", чтобы начать.', reply_markup=markup)

    # Обновление идентификатора последнего отправленного сообщения
    user.last_message_id = message.message_id
    db.commit()



@bot.callback_query_handler(func=lambda call: call.data == 'start_game')
def handle_start_game_callback(call):
    user_id = call.from_user.id
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()

    markup = InlineKeyboardMarkup()
    topics_button = InlineKeyboardButton('Выбрать тему', callback_data='choose_topic')
    back_button = InlineKeyboardButton('Назад', callback_data='back')
    markup.row(topics_button, back_button)

    # Удаление предыдущего сообщения с клавиатурой, если оно существует
    try:
        if user.last_message_id:
            # bot.delete_message(chat_id=call.message.chat.id, message_id=user.last_message_id)
            bot.delete_message(chat_id=user_id, message_id=user.last_message_id)

    except Exception as e:
        print(f"Error deleting message1: {e}")

    message = bot.send_message(user_id, 'Выберите тему:', reply_markup=markup)
    user.last_message_id = message.message_id
    # user.last_message_id = None

    db.commit()
@bot.callback_query_handler(func=lambda call: call.data == 'choose_topic')
def handle_choose_topic_callback(call):
    user_id = call.from_user.id
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()

    markup = InlineKeyboardMarkup()
    for topic in question0:
        button = InlineKeyboardButton(topic["text"], callback_data=f'choose_topic_{topic["id"]}')
        markup.row(button)

    back_button = InlineKeyboardButton('Назад', callback_data='back')
    markup.row(back_button)

    # Удаление предыдущего сообщения с клавиатурой, если оно существует
    try:
        if user.last_message_id:
            bot.delete_message(chat_id=user_id, message_id=user.last_message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

    message = bot.send_message(user_id, 'Выберите тему:', reply_markup=markup)
    user.last_message_id = message.message_id  # Сохраняем идентификатор текущего сообщения
    db.commit()


@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_topic_'))
def handle_topic_chosen_callback(call):
    user_id = call.from_user.id
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()

    chosen_topic_id = call.data.replace('choose_topic_', '')

    user.current_topic = chosen_topic_id
    user.current_question_id = None
    db.commit()

        # Попытка удалить предыдущее сообщение, если оно существует
    try:
        if user.last_message_id:
            bot.delete_message(chat_id=user_id, message_id=user.last_message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

    user.last_message_id = None
    db.commit()
    
    send_random_question(user_id)

def send_random_question(user_id):
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()

    topic_questions = get_questions_by_topic(user.current_topic)
    shuffle(topic_questions)

    if not topic_questions:
        bot.send_message(user_id, 'Вопросы для выбранной темы закончились. Начнем заново или выберите другую тему.')

    else:
        markup = InlineKeyboardMarkup()

        # Разделение вопросов на две части
        mid_point = len(topic_questions) // 2

        # Добавление кнопок для первой половины вопросов
        for question in topic_questions[:mid_point]:
            button = InlineKeyboardButton(question["text"], callback_data=f'choose_question_{question["id"]}')
            markup.add(button)

        # Добавление кнопок для второй половины вопросов
        for question in topic_questions[mid_point:]:
            button = InlineKeyboardButton(question["text"], callback_data=f'choose_question_{question["id"]}')
            markup.add(button)

        next_button = InlineKeyboardButton('Следующий вопрос', callback_data='next_question')
        back_button = InlineKeyboardButton('Назад', callback_data='back')
        markup.row(next_button, back_button)

        # Попытка удалить предыдущее сообщение, если оно существует
        try:
            if user.last_message_id:
                bot.delete_message(chat_id=user_id, message_id=user.last_message_id)
        except Exception as e:
            print(f"Error deleting message: {e}")

        message = bot.send_message(user_id, 'Выберите вопрос:', reply_markup=markup)
        user.last_message_id = message.message_id
        db.commit()
@bot.callback_query_handler(func=lambda call: call.data == 'next_question')
def handle_next_question_callback(call):
    user_id = call.from_user.id
    send_random_question(user_id)


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def handle_back_callback(call):
    user_id = call.from_user.id
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()

    user.current_topic = None
    user.current_question_id = None
    db.commit()

    markup = InlineKeyboardMarkup()
    start_button = InlineKeyboardButton('Начать игру', callback_data='start_game')
    markup.row(start_button)

    # Попытка удалить предыдущее сообщение, если оно существует
    try:
        if user.last_message_id:
            bot.delete_message(chat_id=user_id, message_id=user.last_message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

    message = bot.send_message(user_id, 'Начнем? :)', reply_markup=markup)

    # Обновляем идентификатор последнего отправленного сообщения
    user.last_message_id = message.message_id
    db.commit()

        

def get_questions_by_topic(topic_id):
    if topic_id == 'topic1':
        return question1
    elif topic_id == 'topic2':
        return question2
    elif topic_id == 'topic3':
        return question3
    elif topic_id == 'topic4':
        return question4
    elif topic_id == 'topic5':
        return question5
    elif topic_id == 'topic6':
        return question6
    elif topic_id == 'topic7':
        return question7
    elif topic_id == 'topic8':
        return question8
    elif topic_id == 'topic9':
        return question9
    elif topic_id == 'topic10':
        return question10
    elif topic_id == 'topic11':
        return question11
    elif topic_id == 'topic12':
        return question12
    elif topic_id == 'topic13':
        return question13
    else:
        return []


if __name__ == "__main__":
    bot.polling(none_stop=True)
