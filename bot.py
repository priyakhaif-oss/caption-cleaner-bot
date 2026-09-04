import os
import re
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Default గా కింద యాడ్ అవ్వాల్సిన మెసేజ్
user_custom_caption = "\n\n🔥 Join: @YourChannelName"

# మీరు ఇచ్చిన అన్‌వాంటెడ్ పేర్ల లిస్ట్
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

# పెద్ద పేర్లను ముందు రిమూవ్ చేసేలా సార్ట్ చేసి కంపైల్ చేయడం
SORTED_PREFIXES = sorted(RAW_PREFIXES, key=len, reverse=True)
PATTERN = re.compile("|".join(re.escape(p) for p in SORTED_PREFIXES), re.IGNORECASE)

app = Client("caption_editor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 1. మీకు నచ్చినప్పుడు టెక్స్ట్‌ని మార్చుకోవడానికి కమాండ్
@app.on_message(filters.command("setcaption") & filters.private)
async def set_custom_caption(client: Client, message: Message):
    global user_custom_caption
    if len(message.command) < 2:
        await message.reply_text("ఎలా వాడాలి:\n`/setcaption మీ మెసేజ్ లేదా లింక్స్ ఇక్కడ రాయండి`")
        return
    
    # /setcaption తర్వాత మీరు ఇచ్చిన టెక్స్ట్ మొత్తాన్ని సేవ్ చేసుకుంటుంది
    user_custom_caption = "\n\n" + message.text.split(None, 1)[1]
    await message.reply_text("✅ మీ కస్టమ్ మెసేజ్ సేవ్ అయింది! ఇకపై వచ్చే ఫైల్స్‌కి కింద ఇదే యాడ్ అవుతుంది.")

# 2. ఫైల్స్ వచ్చినప్పుడు ప్రాసెస్ చేసే భాగం
@app.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def forward_with_cleaned_caption(client: Client, message: Message):
    old_caption = message.caption or ""
    
    # లిస్ట్‌లో ఉన్న చెత్త పేర్లను తొలగిస్తుంది
    cleaned_caption = PATTERN.sub("", old_caption)
    
    # ఖాళీ స్పేస్‌లు, లైన్లు క్లీన్ చేయడం
    cleaned_caption = re.sub(r"[ \t]+", " ", cleaned_caption)
    cleaned_caption = re.sub(r"\n\s*\n+", "\n\n", cleaned_caption).strip()
    
    # ఫ్లో: పాత క్యాప్షన్ + మీరు ఇచ్చిన మెసేజ్
    if cleaned_caption:
        final_caption = f"{cleaned_caption}{user_custom_caption}"
    else:
        final_caption = user_custom_caption.strip()

    # 0 Download: సర్వర్‌కి రాకుండా నేరుగా టెలిగ్రామ్ టు టెలిగ్రామ్ కాపీ
    await message.copy(
        chat_id=message.chat.id,
        caption=final_caption
    )

app.run()
