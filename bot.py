import logging
import random
from datetime import datetime
from groq import Groq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8050858161:AAGZ5FAeiIvI5y8h53Uh1RTVHeydnOcibHM"
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)
CHANNEL_ID = "-1002791812237"

TWITTER_API_KEY = "nTJJ9n1vwy5LjYNcbHDu8Arl4"
TWITTER_API_SECRET = "Ne8B0jHnBKmCfNsNx0H1MPriE4hwPCz2fAX6xbmiYijjCskTAI"
TWITTER_ACCESS_TOKEN = "1613939292463579137-Pz9E3CgORyvFqhKSwfFt2Jrx2tb6WK"
TWITTER_ACCESS_TOKEN_SECRET = "n2vRAPDIMTTSWNbTwzTuAQnqPT5OzJGkFOb1Ds80EqZlr"

logging.basicConfig(level=logging.INFO)

PROMPTS = [
    """Ты автор живого Telegram-канала про китайский язык. Пишешь как человек, не как учебник.

Напиши пост: одно полезное слово на каждый день.
Формат:
— иероглиф + пиньинь крупно
— перевод одним словом
— пример из реальной жизни (не из учебника)
— один трюк чтобы запомнить

Стиль: коротко, живо, с характером. Без воды. Максимум 70 слов. Только русский и китайский.""",

    """Ты автор живого Telegram-канала про китайский язык. Пишешь как человек, не как учебник.

Напиши пост: два иероглифа которые все путают.
Покажи разницу через смешной или жизненный пример — чтобы запомнилось.
Никакой теории, только суть.

Стиль: с юмором, коротко, дерзко. Максимум 70 слов. Только русский и китайский.""",

    """Ты автор живого Telegram-канала про китайский язык. Пишешь как человек, не как учебник.

Напиши пост: неожиданный факт о китайском языке или иероглифах.
Что-то такое что человек прочитает и скажет "вот это да".
В конце — провокационный вопрос читателям.

Стиль: живо, удивляй, без занудства. Максимум 70 слов. Только русский и китайский.""",

    """Ты автор живого Telegram-канала про китайский язык. Пишешь как человек, не как учебник.

Напиши пост: фраза которую реально используют китайцы в разговоре.
Не "здравствуйте" и "спасибо" — что-то настоящее из жизни.
Покажи когда это говорят и как звучит.

Стиль: разговорный, живой, как будто сам только что услышал это в Китае. Максимум 70 слов.""",
]

def generate_content():
    prompt = random.choice(PROMPTS)
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content

def post_to_channel(text):
    import urllib.request, json
    data = json.dumps({"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Запостить сейчас", callback_data="post_now")],
        [InlineKeyboardButton("✏️ Свой текст в канал", callback_data="custom_post")],
        [InlineKeyboardButton("🐦 Написать твит", callback_data="tweet_prompt")],
        [InlineKeyboardButton("📊 Статус", callback_data="status")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>NIHAO ACADEMY Bot</b>\n\nВыбери действие:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back")]])

    if query.data == "post_now":
        await query.edit_message_text("⏳ Генерирую контент...")
        try:
            content = generate_content()
            post_to_channel(content)
            await query.edit_message_text(f"✅ <b>Опубликовано!</b>\n\n{content}", parse_mode="HTML", reply_markup=back_btn)
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {e}", reply_markup=back_btn)

    elif query.data == "custom_post":
        context.user_data["awaiting"] = "custom_post"
        await query.edit_message_text("✏️ Напиши текст — опубликую в канале:", reply_markup=back_btn)

    elif query.data == "tweet_prompt":
        context.user_data["awaiting"] = "tweet"
        await query.edit_message_text("🐦 Напиши текст твита:", reply_markup=back_btn)

    elif query.data == "status":
        await query.edit_message_text(
            "📊 <b>Статус</b>\n\n✅ Бот активен\n🕘 Автопост: 09:00 и 19:00\n📣 Канал: @nihaoacademy",
            parse_mode="HTML",
            reply_markup=back_btn
        )

    elif query.data == "back":
        await query.edit_message_text("👋 <b>NIHAO ACADEMY Bot</b>\n\nВыбери действие:", parse_mode="HTML", reply_markup=main_menu())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")

    if awaiting == "custom_post":
        post_to_channel(update.message.text)
        context.user_data["awaiting"] = None
        await update.message.reply_text("✅ Опубликовано в канале!", reply_markup=main_menu())

    elif awaiting == "tweet":
        try:
            import tweepy
            client = tweepy.Client(consumer_key=TWITTER_API_KEY, consumer_secret=TWITTER_API_SECRET, access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)
            client.create_tweet(text=update.message.text)
            context.user_data["awaiting"] = None
            await update.message.reply_text("✅ Твит опубликован!", reply_markup=main_menu())
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}", reply_markup=main_menu())
    else:
        await update.message.reply_text("👋 <b>NIHAO ACADEMY Bot</b>\n\nВыбери действие:", parse_mode="HTML", reply_markup=main_menu())

async def scheduled_post(context):
    try:
        content = generate_content()
        post_to_channel(content)
        print(f"[{datetime.now()}] Auto-posted successfully")
    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

app.job_queue.run_daily(scheduled_post, time=datetime.strptime("09:00", "%H:%M").time())
app.job_queue.run_daily(scheduled_post, time=datetime.strptime("19:00", "%H:%M").time())

print("Bot running... Auto-post at 09:00 and 19:00")
app.run_polling()
