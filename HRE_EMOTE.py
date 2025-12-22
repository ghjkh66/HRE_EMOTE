import telebot
import threading
import time
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
BOT_TOKEN = "8267081286:AAGxj6FK7E1XsKGZFgUJsH9GyxRL9bXwU10"
bot = telebot.TeleBot(BOT_TOKEN)

ADMINS = [7486456672]
BOT_LOCKED = False
STOP_FLAGS = {}

# ================= NORMAL EMOTES (NO EVO) =================
EMOTE_IDS = [
    "909051014","909050009","909051013","909051012","909051010",
    "909051004","909051002","909051001","909048015","909044015",
    "909041008","909049003","909050008","909049001","909041013",
    "909050014","909050015","909050002","909042007","909050028",
    "909049012","909000045","909000034","909000012","909000020",
    "909000008","909000006","909000014","909000010","909038004",
    "909034001","909049017","909040004","909041003","909041012"
]

# ================= EVO EMOTES =================
EVO_EMOTE_IDS = [
    "909051003","909033002","909041005","909038010","909039011",
    "909040010","909000081","909000085","909000063","909000075",
    "909033001","909000090","909000068","909000098","909035007",
    "909035012","909038012","909037011","909042008"
]

# ================= ADMIN KEYBOARD =================
def admin_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔒 Lock" if not BOT_LOCKED else "🔓 Unlock", callback_data="lock"),
        InlineKeyboardButton("🛑 Stop All", callback_data="stop_all")
    )
    return kb

# ================= START / ADMIN =================
@bot.message_handler(commands=['start','admin'])
def start_cmd(m):
    global BOT_LOCKED
    if m.chat.type == "private" and m.from_user.id in ADMINS:
        BOT_LOCKED = False
        STOP_FLAGS.clear()
        bot.send_message(m.chat.id, "👑 ADMIN PANEL", reply_markup=admin_kb())
    else:
        bot.reply_to(
            m,
            "👋 Welcome\n\n"
            "/emote <TC> <UID> HRE\n"
            "/fast <TC> <UID> HRE\n"
            "/evo <TC> <UID> HRE\n"
            "/evo fast <TC> <UID> HRE\n"
            "/stop <UID>"
        )

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    global BOT_LOCKED
    if c.from_user.id not in ADMINS:
        return bot.answer_callback_query(c.id, "❌ Admin only")

    if c.data == "lock":
        BOT_LOCKED = not BOT_LOCKED
    elif c.data == "stop_all":
        for k in STOP_FLAGS:
            STOP_FLAGS[k] = True

    bot.edit_message_reply_markup(
        c.message.chat.id,
        c.message.message_id,
        reply_markup=admin_kb()
    )
    bot.answer_callback_query(c.id, "✅ Done")

# ================= WORKERS =================
def emote_worker(chat, tc, uid, delay, emote_list, tag):
    STOP_FLAGS[str(uid)] = False
    count = 0

    for e in emote_list:
        if STOP_FLAGS.get(str(uid)):
            break
        try:
            url = f"https://epapi-ytxx.onrender.com/join?tc={tc}&uid1={uid}&emote_id={e}"
            requests.get(url, timeout=10)
            bot.send_photo(
                chat,
                f"https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG/{e}.png",
                caption=f"{tag} {e}"
            )
            count += 1
        except:
            pass
        time.sleep(delay)

    bot.send_message(chat, f"✅ DONE\nTotal: {count}")
    STOP_FLAGS.pop(str(uid), None)

def start_thread(chat, tc, uid, delay, emotes, tag):
    threading.Thread(
        target=emote_worker,
        args=(chat, tc, uid, delay, emotes, tag)
    ).start()

# ================= NORMAL COMMANDS =================
@bot.message_handler(commands=['emote'])
def emote_cmd(m):
    if BOT_LOCKED and m.from_user.id not in ADMINS:
        return bot.reply_to(m, "🔒 Bot locked")

    a = m.text.split()
    if len(a) != 4 or a[3].upper() != "HRE":
        return bot.reply_to(m, "❌ /emote TC UID HRE")

    start_thread(m.chat.id, a[1], a[2], 5, EMOTE_IDS, "🎭")

@bot.message_handler(commands=['fast'])
def fast_cmd(m):
    if BOT_LOCKED and m.from_user.id not in ADMINS:
        return bot.reply_to(m, "🔒 Bot locked")

    a = m.text.split()
    if len(a) != 4 or a[3].upper() != "HRE":
        return bot.reply_to(m, "❌ /fast TC UID HRE")

    start_thread(m.chat.id, a[1], a[2], 1, EMOTE_IDS, "⚡")

# ================= EVO COMMANDS =================
@bot.message_handler(commands=['evo'])
def evo_cmd(m):
    if BOT_LOCKED and m.from_user.id not in ADMINS:
        return bot.reply_to(m, "🔒 Bot locked")

    a = m.text.split()

    # /evo fast TC UID HRE
    if len(a) == 5 and a[1].lower() == "fast" and a[4].upper() == "HRE":
        start_thread(m.chat.id, a[2], a[3], 1, EVO_EMOTE_IDS, "🔥 EVO FAST")
        return

    # /evo TC UID HRE
    if len(a) == 4 and a[3].upper() == "HRE":
        start_thread(m.chat.id, a[1], a[2], 5, EVO_EMOTE_IDS, "🔥 EVO")
        return

    bot.reply_to(m, "❌ Use:\n/evo TC UID HRE\n/evo fast TC UID HRE")

# ================= STOP =================
@bot.message_handler(commands=['stop'])
def stop_cmd(m):
    uid = m.text.split()[1] if len(m.text.split()) == 2 else str(m.from_user.id)
    if uid in STOP_FLAGS:
        STOP_FLAGS[uid] = True
        bot.reply_to(m, "🛑 Stopping…")
    else:
        bot.reply_to(m, "⚠️ No active process")

# ================= RUN =================
print("🔥 BOT RUNNING")
bot.infinity_polling(skip_pending=True)