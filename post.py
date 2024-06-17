import telebot
import random
from telebot import types
import qrcode


bot = telebot.TeleBot("7227507399:AAGrk8wjVxzu7FpqrydYDZcdt-1utcdCCXw")
CHANNEL_NAME = '@Aroratg'

# Функция для генерации случайного артикула
def generate_sku():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))

# Функция для создания QR кода
def create_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(f'{data}.png')  # Сохраняем QR код как изображение
    


# привествие
@bot.message_handler(commands=["start"])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard= True, one_time_keyboard= True)
    keyboard.add(types.KeyboardButton('/QR-код'))
    keyboard.add(types.KeyboardButton('/post'))
    bot.send_message(message.chat.id, "Привет! Я бот для выгрузки постов в канал)\nЕсли желаете создать пост нажмите:'/post'", reply_markup=keyboard)
    
    
user_data = {}

@bot.message_handler(func=lambda message: message.text == '/post')
def ask_for_name(message):
    msg = bot.reply_to(message, "Введите название товара:")
    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    user_data['name'] = message.text
    msg = bot.reply_to(message, "Введите размер товара:")
    bot.register_next_step_handler(msg, process_size_step)


def process_size_step(message):
    user_data['size'] = message.text
    msg = bot.reply_to(message, "Введите цену товара:")
    bot.register_next_step_handler(msg, process_price_step)

def process_price_step(message):
    user_data['price'] = message.text
    bot.send_message(message.chat.id, "Пожалуйста, загрузите фотографию товара.")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_data['photo_id'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "Фотография сохранена. Теперь вы можете создать пост. /photo")

        
@bot.message_handler(commands=['QR-код'])
def new_sku(message):
    sku = generate_sku()  # Генерируем новый артикул
    create_qr_code(sku)  # Создаем QR код для артикула
    with open(f'{sku}.png', 'rb') as qr_file:
        bot.send_photo(message.chat.id, qr_file, caption=f'Артикул: {sku}')
        

@bot.message_handler(func=lambda message:message.text == '/photo')
def create_post(message):
    user_data['/photo'] = message.text
    if 'photo_id' in user_data:
        sku = generate_sku()  
        create_qr_code(sku) 
        with open(f'{sku}.png', 'rb') as qr_file:
            bot.send_photo(message.chat.id, qr_file, caption=f'артикул: {sku}')
        bot.send_photo(chat_id=CHANNEL_NAME, photo=user_data['photo_id'], caption=f"Название: {user_data['name']}\nРазмеры: {user_data['size']}\nЦена: {user_data['price']}\nАртикул: {sku}")

    else:
        bot.send_message(message.chat.id, "Фотография не загружена.")
        
        

    

bot.polling(none_stop = True)
