import os
import io
import logging
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import telebot
from telebot import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
bot = telebot.TeleBot(BOT_TOKEN)

user_sessions = {}

ENHANCEMENTS = {
    "Auto Enhance": {
        "desc": "Smart auto brightness, contrast and color boost",
    },
    "Sharpen": {
        "desc": "Crisp and sharp details",
    },
    "Vivid Colors": {
        "desc": "Boost saturation and vibrancy",
    },
    "Portrait": {
        "desc": "Soft skin, bright eyes, natural glow",
    },
    "Landscape": {
        "desc": "Deep greens, vivid sky, sharp horizon",
    },
    "Night Mode": {
        "desc": "Brighten dark photos, reduce noise",
    },
    "Vintage": {
        "desc": "Warm faded film look",
    },
    "Black & White": {
        "desc": "Dramatic high contrast monochrome",
    },
    "HDR Effect": {
        "desc": "High dynamic range pop",
    },
    "Soft Glow": {
        "desc": "Dreamy soft light effect",
    },
}

INTENSITIES = {
    "Light":  0.5,
    "Medium": 1.0,
    "Strong": 1.8,
}


def auto_enhance(img, strength):
    img = ImageOps.autocontrast(img, cutoff=1)
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 + 0.15 * strength)
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 + 0.2 * strength)
    color = ImageEnhance.Color(img)
    img = color.enhance(1.0 + 0.15 * strength)
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(1.0 + 0.3 * strength)
    return img


def sharpen_enhance(img, strength):
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(1.0 + 2.0 * strength)
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 + 0.1 * strength)
    for _ in range(int(strength * 2)):
        img = img.filter(ImageFilter.SHARPEN)
    return img


def vivid_enhance(img, strength):
    color = ImageEnhance.Color(img)
    img = color.enhance(1.0 + 0.8 * strength)
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 + 0.3 * strength)
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 + 0.05 * strength)
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(1.0 + 0.2 * strength)
    return img


def portrait_enhance(img, strength):
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 + 0.12 * strength)
    color = ImageEnhance.Color(img)
    img = color.enhance(1.0 + 0.2 * strength)
    # Soft blur then sharpen for skin smoothing
    smoothed = img.filter(ImageFilter.GaussianBlur(radius=0.5 * strength))
    sharpness = ImageEnhance.Sharpness(smoothed)
    img = sharpness.enhance(1.0 + 0.5 * strength)
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 + 0.1 * strength)
    return img


def landscape_enhance(img, strength):
    color = ImageEnhance.Color(img)
    img = color.enhance(1.0 + 0.5 * strength)
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 + 0.35 * strength)
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(1.0 + 0.6 * strength)
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 - 0.05 * strength)
    return img


def night_enhance(img, strength):
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 + 0.4 * strength)
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 + 0.2 * strength)
    # Reduce noise with slight blur
    img = img.filter(ImageFilter.GaussianBlur(radius=0.4 * strength))
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(1.0 + 0.8 * strength)
    color = ImageEnhance.Color(img)
    img = color.enhance(1.0 + 0.1 * strength)
    return img


def vintage_enhance(img, strength):
    # Warm tone
    color = ImageEnhance.Color(img)
    img = color.enhance(0.7 - 0.1 * strength)
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 + 0.05 * strength)
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(0.85 + 0.05 * strength)
    # Sepia tint
    r, g, b = img.split()
    r = r.point(lambda i: min(255, i + int(30 * strength)))
    b = b.point(lambda i: max(0, i - int(20 * strength)))
    img = Image.merge("RGB", (r, g, b))
    return img


def bw_enhance(img, strength):
    img = ImageOps.grayscale(img).convert("RGB")
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 + 0.5 * strength)
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 + 0.05 * strength)
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(1.0 + 0.4 * strength)
    return img


def hdr_enhance(img, strength):
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 + 0.5 * strength)
    color = ImageEnhance.Color(img)
    img = color.enhance(1.0 + 0.4 * strength)
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(1.0 + 0.6 * strength)
    # Edge enhancement for HDR pop
    img = img.filter(ImageFilter.EDGE_ENHANCE)
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 - 0.05 * strength)
    return img


def softglow_enhance(img, strength):
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.0 + 0.1 * strength)
    # Glow layer
    glow = img.filter(ImageFilter.GaussianBlur(radius=3 * strength))
    # Blend original with glow
    img = Image.blend(img, glow, alpha=0.3 * strength)
    color = ImageEnhance.Color(img)
    img = color.enhance(1.0 + 0.15 * strength)
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.0 - 0.05 * strength)
    return img


ENHANCERS = {
    "Auto Enhance":  auto_enhance,
    "Sharpen":       sharpen_enhance,
    "Vivid Colors":  vivid_enhance,
    "Portrait":      portrait_enhance,
    "Landscape":     landscape_enhance,
    "Night Mode":    night_enhance,
    "Vintage":       vintage_enhance,
    "Black & White": bw_enhance,
    "HDR Effect":    hdr_enhance,
    "Soft Glow":     softglow_enhance,
}


def enhance_image(img_bytes, enhancement, intensity_name):
    strength = INTENSITIES[intensity_name]
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # Upscale small images for better quality output
    w, h = img.size
    if max(w, h) < 800:
        scale = 800 / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    enhancer_fn = ENHANCERS[enhancement]
    img = enhancer_fn(img, strength)

    # Clamp pixel values
    img = img.convert("RGB")

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out.read()


# ---- Bot flow ----

def send_enhancement_picker(cid):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(name, callback_data=f"enh:{name}")
        for name in ENHANCEMENTS
    ]
    markup.add(*buttons)
    bot.send_message(
        cid,
        "✨ *Step 2 — Choose an enhancement:*",
        parse_mode="Markdown",
        reply_markup=markup,
    )


def send_intensity_picker(cid):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("🌤 Light", callback_data="intensity:Light"),
        types.InlineKeyboardButton("⚡ Medium", callback_data="intensity:Medium"),
        types.InlineKeyboardButton("🔥 Strong", callback_data="intensity:Strong"),
    )
    bot.send_message(
        cid,
        "🎚 *Step 3 — Choose intensity:*",
        parse_mode="Markdown",
        reply_markup=markup,
    )


@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    cid = message.chat.id
    text = (
        "🔔បើកអាខោនឥឡូវនេះ ថែមជូន100% ភ្លាមៗ!🚦\n\n"
        "🔗បង្កើតអាខោន: https://t.me/S8888_TTB\n\n"
        "💎ទំនុកចិត្ត សេវាកម្ម ទាន់ចិត្ត 24ម៉ោង⏰\n"
        "🎲អតិថិជនទទួលសំណាងធំៗរាល់ថ្ងៃ: $1,000 $3,500 $15,000 $100,000\n\n"
        "🎰 មានហ្គេមកម្សាន្តជាច្រើន:\n"
        "🔔មាន់ជល់SB24 / មាន់ជល់V99 / ខ្លាឃ្លោកខ្មែរ / បាល់SBC369"
    )
    image_url = "https://freeimage.host/i/Cg9fFbR"
    try:
        bot.send_photo(cid, image_url, caption=text)
    except Exception:
        bot.send_message(cid, text)
    bot.send_message(
        cid,
        "📸 *AI Photo Enhancer Bot*\n\n"
        "I'll enhance your photos using smart filters!\n\n"
        "10 enhancement modes:\n"
        "Auto · Sharpen · Vivid · Portrait · Landscape\n"
        "Night · Vintage · B&W · HDR · Soft Glow\n\n"
        "Send /enhance to start!",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["enhance"])
def cmd_enhance(message):
    cid = message.chat.id
    user_sessions[cid] = {"step": "photo"}
    bot.send_message(
        cid,
        "📸 *Step 1 — Send your photo:*\n"
        "_(send as a file for best quality)_",
        parse_mode="Markdown",
    )


@bot.message_handler(
    content_types=["photo", "document"],
    func=lambda m: user_sessions.get(m.chat.id, {}).get("step") == "photo",
)
def handle_photo(message):
    cid = message.chat.id
    session = user_sessions.get(cid, {})
    try:
        if message.content_type == "photo":
            file_id = message.photo[-1].file_id
        else:
            if not message.document.mime_type.startswith("image/"):
                bot.send_message(cid, "⚠️ Please send an image file.")
                return
            file_id = message.document.file_id

        file_info = bot.get_file(file_id)
        img_bytes = bot.download_file(file_info.file_path)
        session["img_bytes"] = img_bytes
        session["step"] = "enhancement"
        bot.send_message(cid, "✅ Photo received!")
        send_enhancement_picker(cid)

    except Exception as e:
        logger.exception("Photo error")
        bot.send_message(cid, f"❌ Error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("enh:"))
def handle_enhancement(call):
    cid = call.message.chat.id
    enh = call.data.split(":", 1)[1]
    session = user_sessions.setdefault(cid, {})
    session["enhancement"] = enh
    session["step"] = "intensity"
    bot.answer_callback_query(call.id, f"{enh} selected!")
    bot.edit_message_text(
        f"✅ Enhancement: *{enh}*\n_{ENHANCEMENTS[enh]['desc']}_",
        cid, call.message.message_id, parse_mode="Markdown",
    )
    send_intensity_picker(cid)


@bot.callback_query_handler(func=lambda call: call.data.startswith("intensity:"))
def handle_intensity(call):
    cid = call.message.chat.id
    intensity = call.data.split(":")[1]
    session = user_sessions.setdefault(cid, {})
    session["intensity"] = intensity
    session["step"] = "done"
    bot.answer_callback_query(call.id, f"{intensity} intensity selected!")
    bot.edit_message_text(
        f"✅ Intensity: *{intensity}*",
        cid, call.message.message_id, parse_mode="Markdown",
    )
    generate_photo(cid)


def generate_photo(cid):
    session = user_sessions.get(cid, {})
    img_bytes = session.get("img_bytes")
    enhancement = session.get("enhancement", "Auto Enhance")
    intensity = session.get("intensity", "Medium")

    msg = bot.send_message(cid, "⏳ Enhancing your photo…")
    try:
        result = enhance_image(img_bytes, enhancement, intensity)
        bot.send_photo(
            cid,
            result,
            caption=(
                f"✅ *Enhanced!*\n\n"
                f"Mode: {enhancement}\n"
                f"Intensity: {intensity}\n\n"
                f"Send /enhance to enhance another photo!"
            ),
            parse_mode="Markdown",
        )
        bot.delete_message(cid, msg.message_id)
    except Exception as e:
        logger.exception("Enhancement error")
        bot.send_message(cid, f"❌ Failed: {e}")


@bot.message_handler(commands=["cancel"])
def cmd_cancel(message):
    cid = message.chat.id
    user_sessions.pop(cid, None)
    bot.send_message(cid, "❌ Cancelled. Send /enhance to start over.")


if __name__ == "__main__":
    logger.info("AI Photo Enhancer bot starting…")
    bot.infinity_polling()
