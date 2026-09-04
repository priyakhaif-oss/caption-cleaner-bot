import os
import re
from pyrogram import Client, filters
from pyrogram.types import Message

# Render లో యాడ్ చేసే Environment variables
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Meeru icchina unwanted list
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

# Words sequence ni sort chesi regex compile cheyadam
SORTED_PREFIXES = sorted(RAW_PREFIXES, key=len, reverse=True)
PATTERN = re.compile("|".join(re.escape(prefix) for prefix in SORTED_PREFIXES), re.IGNORECASE)

# Meeru add cheyyalsina mee channel text (Deenni meeku nachinattu marchukondi)
FOOTER_TEXT = "\n\nJoin: @YourChannelName"

app = Client("caption_editor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def clean_caption(original_text: str) -> str:
    if not original_text:
        return FOOTER_TEXT.strip()
    
    # List lo unna perlu / tags delete chesthundi
    cleaned = PATTERN.sub("", original_text)
    
    # Extra spaces & ఖాళీ లైన్లు సర్దుబాటు చేస్తుంది
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned).strip()
    
    # As it is caption కింద మీ ఛానల్ పేరు పెడుతుంది
    return f"{cleaned}{FOOTER_TEXT}" if cleaned else FOOTER_TEXT.strip()

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def forward_with_new_caption(client: Client, message: Message):
    old_caption = message.caption or ""
    new_caption = clean_caption(old_caption)

    # 0 Download: Telegram లోనే డైరెక్ట్ మెసేజ్ కాపీ అయి కొత్త క్యాప్షన్‌తో వెళ్తుంది
    await message.copy(
        chat_id=message.chat.id,
        caption=new_caption
    )

app.run()
