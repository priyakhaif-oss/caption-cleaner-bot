import os
import re
import logging
from pyrogram import Client, filters, idle
from pyrogram.types import Message, BotCommand

# ----------------- LOGGING SETUP -----------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

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

SORTED_PREFIXES = sorted(RAW_PREFIXES, key=len, reverse=True)
PATTERN = re.compile("|".join(re.escape(prefix) for prefix in SORTED_PREFIXES), re.IGNORECASE)

# Session tracking: user_id -> {"state": "COLLECTING" | "WAITING_TEXT", "files": [Message]}
user_sessions = {}

app = Client("caption_editor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = PATTERN.sub("", text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
    return cleaned.strip()


def get_file_name(message: Message) -> str:
    if message.document and message.document.file_name:
        return clean_text(message.document.file_name)
    elif message.video and message.video.file_name:
        return clean_text(message.video.file_name)
    elif message.audio and message.audio.file_name:
        return clean_text(message.audio.file_name)
    return ""


# ----------------- COMMAND HANDLERS -----------------
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    user_sessions[user_id] = {"state": "COLLECTING", "files": []}
    logger.info(f"User {user_id} started the bot session.")

    welcome_text = (
        "👋 **Welcome to Auto Caption Editor Bot!**\n\n"
        "📤 **Step 1:** Forward or send your file(s) here (single file or multiple files up to 100+).\n"
        "⚡ All unwanted usernames, channels, and tags will be removed automatically.\n\n"
        "👉 When you finish sending all your files, click /done to set your custom caption."
    )
    await message.reply_text(welcome_text)


@app.on_message(filters.command("done") & filters.private)
async def done_handler(client: Client, message: Message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session or not session.get("files"):
        await message.reply_text("⚠️ No files found in queue. Please send or forward your files first!")
        return

    session["state"] = "WAITING_TEXT"
    file_count = len(session["files"])
    logger.info(f"User {user_id} queued {file_count} files. Waiting for custom text input.")

    prompt_text = (
        f"✅ **Received {file_count} file(s)!**\n\n"
        "✍️ **Step 2:** Now send the message/links you want to add.\n"
        "The bot will combine:\n"
        "`[File Name] + [Cleaned Caption] + [Your Message]`\n\n"
        "Reply with your text now, or send /cancel to abort."
    )
    await message.reply_text(prompt_text)


@app.on_message(filters.command("cancel") & filters.private)
@app.on_message(filters.command("clear") & filters.private)
async def cancel_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    logger.info(f"Session cleared for user {user_id}.")
    await message.reply_text("🗑️ **Queue cleared.** Send /start whenever you want to begin again.")


# ----------------- FILE HANDLER -----------------
@app.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def file_collector(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {"state": "COLLECTING", "files": []}

    session = user_sessions[user_id]
    if session["state"] == "WAITING_TEXT":
        session["state"] = "COLLECTING"

    session["files"].append(message)
    total_files = len(session["files"])
    logger.info(f"User {user_id} added file #{total_files} to queue.")

    if total_files == 1:
        await message.reply_text(
            "📥 **File added to queue!**\n"
            "You can keep sending more files. Once finished, click /done."
        )
    elif total_files % 10 == 0:
        await message.reply_text(f"📥 **{total_files} files queued so far.** Click /done when ready.")


# ----------------- TEXT HANDLER -----------------
@app.on_message(filters.text & filters.private & ~filters.command(["start", "done", "cancel", "clear"]))
async def custom_text_processor(client: Client, message: Message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session or session.get("state") != "WAITING_TEXT":
        await message.reply_text("ℹ️ Please send your files first, or type /start to restart.")
        return

    user_append_text = message.text.strip()
    files_to_process = session.get("files", [])
    total = len(files_to_process)

    status_msg = await message.reply_text(f"⚡ **Processing {total} file(s)... Please wait.**")
    logger.info(f"Processing {total} files for user {user_id}...")

    success_count = 0
    for idx, file_msg in enumerate(files_to_process, start=1):
        try:
            filename = get_file_name(file_msg)
            original_caption = clean_text(file_msg.caption or "")

            caption_parts = []
            if filename:
                caption_parts.append(filename)
            if original_caption:
                caption_parts.append(original_caption)
            if user_append_text:
                caption_parts.append(user_append_text)

            final_caption = "\n\n".join(caption_parts)

            await file_msg.copy(
                chat_id=message.chat.id,
                caption=final_caption
            )
            success_count += 1

        except Exception as e:
            logger.error(f"Error copying file #{idx} for user {user_id}: {e}")

    del user_sessions[user_id]

    await status_msg.edit_text(
        f"🎉 **Done! Successfully processed and delivered {success_count}/{total} file(s).**\n\n"
        "Send /start anytime to process another batch."
    )
    logger.info(f"Completed batch of {success_count} files for user {user_id}.")


# ----------------- STARTUP & KEEP-ALIVE -----------------
async def main():
    await app.start()
    logger.info("==========================================")
    logger.info("🤖 Auto Caption Editor Bot is ONLINE & RUNNING!")
    logger.info("⚡ Zero-download instant forward mode active.")
    logger.info("==========================================")

    await app.set_bot_commands([
        BotCommand("start", "Start the bot and send files"),
        BotCommand("done", "Done sending files & set your message"),
        BotCommand("cancel", "Cancel current queue"),
        BotCommand("clear", "Clear queued files")
    ])
    logger.info("✅ Menu commands registered successfully.")

    # Bot aagipokunda continuous ga wait chesela idle() pettadam jarigindi
    await idle()
    await app.stop()


if __name__ == "__main__":
    app.run(main())
