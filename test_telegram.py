import telegram

TELEGRAM_TOKEN = '8322483491:AAGLfls2dUvCs1zAIF4CXE00l2P-5qgUdyE'
TELEGRAM_USER_ID = '8131218642'

bot = telegram.Bot(token=TELEGRAM_TOKEN)

bot.send_message(chat_id=TELEGRAM_USER_ID, text='✅ Test message from your Cita Previa bot!')
print("Test message sent!")
