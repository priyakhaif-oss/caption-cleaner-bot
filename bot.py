import os
import re
import logging
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.types import Message, BotCommand

# ----------------- LOGGING SETUP -----------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

# ----------------- DUMMY FLASK WEB SERVER FOR RENDER -----------------
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

# ----------------- UNWANTED PREFIXES / USERNAMES -----------------
RAW_PREFIXES = [
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
    "@HollyMovies4_",
    "@HollyMovies4_ ",
    "@HollyMovies4 - ",
    "@HollyMovies4",
    "@TGCinemasworld -",
    "@TGCinemasworld - ",
    "@TGCinemasworld_",
    "@TGCinemasworld",
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

# Sort by length descending for clean regex match
SORTED_PREFIXES = sorted(RAW_PREFIXES, key=len, reverse=True)
PATTERN = re.compile("|".join(re.escape(prefix) for prefix in SORTED_PREFIXES), re.IGNORECASE)

# User sessions: user_id -> {"state": "COLLECTING" | "WAITING_TEXT", "files": [Message]}
user_sessions = {}

app = Client("caption_editor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def clean_text(text: str) -> str:
    """Removes blacklisted words and cleans excess spaces."""
    if not text:
        return ""
    cleaned = PATTERN.sub("", text)
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
        "👋 **Welcome to Auto Caption Editor Bot!**\n\n"
        "📤 **Step 1:** Send or forward your file(s) here (1 or 100+ files).\n"
        "⚡ All unwanted links and usernames will be cleaned automatically.\n\n"
        "👉 Once you finish sending files, send /done to proceed."
    )
    await message.reply_text(welcome_text)


@app.on_message(filters.command("done") & filters.private)
async def done_handler(client: Client, message: Message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session or not session.get("files"):
        await message.reply_text("⚠️ No files in queue! Please send or forward your files first.")
        return

    session["state"] = "WAITING_TEXT"
    file_count = len(session["files"])
    logger.info(f"User {user_id} submitted {file_count} files for captioning.")

    prompt_text = (
        f"✅ **Received {file_count} file(s) in total!**\n\n"
        "✍️ **Step 2:** Now send the text / links / username you want to append.\n\n"
        "👉 Flow: `[Original Cleaned Caption] + [Your Message]`\n"
        "Send your message now (or send /cancel to reset)."
    )
    await message.reply_text(prompt_text)


@app.on_message(filters.command("cancel") & filters.private)
@app.on_message(filters.command("clear") & filters.private)
async def cancel_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    logger.info(f"Session cleared for user {user_id}.")
    await message.reply_text("🗑️ **Queue cleared.** Send your files or type /start to begin fresh.")


# ----------------- FILE HANDLER (NO SPAM) -----------------
@app.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def file_collector(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {"state": "COLLECTING", "files": []}

    session = user_sessions[user_id]
    if session["state"] == "WAITING_TEXT":
        session["state"] = "COLLECTING"

    # Silently queue the file - NO SPAM REPLIES on every forward
    session["files"].append(message)
    logger.info(f"User {user_id} queued file #{len(session['files'])}")


# ----------------- TEXT HANDLER & SENDER -----------------
@app.on_message(filters.text & filters.private & ~filters.command(["start", "done", "cancel", "clear"]))
async def custom_text_processor(client: Client, message: Message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    # Ignore random text if user didn't hit /done
    if not session or session.get("state") != "WAITING_TEXT":
        await message.reply_text("ℹ️ Forward your files first, then click /done when finished.")
        return

    user_append_text = message.text.strip()
    files_to_process = session.get("files", [])
    total = len(files_to_process)

    status_msg = await message.reply_text(f"⚡ **Processing and delivering {total} file(s)...**")
    logger.info(f"Processing {total} files for user {user_id}...")

    success_count = 0
    for idx, file_msg in enumerate(files_to_process, start=1):
        try:
            # Clean unwanted usernames & prefixes from the original caption
            original_caption = clean_text(file_msg.caption or "")

            # Flow: Cleaned Caption + User Custom Text
            caption_parts = []
            if original_caption:
                caption_parts.append(original_caption)
            if user_append_text:
                caption_parts.append(user_append_text)

            final_caption = "\n\n".join(caption_parts)

            # Instant zero-download forward
            await file_msg.copy(
                chat_id=message.chat.id,
                caption=final_caption
            )
            success_count += 1

        except Exception as e:
            logger.error(f"Error forwarding file #{idx} for user {user_id}: {e}")

    # Clear user session after batch is complete
    del user_sessions[user_id]

    await status_msg.edit_text(
        f"🎉 **Complete! Successfully sent {success_count}/{total} file(s).**\n\n"
        "Forward more files anytime and click /done."
    )
    logger.info(f"Completed batch of {success_count} files for user {user_id}.")


# ----------------- STARTUP & KEEP-ALIVE -----------------
async def main():
    # Start Flask Web Server in background for Render port binding
    keep_alive()
    logger.info("🌐 Flask Web Server started for Render health check.")

    await app.start()
    logger.info("==========================================")
    logger.info("🤖 Auto Caption Editor Bot is ONLINE & RUNNING!")
    logger.info("⚡ Zero-download instant forward mode active.")
    logger.info("==========================================")

    # Set Telegram Menu Button commands (3 lines)
    await app.set_bot_commands([
        BotCommand("start", "Start the bot and send files"),
        BotCommand("done", "Done sending files & set your message"),
        BotCommand("cancel", "Cancel current queue"),
        BotCommand("clear", "Clear queued files")
    ])
    logger.info("✅ Menu commands registered successfully.")

    # Keep bot active
    await idle()
    await app.stop()


if __name__ == "__main__":
    app.run(main())
