import os
import yt_dlp
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

TOKEN = "7954276064:AAFqLoTFXVtjo7Kwrix4kVE88KjCGR30AjI"

# 📥 Instagram videosi, rasm va karusel yuklash (toza holda)
def download_instagram(url):
    ydl_opts = {'outtmpl': 'downloads/video.mp4', 'format': 'best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "downloads/video.mp4"

# 📥 YouTube videosi yuklash (toza holda)
def download_youtube(url):
    ydl_opts = {'outtmpl': 'downloads/video.mp4', 'format': 'best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "downloads/video.mp4"

# 📥 TikTok videosini yuklash (suv belgisiz)
def download_tiktok(url):
    ydl_opts = {
        'outtmpl': 'downloads/video.mp4',
        'format': 'best',
        'postprocessors': [{'key': 'FFmpegVideoRemuxer', 'preferedformat': 'mp4'}]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "downloads/video.mp4"

# 📥 Instagram story yuklash (toza holda)
def download_instagram_story(username):
    L = instaloader.Instaloader()
    os.makedirs("downloads", exist_ok=True)
    profile = instaloader.Profile.from_username(L.context, username)
    
    for story in L.get_stories(userids=[profile.userid]):
        for item in story.get_items():
            L.download_storyitem(item, target="downloads")
            return f"downloads/{item.date}_story.mp4"

# 🔘 Tugmalar
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📥 Instagram", callback_data="instagram"),
         InlineKeyboardButton("🎥 YouTube", callback_data="youtube")],
        [InlineKeyboardButton("🎵 TikTok", callback_data="tiktok"),
         InlineKeyboardButton("📸 Instagram Story", callback_data="story")],
    ]
    return InlineKeyboardMarkup(keyboard)

# 🏁 /start komandasi
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 Salom! Yuklab olmoqchi bo‘lgan platformani tanlang:", reply_markup=get_main_keyboard())

# 🔘 Tugmalarni qayta ishlash
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "instagram":
        await query.message.reply_text("📥 Instagram videosi yoki rasmini yuklab olish uchun link yuboring.")
    elif query.data == "youtube":
        await query.message.reply_text("🎥 YouTube videosini yuklab olish uchun link yuboring.")
    elif query.data == "tiktok":
        await query.message.reply_text("🎵 TikTok videosini yuklab olish uchun link yuboring.")
    elif query.data == "story":
        await query.message.reply_text("📸 Instagram story yuklash uchun username yuboring (masalan, `@cristiano`).")

# 📩 Foydalanuvchi xabarini qayta ishlash
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    if "instagram.com" in text:
        await update.message.reply_text("⏳ Instagram videosi yuklab olinmoqda...")
        file_path = download_instagram(text)
    elif "youtube.com" in text or "youtu.be" in text:
        await update.message.reply_text("⏳ YouTube videosi yuklab olinmoqda...")
        file_path = download_youtube(text)
    elif "tiktok.com" in text:
        await update.message.reply_text("⏳ TikTok videosi yuklab olinmoqda...")
        file_path = download_tiktok(text)
    elif text.startswith("@"):
        await update.message.reply_text(f"📸 {text} username story yuklab olinmoqda...")
        file_path = download_instagram_story(text.strip("@"))
    else:
        await update.message.reply_text("⚠️ Noto‘g‘ri format! Iltimos, to‘g‘ri link yoki username yuboring.")
        return
    
    if file_path:
        await update.message.reply_video(video=open(file_path, "rb"))
        os.remove(file_path)

# 🚀 Botni ishga tushirish
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
