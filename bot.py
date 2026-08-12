import os
import io
import threading
import logging

import telebot
from PIL import Image, ImageEnhance, ImageFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- CONFIG ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable set nahi hai! GitHub Secrets me set karein.")

# GitHub Actions job max 6 ghante (360 min) chalta hai, usse pehle hi gracefully band kar dete hain
# taaki agla scheduled run smoothly shuru ho sake.
MAX_RUN_MINUTES = int(os.environ.get("MAX_RUN_MINUTES", 340))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# ---------- IMAGE ENHANCEMENT ----------
def enhance_image(image_bytes: bytes) -> bytes:
    """
    Photo ko enhance karta hai:
    - Sharpness badhata hai
    - Contrast improve karta hai
    - Color/saturation thoda boost karta hai
    - Brightness auto-adjust
    - Halka denoise + upscale (agar image chhoti ho)
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    max_side = max(img.size)
    if max_side < 1600:
        scale = min(2.0, 1600 / max_side)
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, Image.LANCZOS)

    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Color(img).enhance(1.2)
    img = ImageEnhance.Brightness(img).enhance(1.05)
    img = ImageEnhance.Sharpness(img).enhance(1.5)

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=95)
    output.seek(0)
    return output.read()


# ---------- BOT KEYBOARDS ----------
def main_menu():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton("📸 Enhance Photo"),
        telebot.types.KeyboardButton("❓ Help"),
        telebot.types.KeyboardButton("ℹ️ About")
    )
    return keyboard


# ---------- BOT HANDLERS ----------
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 <b>Welcome to AI Photo Enhancer!</b>\n\n"
        "📸 Apni photo bhejein aur main usay automatically enhance karke wapas bhej dunga.\n\n"
        "👇 Neeche menu se option select karein:",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "📸 Enhance Photo")
def enhance_photo_button(message):
    bot.send_message(message.chat.id, "📸 <b>Photo Enhance</b>\n\nAb apni photo send karein. Main usay enhance karke wapas bhej dunga.", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "❓ Help")
def help_button(message):
    bot.send_message(
        message.chat.id,
        "❓ <b>How to use</b>\n\n"
        "1️⃣ <b>📸 Enhance Photo</b> par tap karein.\n"
        "2️⃣ Apni photo send karein.\n"
        "3️⃣ Bot photo ko automatically enhance karega.\n"
        "4️⃣ Enhanced photo aapko wapas mil jayegi.\n\n"
        "💡 Best result ke liye clear/original photo bhejein.",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "ℹ️ About")
def about_button(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>About AI Photo Enhancer</b>\n\n"
        "✨ Automatic photo enhancement\n"
        "🔍 Sharper details\n"
        "🎨 Improved colors\n"
        "💡 Better brightness & contrast\n"
        "📐 Small images ka automatic upscale\n\n"
        "Powered by Python + Pillow.",
        reply_markup=main_menu()
    )


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    try:
        bot.send_chat_action(message.chat.id, "upload_photo")
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        enhanced_bytes = enhance_image(downloaded_file)
        bot.send_photo(
            message.chat.id, photo=enhanced_bytes,
            caption="✅ <b>Enhanced photo ready!</b>\n\n✨ Sharper • 🎨 Better colors • 💡 Improved brightness",
            reply_to_message_id=message.message_id, reply_markup=main_menu()
        )
    except Exception as e:
        logger.exception("Error while enhancing photo")
        bot.reply_to(message, f"❌ Kuch error aa gaya: {e}", reply_markup=main_menu())


@bot.message_handler(content_types=["document"])
def handle_document(message):
    try:
        mime = message.document.mime_type or ""
        if not mime.startswith("image/"):
            bot.reply_to(message, "⚠️ Please koi image file bhejein.", reply_markup=main_menu())
            return
        bot.send_chat_action(message.chat.id, "upload_photo")
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        enhanced_bytes = enhance_image(downloaded_file)
        bot.send_document(
            message.chat.id, document=("enhanced.jpg", enhanced_bytes),
            caption="✅ Enhanced image ready!", reply_to_message_id=message.message_id,
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.exception("Error while enhancing document image")
        bot.reply_to(message, f"❌ Kuch error aa gaya: {e}", reply_markup=main_menu())


@bot.message_handler(func=lambda message: True, content_types=["text"])
def unknown_text(message):
    bot.send_message(message.chat.id, "👇 Menu se koi option select karein, ya directly photo send karein.", reply_markup=main_menu())


# ---------- AUTO-STOP (GitHub Actions time limit ke liye) ----------
def auto_stop():
    logger.info(f"{MAX_RUN_MINUTES} minute ho gaye, bot ko gracefully stop kar rahe hain "
                f"(agla scheduled run isse continue karega)...")
    bot.stop_polling()


if __name__ == "__main__":
    timer = threading.Timer(MAX_RUN_MINUTES * 60, auto_stop)
    timer.daemon = True
    timer.start()

    logger.info("Bot polling shuru ho raha hai...")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
