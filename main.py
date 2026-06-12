import telebot
from telebot import types
import os
from dotenv import load_dotenv
import platform
import psutil
from datetime import datetime
import docker

load_dotenv()
token = os.getenv("BOT_TOKEN")
chat_id = int(os.getenv("CHAT_ID"))

bot = telebot.TeleBot(token)

@bot.message_handler(commands=["start", "help"])
def hello_msg(message):
    if message.chat.id != chat_id:
        bot.send_message(message.chat.id, "Доступ запрещен")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("⚙️Получить хар-ки сервера⚙️")
    btn2 = types.KeyboardButton("🐬Информация о работе докер контейнеров🐬")
    markup.add(btn1, btn2, row_width=1)

    os_name = platform.platform()
    bot.send_message(message.chat.id, f"{message.from_user.first_name}, добро пожаловать в {os_name}", reply_markup=markup)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.chat.id != chat_id:
        bot.send_message(message.chat.id, "Доступ запрещен")
        return
    
    if message.text == "⚙️Получить хар-ки сервера⚙️":
        bot.send_chat_action(message.chat.id, 'typing')
        server_info = get_server_info()
        bot.send_message(message.chat.id, server_info, parse_mode="HTML")
    if message.text == "🐳Информация о работе докер контейнеров🐳":
        bot.send_chat_action(message.chat.id, 'typing')
        docker_containers = get_docker_containers()
        bot.send_message(message.chat.id, docker_containers, parse_mode="HTML", link_preview_options=types.LinkPreviewOptions(is_disabled=True))



def get_server_info():
    os_name = platform.system()
    os_release = platform.release()
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    uptime_str = str(uptime).split('.')[0]
    
    cpu_cores_physical = psutil.cpu_count(logical=False) or 0
    cpu_cores_logical = psutil.cpu_count(logical=True) or 0
    cpu_usage = psutil.cpu_percent(interval=1) 
    
    ram = psutil.virtual_memory()
    ram_total = ram.total
    ram_used = ram.used
    ram_percent = ram.percent
    
    root_partition = "C:\\" if os_name == "Windows" else "/"
    disk = psutil.disk_usage(root_partition)
    disk_total = disk.total
    disk_used = disk.used
    disk_percent = disk.percent
    
    net_io = psutil.net_io_counters()
    net_sent = net_io.bytes_sent
    net_recv = net_io.bytes_recv

    message = (
        "🖥 <b>Информация о сервере</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🐧 <b>ОС:</b> {os_name} {os_release}\n"
        f"⏱ <b>Аптайм:</b> {uptime_str}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 <b>Процессор:</b>\n"
        f"   • Ядер: {cpu_cores_physical} (потоков: {cpu_cores_logical})\n"
        f"   • Загрузка: <b>{cpu_usage}%</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💾 <b>Оперативная память:</b>\n"
        f"   • Всего: {ram_total / 1024**3:.2f} ГБ\n"
        f"   • Использовано: {ram_used / 1024**3:.2f} ГБ (<b>{ram_percent}%</b>)\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💿 <b>Диск ({root_partition}):</b>\n"
        f"   • Всего: {disk_total / 1024**3:.2f} ГБ\n"
        f"   • Использовано: {disk_used / 1024**3:.2f} ГБ (<b>{disk_percent}%</b>)\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>Сеть:</b>\n"
        f"   • Получено: {net_recv / 1024**3:.2f} ГБ\n"
        f"   • Отправлено: {net_sent / 1024**3:.2f} ГБ\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    return message

def get_docker_containers():
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        if not containers:
            return "<b>Docker:</b> Контейнеры отсутствуют"
        lines = ["<b>Docker контейнеры:</b>"]
        for c in containers:
            name = c.name
            status = c.status
            image = c.image.tags[0] if c.image.tags else c.image.id[:12]
            icon = "🟢" if status == "running" else "🔴"
            lines.append(f"{icon} <code>{name}</code> ({image}) — {status}")
        return "\n".join(lines)
    except Exception:
        return "🐳 <b>Docker:</b> Ошибка подключения или сервис не запущен"

bot.infinity_polling()