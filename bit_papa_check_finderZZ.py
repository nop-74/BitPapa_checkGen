import telebot
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Чтение токена из файла token.ini
try:
    with open('token.ini', 'r') as f:
        token = f.readline().strip()
except FileNotFoundError:
    print("Файл token.ini не найден.")
    exit()

bot = telebot.TeleBot(token)
running = True

# Настройки Selenium для Chrome
options = Options()
options.add_argument("--headless") # Запуск в скрытом режиме
try:
    driver = webdriver.Chrome(options=options) # Инициализация веб-драйвера Chrome
except WebDriverException as e:
    print(f"Ошибка при инициализации Chrome: {e}")
    exit()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет!Запомни команды нашего бота или запиши где нибудь|admin @fradyrad\n/generate - сгенерировать чеки\n/check - проверить чеки\n/stop - остановить")

# Обработчик команды /generate
@bot.message_handler(commands=['generate'])
def generate_btc(message):
    bot.send_message(message.chat.id, "Сколько чеков?")
    bot.register_next_step_handler(message, process_amount)

# Обработка количества чеков, введенного пользователем
def process_amount(message):
    try:
        amount = int(message.text)
        if 1 <= amount <= 99999: # Проверка на корректность введенного числа
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
            for n in range(amount):
                password = ''.join(random.choice(chars) for i in range(23))
                btclink = 'http://t.me/bitpapa_bot?start=papa_code__' + password
                bot.send_message(message.chat.id, btclink)
            bot.send_message(message.chat.id, f"Сгенерировано {amount} ссылок.")
        else:
            bot.send_message(message.chat.id, "Число от 1 до 99999.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите число.")

# Обработчик команды /check
@bot.message_handler(commands=['check'])
def check_links(message):
    try:
        with open('checks.ini', 'r') as f:
            links = [line.strip() for line in f] # Чтение ссылок из файла checks.ini
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Файл checks.ini не найден.")
        return

    for link in links: # Перебор ссылок из файла
        if not running: # Проверка, не остановлен ли скрипт
            break
        try:
            bot.send_message(message.chat.id, f"Переходим по ссылке: {link}")
            driver.get(link) # Открытие ссылки в браузере
            time.sleep(random.randint(10, 20)) # Ожидание случайного времени
            #driver.close()
            #driver.switch_to.window(driver.window_handles[0]) # Переключение на первую вкладку
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при обработке ссылки {link}: {e}")

# Обработчик команды /stop
@bot.message_handler(commands=['stop'])
def stop_script(message):
    global running 
    running = False # Установка флага остановки
    bot.send_message(message.chat.id, "Скрипт остановлен.")
    driver.quit() # Закрытие браузера

bot.polling()
