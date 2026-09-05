import os
import re
import logging
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.types import Message, BotCommand
from pyrogram.enums import ParseMode

# ----------------- LOGGING SETUP -----------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

# ----------------- FLASK WEB SERVER FOR RENDER -----------------
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running healthy & live 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

# ----------------- CONFIGURATION -----------------
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ----------------- DEFAULT BASE PREFIXES -----------------
DEFAULT_PREFIXES = [
    "@VGCinemas_off",
    "www.1TamilBlasters.tel",
    "HollywoodGbs_",
    "@HollywoodGbs_",
    "[TF]",
    "@ViewCinemas_",
    "@ViewCinemas",
    "@WayneEntertainment - ",
    "@WayneEntertainment_",
    "@WayneEntertainment ",
    "@WaynEntertainment - ",
    "@WaynEntertainment",
    "@Gangz7 - ",
    "@Gangz7 ",
    "@Gangz7",
    "@Gangz7_",
    "@PrakyTV - ",
    "@PrakyTV -",
    "@PrakyTV",
    "@PrakyTV ",
    "@PH_FILES",
    "@NaChannel4 -",
    "@NaChannel4 - ",
    "@NaChannel4 - - ",
    "@NaChannel4 -- ",
    "@NaChannel4 - -",
    "@TollyMovies_Official -",
    "@TollyMovies_Official - ",
    "@TollyMovies_Official -",
    "[@MOVIES_HUNT]",
    "@TBOriginals_",
    "@CINEMA_BEACON",
    "@CV",
    "HollywoodGbs - ",
    "HollywoodGbs -",
    "HollywoodGbs",
    "@Movies_arena_4u_",
    "@TG_Movies4u ",
    "@TG_Movies4u_",
    "@TG_Movies4u - ",
    "@TG_Movies4u  - ",
    "@TG_Movies4u  -",
    "@TG_Movies - ",
    "@TG_Movies -",
    "@TG_Movies4u -",
    "@Tg_Movies4u --",
    "@TG_Movies4u -- ",
    "@Tg_Movies4u - ",
    "@Tg_Movies4u -- ",
    "@tg_movies4u - ",
    "@CR7XPRAJITH ",
    "@CR7XPRAJITH  ",
    "@CR7XPRAJITH",
    "[FC]",
    "@PrankyTv",
    "@MJ_Linkz",
    "@MM_X265",
    "@TroopOriginals_",
    "@VGCINEMAS_",
    "@VGCINEMAS",
    "_@VGCINEMAS2_",
    "@VGCinemas_ofcl_",
    "@VGCinemas_Ofcl",
    "@telugu_moviez_",
    "@Filmyzone4u_",
    "@NDLMoviee_",
    "@KumarValimaiofcl_",
    "@S95Hub",
    "@S95files_",
    "@S95files - ",
    "@MnA_Movies_",
    "@WayneEntertainment",
    "@MULTIVERSE_OFCL",
    "mj_link_4u_",
    "mj_link_4u",
    "@SGCINEMAS",
    "@mj_link_4u_",
    "@mj_link_4u",
    "[CF]",
    "@CC_X265",
    "_mx_",
    "www_3MovieRulz_mx_",
    "@toonflexpage - ",
    "@toonflexpage",
    "toonflex - ",
    "toonflex",
    "Toonfelx - ",
    "Toonflex",
    "@Anu_movies_",
    "@Anu_movies - ",
    "@Anu_movies",
    "@TrollerMawaofficial_",
    "@MM_",
    "[MP]",
]

active_prefixes = set(DEFAULT_PREFIXES)
compiled_pattern = None

def rebuild_pattern():
    """Sorts and compiles regex safely."""
    global compiled_pattern
    sorted_list = sorted(list(active_prefixes), key=len, reverse=True)
    compiled_pattern = re.compile("|".join(re.escape(p) for p in sorted_list), re.IGNORECASE)

rebuild_pattern()

user_sessions = {}

app = Client("caption_editor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def clean_text(text: str) -> str:
    """Removes all prefixes and cleans excess whitespace."""
    if not text:
        return ""
    cleaned = compiled_pattern.sub("", text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
    return cleaned.strip()


# ----------------- COMMAND HANDLERS -----------------
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    user_sessions[user_id] = {"state": "COLLECTING", "files": []}
    logger.info(f"User {user_id} started session.")

    welcome_text = (
        "👋 Welcome to Auto Caption Editor Bot!\n\n"
        "📤 Step 1: Send or forward your file(s) here (1 or 100+ files).\n"
        "⚡ All unwanted usernames, channels, and links will be removed automatically.\n\n"
        "👉 When finished sending all files, send /done to set your custom text.\n\n"
        "⚙️ Prefix Management:\n"
        "• /addprefix <prefixes> - Add new prefixes in bulk\n"
        "• /prefixes - Check count of clean prefixes"
    )
    await message.reply_text(welcome_text, parse_mode=ParseMode.DISABLED)


@app.on_message(filters.command("addprefix") & filters.private)
async def add_prefix_handler(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        usage_text = (
            "ℹ️ How to add prefixes:\n\n"
            "Format 1:\n/addprefix @Channel1 @Channel2\n\n"
            "Format 2 (Lines):\n/addprefix\n@Channel1\n@Channel2\nwww.example.com"
        )
        await message.reply_text(usage_text, parse_mode=ParseMode.DISABLED)
        return

    raw_input = ""
    if len(message.command) >= 2:
        raw_input = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        raw_input = message.reply_to_message.text

    new_items = [item.strip() for item in re.split(r"[\r\n\s]+", raw_input) if item.strip()]

    if not new_items:
        await message.reply_text("⚠️ No valid prefixes detected.", parse_mode=ParseMode.DISABLED)
        return

    for item in new_items:
        active_prefixes.add(item)

    rebuild_pattern()
    logger.info(f"Added {len(new_items)} new prefix(es). Total: {len(active_prefixes)}")

    preview = "\n".join([f"• {x}" for x in new_items[:10]])
    more_text = f"\n...and {len(new_items) - 10} more" if len(new_items) > 10 else ""

    await message.reply_text(
        f"✅ Successfully added {len(new_items)} prefix(es) to clean list!\n\n{preview}{more_text}",
        parse_mode=ParseMode.DISABLED
    )


@app.on_message(filters.command("prefixes") & filters.private)
async def list_prefixes_handler(client: Client, message: Message):
    # ParseMode.DISABLED avoids ENTITY_BOUNDS_INVALID caused by markdown syntax collisions
    total = len(active_prefixes)
    await message.reply_text(
        f"📋 Total cleanable prefixes loaded: {total}\n\n"
        "You can add more anytime using /addprefix <prefix1> <prefix2>",
        parse_mode=ParseMode.DISABLED
    )


@app.on_message(filters.command("done") & filters.private)
async def done_handler(client: Client, message: Message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session or not session.get("files"):
        await message.reply_text("⚠️ No files in queue! Please send or forward your files first.", parse_mode=ParseMode.DISABLED)
        return

    session["state"] = "WAITING_TEXT"
    file_count = len(session["files"])
    logger.info(f"User {user_id} queued {file_count} files.")

    prompt_text = (
        f"✅ Received {file_count} file(s) in queue!\n\n"
        "✍️ Step 2: Now send the text/links you want to append to the caption.\n\n"
        "Flow: [Cleaned Caption] + [Your Message]\n"
        "Send your message now (or send /cancel to reset)."
    )
    await message.reply_text(prompt_text, parse_mode=ParseMode.DISABLED)


@app.on_message(filters.command("cancel") & filters.private)
@app.on_message(filters.command("clear") & filters.private)
async def cancel_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    logger.info(f"Session cleared for user {user_id}.")
    await message.reply_text("🗑️ Queue cleared. Send files or type /start to begin again.", parse_mode=ParseMode.DISABLED)


# ----------------- FILE HANDLER (ZERO SPAM) -----------------
@app.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def file_collector(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {"state": "COLLECTING", "files": []}

    session = user_sessions[user_id]
    if session["state"] == "WAITING_TEXT":
        session["state"] = "COLLECTING"

    session["files"].append(message)
    logger.info(f"User {user_id} queued file #{len(session['files'])}")


# ----------------- TEXT HANDLER & SENDER -----------------
@app.on_message(filters.text & filters.private & ~filters.command(["start", "done", "cancel", "clear", "addprefix", "prefixes"]))
async def custom_text_processor(client: Client, message: Message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session or session.get("state") != "WAITING_TEXT":
        await message.reply_text("ℹ️ Forward your files first, then click /done when finished.", parse_mode=ParseMode.DISABLED)
        return

    user_append_text = message.text.strip()
    files_to_process = session.get("files", [])
    total = len(files_to_process)

    status_msg = await message.reply_text(f"⚡ Processing and delivering {total} file(s)...", parse_mode=ParseMode.DISABLED)
    logger.info(f"Delivering {total} files for user {user_id}...")

    success_count = 0
    for idx, file_msg in enumerate(files_to_process, start=1):
        try:
            original_caption = clean_text(file_msg.caption or "")

            caption_parts = []
            if original_caption:
                caption_parts.append(original_caption)
            if user_append_text:
                caption_parts.append(user_append_text)

            final_caption = "\n\n".join(caption_parts)

            # Direct server-to-server zero download copy
            await file_msg.copy(
                chat_id=message.chat.id,
                caption=final_caption
            )
            success_count += 1

        except Exception as e:
            logger.error(f"Error forwarding file #{idx} for user {user_id}: {e}")

    del user_sessions[user_id]

    await status_msg.edit_text(
        f"🎉 Complete! Successfully delivered {success_count}/{total} file(s).\n\n"
        "Forward more files anytime and click /done.",
        parse_mode=ParseMode.DISABLED
    )
    logger.info(f"Completed batch delivery of {success_count} files for user {user_id}.")


# ----------------- STARTUP & KEEP-ALIVE -----------------
async def main():
    keep_alive()
    logger.info("🌐 Flask Web Server started.")

    await app.start()
    logger.info("==========================================")
    logger.info("🤖 Auto Caption Editor Bot is ONLINE & RUNNING!")
    logger.info("⚡ Zero-download instant forward mode active.")
    logger.info("==========================================")

    await app.set_bot_commands([
        BotCommand("start", "Start session & send files"),
        BotCommand("done", "Finish files & set message"),
        BotCommand("addprefix", "Add prefixes in bulk to clean"),
        BotCommand("prefixes", "Check loaded clean prefixes"),
        BotCommand("cancel", "Cancel current queue"),
        BotCommand("clear", "Clear queued files")
    ])
    logger.info("✅ Menu commands registered successfully.")

    await idle()
    await app.stop()


if __name__ == "__main__":
    app.run(main())
