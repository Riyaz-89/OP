import os
import re
import json
import psutil
import time
import telebot
import telebot
import requests
import pycountry
from telebot import TeleBot, types
from datetime import datetime
from random import randint
from pymongo import MongoClient
from re import split
import urllib3
urllib3.disable_warnings()


BOT_TOKEN = '7572240564:AAGadEivBAcX3ZKbZRWy4tQFv3H5nEENhNY'

ADMIN_ID = "7915760293"
CHANNEL_ID = "-1002384208111"
CHANNEL_LINK = "https://t.me/DariusXP"

MONGO_URI = "mongodb+srv://Riyaz:Riyaz@riyazx.l7hnh.mongodb.net/?retryWrites=true&w=majority&appName=RiyazX"

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["Riyaz"]  # Database name
users_collection = db["users"]  # Collection for users

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# Regex pattern to match card information
CARD_PATTERN = re.compile(r'(\d{15,16})[|/](\d{1,2})[|/](\d{2,4})[|/](\d{3,4})')

# Regex pattern to match email:password
EMAIL_PATTERN = re.compile(r'([\w\.-]+@[\w\.-]+\.\w+):([^\s|]+)')

def extract_emails(text):
    return EMAIL_PATTERN.findall(text)

def get_bot_profile_photo():
    try:
        bot_photos = bot.get_user_profile_photos(bot.get_me().id, limit=1)
        if bot_photos.photos:
            return bot_photos.photos[0][-1].file_id
    except Exception as e:
        print(f"Error getting bot profile photo: {e}")
    return None


def is_user_in_channel(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking channel membership: {e}")
        return False


def force_user_to_join(user_id, message_id=None):
    photo_id = get_bot_profile_photo()
    caption = """
Wᴇʟᴄᴏᴍᴇ Tᴏ Tʜᴇ Aʟʟ Pʀᴇᴍɪᴜᴍ Bᴏᴛ 😊
┏━━━━━━━━━━━━━━━━━⧫
┠ • ɪ ʜᴀᴠᴇ sᴘᴇᴄɪᴀʟ ғᴇᴀᴛᴜʀᴇs.
┠ • ᴀʟʟ-ɪɴ-ᴏɴᴇ ʙᴏᴛ.
┗━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━⧫
┠ • ʏᴏᴜ ᴄᴀɴ ᴄᴄ ɢᴇɴᴇʀᴀᴛᴏʀ ᴛᴏᴏʟs..
┠ • ʏᴏᴜ ᴄᴀɴ ʙɪɴ ᴄʜᴇᴄᴋᴇʀ ᴛᴏᴏʟs..
┠ • ʏᴏᴜ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ sᴋ ᴋᴇʏs ᴛᴏᴏʟs..
┠ • ʏᴏᴜ ᴄᴀɴ ᴛᴇxᴛ ɪɴᴛᴏ ꜰɪʟᴇ ᴛᴏᴏʟs..
┠ • ʏᴏᴜ ᴄᴀɴ ᴄᴄ ᴄʟᴇᴀɴᴇʀ ᴛᴏᴏʟs..
┠ • ᴍᴏʀᴇ ғᴇᴀᴛᴜʀᴇs ɪɴ ᴄᴍᴅ ʙᴜᴛᴛᴏɴ...
┗━━━━━━━━━━━━━━━━━⧫
๏ ᴀꜰᴛᴇʀ ᴊᴏɪɴᴇᴅ ᴘʀᴇss ᴏɴ ᴊᴏɪɴᴇᴅ
ᴄʜᴇᴄᴋ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ...
"""
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=CHANNEL_LINK),
        types.InlineKeyboardButton("ᴄᴏᴍᴍᴀɴᴅ", callback_data="help_info")
    )
    markup.add(types.InlineKeyboardButton("ᴊᴏɪɴᴇᴅ ✅", callback_data="verify_join"))

    if photo_id:
        if message_id:
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo_id, caption=caption),
                chat_id=user_id,
                message_id=message_id,
                reply_markup=markup
            )
        else:
            bot.send_photo(user_id, photo_id, caption=caption, reply_markup=markup)
    else:
        if message_id:
            bot.edit_message_caption(chat_id=user_id, message_id=message_id, caption=caption, reply_markup=markup)
        else:
            bot.send_message(user_id, caption, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join_callback(call):
    try:
        if is_user_in_channel(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ sᴜᴄᴄᴇssꜰᴜʟ", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            show_main_menu(call.from_user.id)
        else:
            bot.answer_callback_query(call.id, "❌ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ꜰɪʀsᴛ!", show_alert=True)
    except Exception as e:
        print(f"Error in verify_join_callback: {e}")
        bot.answer_callback_query(call.id, "⚠️ An error occurred. Please try again.")


@bot.callback_query_handler(func=lambda call: call.data == "help_info")
def help_info_callback(call):
    try:
        help_text = """
━━━━━━━━━━━━━━━━━━
[⌬] 𝗩𝗥𝟭 𝗧𝗼𝗼𝗹𝘀 - 𝗟𝗶𝘃𝗲🌥️ [⌬]
━━━━━━━━━━━━━━━━━━
[✢] 𝗧𝗼𝗼𝗹 → ᴄᴄ ɢᴇɴᴇʀᴀᴛᴏʀ
[✦] 𝗖𝗺𝗻𝗱 → /gen xxx
[✢] 𝗦𝘁𝗮𝘁𝘂𝘀 → ᴀᴄᴛɪᴠᴇ ✅
[✦] 𝗠𝗮𝘀𝘀 → /ɢᴇɴ xxx xxx
━━━━━━━━━━━━━━━━━━
[✢] 𝗧𝗼𝗼𝗹 → ʙɪɴ ᴄʜᴇᴄᴋᴇʀ ✅
[✦] 𝗖𝗺𝗻𝗱 → /bin
[✢] 𝗦𝘁𝗮𝘁𝘂𝘀 → ᴀᴄᴛɪᴠᴇ ✅
[✦] 𝗠𝗮𝘀𝘀 → /ʙɪɴ ʀᴇᴘʟʏ ᴛxᴛ
━━━━━━━━━━━━━━━━━━
[✢] 𝗧𝗼𝗼𝗹 → ᴄʟᴇᴀɴ ᴄᴏᴍʙᴏs ✅
[✦] 𝗖𝗺𝗻𝗱 → /clean
[✢] 𝗦𝘁𝗮𝘁𝘂𝘀 → ᴀᴄᴛɪᴠᴇ ✅
[✦] 𝗠𝗮𝘀𝘀 → /ᴄʟᴇᴀɴ ʀᴇᴘʟʏ
━━━━━━━━━━━━━━━━━━
[✢] 𝗧𝗼𝗼𝗹 → sᴘʟɪᴛ ᴛᴇxᴛ ꜰɪʟᴇs ✅
[✦] 𝗖𝗺𝗻𝗱 → /split
[✢] 𝗦𝘁𝗮𝘁𝘂𝘀 → ᴀᴄᴛɪᴠᴇ ✅
[✦] 𝗠𝗮𝘀𝘀 → /sᴘʟɪᴛ ʀᴇᴘʟʏ
━━━━━━━━━━━━━━━━━━
[✢] 𝗧𝗼𝗼𝗹 → sᴏʀᴛ ᴄᴀʀᴅ ʙʏ ʙʀᴀɴᴅ ✅
[✦] 𝗖𝗺𝗻𝗱 → /sort
[✢] 𝗦𝘁𝗮𝘁𝘂𝘀 → ᴀᴄᴛɪᴠᴇ ✅
[✦] 𝗠𝗮𝘀𝘀 → /sᴏʀᴛ ʀᴇᴘʟʏ
━━━━━━━━━━━━━━━━━━
[✢] 𝗧𝗼𝗼𝗹 → ꜰɪʟᴛᴇʀ ᴄᴀʀᴅs ʙʏ ʙɪɴ ✅
[✦] 𝗖𝗺𝗻𝗱 → /find
[✢] 𝗦𝘁𝗮𝘁𝘂𝘀 → ᴀᴄᴛɪᴠᴇ ✅
[✦] 𝗠𝗮𝘀𝘀 → /ꜰɪɴᴅ xxx ʀᴇᴘʟʏ
━━━━━━━━━━━━━━━━━━
"""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_to_start"))
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=help_text,
            reply_markup=markup, parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error in help_info_callback: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "back_to_start")
def back_to_start_callback(call):
    try:
        force_user_to_join(call.from_user.id, call.message.message_id)
    except Exception as e:
        print(f"Error in back_to_start_callback: {e}")


def show_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if str(user_id) == ADMIN_ID:
        markup.add(
            types.KeyboardButton("💓 Broadcast"),
            types.KeyboardButton("👻 Forwarded"),
            types.KeyboardButton("📥 Import Users"),
            types.KeyboardButton("📤 Export Users"),
            types.KeyboardButton("❌ Delete All Users")
        )
    bot.send_message(user_id, "🎉 ᴛʜᴇ ʙᴏᴛ ʜᴀs ʙᴇᴇɴ ɢʀᴀɴᴛᴇᴅ ᴀᴄᴄᴇss. ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ɪᴛ ɴᴏᴡ. ɪꜰ ʏᴏᴜ ʟᴇᴀᴠᴇ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ, ᴛʜᴇ ʙᴏᴛ's ᴀᴄᴄᴇss ᴡɪʟʟ ʙᴇ ᴅɪsᴀʙʟᴇᴅ!", reply_markup=markup)
    


def country_flag(country_name):  
    try:  
        country = pycountry.countries.search_fuzzy(country_name)[0]  
        alpha_2 = country.alpha_2  
        flag = ''.join(chr(127397 + ord(c)) for c in alpha_2.upper())  
        return f"{country.name.upper()} {flag}"  
    except:  
        return country_name.upper()  

def get_bin_info(bin_code):  
    if len(bin_code) < 6:
        return None

    url = 'http://bins.su/'  
    headers = {  
        'User-Agent': 'Mozilla/5.0',  
        'Content-Type': 'application/x-www-form-urlencoded',  
        'Referer': 'http://bins.su/',  
        'Origin': 'http://bins.su'  
    }  
    payload = {  
        'action': 'searchbins',  
        'bins': bin_code,  
        'bank': '',  
        'country': ''  
    }  

    try:  
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=10)  
        result = response.text  

        if 'No bins found!' in result:  
            return None  

        def extract(text, start, end):  
            return re.search(f'{start}(.*?){end}', text).group(1).strip()  

        bank = extract(result, '<td>Bank</td></tr><tr><td>', '</td>')  
        country = extract(result, f'<td>{bank}</td><td>', '</td>')  
        brand = extract(result, f'<td>{country}</td><td>', '</td>')  
        level = extract(result, f'<td>{brand}</td><td>', '</td>')  
        type_ = extract(result, f'<td>{level}</td><td>', '</td>')  
        bank_name = extract(result, f'<td>{type_}</td><td>', '</td>')  

        return {  
            'bin': bin_code,  
            'brand': brand,  
            'level': level,  
            'type': type_,  
            'country': country,  
            'bank': bank_name  
        }  

    except:  
        return None  

def luhn(card_number):
    digits = [int(d) for d in card_number]
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0

def complete_luhn(base_number):
    for i in range(10):
        trial = base_number + str(i)
        if luhn(trial):
            return trial
    return base_number + '0'

def generate_card(bin_format):
    parts = split(r'[|/@$]', bin_format)
    raw_bin = parts[0].lower()
    exp_m = parts[1] if len(parts) > 1 else ""
    exp_y = parts[2] if len(parts) > 2 else ""
    cvv = parts[3] if len(parts) > 3 else ""

    # Replace letters/x with random digits
    bin_filled = ''.join(str(randint(0, 9)) if c.isalpha() or c == 'x' else c for c in raw_bin)
    while len(bin_filled) < 15:
        bin_filled += str(randint(0, 9))
    bin_filled = bin_filled[:15]

    card = complete_luhn(bin_filled)

    exp_m = exp_m.zfill(2) if exp_m else str(randint(1, 12)).zfill(2)
    exp_y = "20" + exp_y if exp_y and len(exp_y) == 2 else (exp_y if exp_y else str(datetime.now().year + randint(1, 5)))
    cvv = cvv.zfill(3) if cvv and cvv.lower() != "rnd" else str(randint(0, 999)).zfill(3)

    return f"{card}|{exp_m}|{exp_y}|{cvv}"
    
    
    
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
     # Automatically register user if not already registered
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})
    if not is_user_in_channel(user_id):
        force_user_to_join(user_id)
    else:
        show_main_menu(user_id)
        


@bot.message_handler(func=lambda message: message.text.lower().startswith(('/gen', '!gen', '.gen')))
def handle_gen(message):
    user_id = message.from_user.id
    if not is_user_in_channel(user_id):
        force_user_to_join(user_id)
        return  # Only return if user needs to join channel
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❗ Send BIN. Example: `/gen 457173xxxxxxxxxx|05|26|rnd 10`", parse_mode="Markdown")
            return

        bin_input = args[1]
        amount = int(args[2]) if len(args) > 2 else 10
        lookup_bin = re.sub(r'\D', '', bin_input)[:6]

        if len(lookup_bin) < 6:
            bot.reply_to(message, "❌ Invalid BIN.")
            return

        processing = bot.send_message(message.chat.id, "⏳ Generating cards...")

        bin_data = get_bin_info(lookup_bin)
        if not bin_data:
            bot.edit_message_text("❌ BIN not found or site error.", message.chat.id, processing.message_id)
            return

        cards = [generate_card(bin_input) for _ in range(amount)]
        country_full_flag = country_flag(bin_data['country'])

        user = message.from_user
        name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        link = f"tg://user?id={user.id}"

        if amount > 10:
            filename = f"cards_{user.id}.txt"
            with open(filename, "w") as f:
                f.write("\n".join(cards))
            caption = (
                f"<b>[⌬] 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐂𝐂𝐳\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"[↯] 𝐁𝐢𝐧 : <code>{bin_data['bin']}</code> - {bin_data['level']}\n"
                f"[↯] 𝐈𝐧𝐟𝐨 : <code>{bin_data['brand']} - {bin_data['type']}</code>\n"
                f"[↯] 𝐁𝐚𝐧𝐤 : <code>{bin_data['bank']}</code>\n"
                f"[↯] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 : <code>{country_full_flag}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"[✗] 𝐓𝐨𝐭𝐚𝐥 𝐂𝐂𝐳 : <code>{amount}</code>\n"
                f"[✗] 𝐑𝐞𝐪 𝐁𝐲 : <a href='{link}'>{name}</a></b>"
            )
            with open(filename, "rb") as f:
                bot.send_document(message.chat.id, f, caption=caption, parse_mode="HTML")
            bot.delete_message(message.chat.id, processing.message_id)
            os.remove(filename)
        else:
            text_cards = "\n".join(f"`{card}`" for card in cards)
            bot.edit_message_text(
                f"𝗖𝗖 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 ✅\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"𝗕𝗜𝗡 : `{bin_data['bin']}`\n"
                f"𝗔𝗺𝗼𝘂𝗻𝘁 : {amount}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{text_cards}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"𝗜𝗻𝗳𝗼 : {bin_data['brand']} - {bin_data['type']} - {bin_data['level']}\n"
                f"𝗕𝗮𝗻𝗸 : {bin_data['bank']}\n"
                f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country_full_flag}", 
                chat_id=message.chat.id,
                message_id=processing.message_id,
                parse_mode="Markdown"
            )
    except Exception as e:
        bot.edit_message_text(
            f"<b>Error:</b> <code>{str(e)}</code>",
            chat_id=message.chat.id,
            message_id=processing.message_id,
            parse_mode="HTML"
        )

@bot.message_handler(func=lambda message: message.text.lower().startswith(('/bin', '!bin', '.bin')))
def bin_lookup(message):
    user_id = message.from_user.id
    if not is_user_in_channel(user_id):
        force_user_to_join(user_id)
        return  # Only return if user needs to join channel
    
    try:
        bin_list = []

        # If message is a reply to a document
        if message.reply_to_message and message.reply_to_message.document:
            file_id = message.reply_to_message.document.file_id
            file_info = bot.get_file(file_id)
            file = requests.get(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}')
            lines = file.text.strip().splitlines()
            bin_list = [re.sub(r'\D', '', line.strip())[:6] for line in lines if len(re.sub(r'\D', '', line.strip())) >= 6]

        # If message is a reply to text
        elif message.reply_to_message and message.reply_to_message.text:
            lines = message.reply_to_message.text.strip().splitlines()
            bin_list = [re.sub(r'\D', '', line.strip())[:6] for line in lines if len(re.sub(r'\D', '', line.strip())) >= 6]

        # Direct BIN list
        else:
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "<b>[ALERT]</b> <i>Give me a valid BIN or reply to text/file</i>", parse_mode="HTML")
                return
            bin_list = [re.sub(r'\D', '', bin_input)[:6] for bin_input in parts[1:] if len(re.sub(r'\D', '', bin_input)[:6]) >= 6]

        # Remove duplicates by converting to a set and then back to a list
        bin_list = list(set(bin_list))

        # Limit to 100 BINs
        bin_list = bin_list[:100]

        if not bin_list:
            bot.reply_to(message, "<b>[ALERT]</b> <i>No valid BINs found</i>", parse_mode="HTML")
            return

        processing_msg = bot.send_message(message.chat.id, f"⏳ Checking {len(bin_list)} BIN(s)...")

        results_text = []
        results_file = []

        for bin_code in bin_list:
            data = get_bin_info(bin_code)
            if data and data['bank'].strip():
                country_flagged = country_flag(data['country'])

                formatted_text = (
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"BIN : <code>{data['bin']}</code>\n"
                    f"INFO : {data['brand']} - {data['type']} - {data['level']}\n"
                    f"BANK : {data['bank']}\n"
                    f"COUNTRY : {country_flagged}"
                )
                formatted_file = (
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"BIN : {data['bin']}\n"
                    f"INFO : {data['brand']} - {data['type']} - {data['level']}\n"
                    f"BANK : {data['bank']}\n"
                    f"COUNTRY : {country_flagged}"
                )
                results_text.append(formatted_text)
                results_file.append(formatted_file)

        total_valid = len(results_text)

        if total_valid == 0:
            bot.edit_message_text("❌ No valid BINs with bank name found.", chat_id=message.chat.id, message_id=processing_msg.message_id)
            return

        header_html = f"<b>TOTAL BIN: {total_valid}</b>\n\n"
        header_txt = f"TOTAL BIN: {total_valid}\n\n"

        if total_valid > 15:
            filename = f"bin_result_{message.from_user.id}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(header_txt + "\n\n".join(results_file))

            bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

            bot.send_document(message.chat.id, open(filename, "rb"),
                              caption=f"<b>✅ Valid BINs: {total_valid}</b>", parse_mode="HTML")
            os.remove(filename)
        else:
            final_output = header_html + "\n\n".join(results_text)
            bot.edit_message_text(final_output, chat_id=message.chat.id,
                                  message_id=processing_msg.message_id, parse_mode="HTML")

            
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Error:</b> <code>{str(e)}</code>", parse_mode="HTML")


@bot.message_handler(func=lambda message: message.text.lower().startswith(('/clean', '!clean', '.clean')))
def clean_command(message):
    user_id = message.from_user.id
    if not is_user_in_channel(user_id):
        force_user_to_join(user_id)
        return  # Only return if user needs to join channel
    
    if message.reply_to_message and message.reply_to_message.document:
        try:
            processing_msg = bot.reply_to(message, "⏳ Processing...")

            file_id = message.reply_to_message.document.file_id
            file_info = bot.get_file(file_id)
            file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'
            file_response = requests.get(file_url)
            file_text = file_response.content.decode('utf-8', errors='ignore')

            extracted_cards = []
            for match in CARD_PATTERN.findall(file_text):
                card_number, month, year, cvv = match
                extracted_cards.append(f"{card_number}|{month}|{year}|{cvv}")

            extracted_cards = list(set(extracted_cards))

            if extracted_cards:
                output_file = "Clean_Card.txt"
                with open(output_file, "w") as f:
                    f.write("\n".join(extracted_cards))

                with open(output_file, "rb") as f:
                    bot.send_document(message.chat.id, f)

                os.remove(output_file)
                bot.send_message(message.chat.id, "✅ The file has been successfully cleaned!")
            else:
                bot.send_message(message.chat.id, "No valid card information found in the file.")

            bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred: {e}")
    else:
        bot.reply_to(message, "❗ Please reply to a document file with /clean to extract card information.")

@bot.message_handler(func=lambda message: message.text.lower().startswith(('/visa', '!visa', '.visa')))
def vis_command(message):
    user_id = message.from_user.id
    if not is_user_in_channel(user_id):
        force_user_to_join(user_id)
        return  # Only return if user needs to join channel
    
    if message.reply_to_message and message.reply_to_message.document:
        try:
            processing_msg = bot.reply_to(message, "⏳ Processing...")

            file_id = message.reply_to_message.document.file_id
            file_info = bot.get_file(file_id)
            file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'
            file_response = requests.get(file_url)
            file_text = file_response.content.decode('utf-8', errors='ignore')

            extracted_cards = []
            for match in CARD_PATTERN.findall(file_text):
                card_number, month, year, cvv = match
                if card_number.startswith('4'):
                    extracted_cards.append(f"{card_number}|{month}|{year}|{cvv}")

            if extracted_cards:
                output_file = "visa_cards.txt"
                with open(output_file, "w") as f:
                    f.write("\n".join(extracted_cards))

                with open(output_file, "rb") as f:
                    bot.send_document(message.chat.id, f)

                os.remove(output_file)
                bot.send_message(message.chat.id, "✅ Visa cards have been successfully cleaned!")
            else:
                bot.reply_to(message, "No valid Visa card information found in the file.")

            bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

        except Exception as e:
            bot.reply_to(message, f"An error occurred: {e}")
    else:
        bot.reply_to(message, "❗ Please reply to a document file with /vis to extract Visa card information.")

@bot.message_handler(func=lambda message: message.text.lower().startswith(('/find', '!find', '.find')))
def find_command(message):
    user_id = message.from_user.id
    if not is_user_in_channel(user_id):
        force_user_to_join(user_id)
        return  # Only return if user needs to join channel
    
    try:
        parts = message.text.strip().split()
        if len(parts) < 2:
            return bot.reply_to(message, "❗ Please provide a number to search for. Usage: /find <number>")
        
        search_number = parts[1]
        processing_msg = bot.reply_to(message, "⏳ Processing...")

        if message.reply_to_message and message.reply_to_message.document:
            file_id = message.reply_to_message.document.file_id
            file_info = bot.get_file(file_id)
            file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'
            file_response = requests.get(file_url)
            file_text = file_response.content.decode('utf-8', errors='ignore')

            extracted_cards = []
            for match in CARD_PATTERN.findall(file_text):
                card_number, month, year, cvv = match
                extracted_cards.append(f"{card_number}|{month}|{year}|{cvv}")

            found_cards = [card for card in extracted_cards if search_number in card]

            if found_cards:
                output_file = "found_cards.txt"
                with open(output_file, "w") as f:
                    f.write("\n".join(found_cards))

                with open(output_file, "rb") as f:
                    bot.send_document(message.chat.id, f)

                os.remove(output_file)
                bot.send_message(message.chat.id, f"✅ The number `{search_number}` has been successfully found!", parse_mode="Markdown")
            else:
                bot.reply_to(message, f"No cards found with the number: {search_number}")
        else:
            bot.reply_to(message, "❗ Please reply to a document file with /find <number> to search for card information.")

        bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")
        
@bot.message_handler(func=lambda message: message.text.lower().startswith(('/sort', '!sort', '.sort')))
def vis_command(message):
    user_id = message.from_user.id
    if not is_user_in_channel(user_id):
        force_user_to_join(user_id)
        return  # Only return if user needs to join channel
    
    if message.reply_to_message and message.reply_to_message.document:
        try:
            # Send processing message
            processing_msg = bot.reply_to(message, "⏳ Processing...")
            
            # Get the file from the replied message
            file_id = message.reply_to_message.document.file_id
            file_info = bot.get_file(file_id)
            file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'
            
            # Start time for performance measurement
            start_time = time.time()
            
            file_response = requests.get(file_url)
            file_text = file_response.text

            # Extract card information
            extracted_cards = {"visa": [], "mastercard": [], "amex": [], "discover": [], "union": []}

            for match in CARD_PATTERN.findall(file_text):
                card_number, month, year, cvv = match
                
                # Check the starting digit and categorize accordingly
                if card_number.startswith('3'):
                    extracted_cards["amex"].append(f"{card_number}|{month}|{year}|{cvv}")
                elif card_number.startswith('4'):
                    extracted_cards["visa"].append(f"{card_number}|{month}|{year}|{cvv}")
                elif card_number.startswith('5'):
                    extracted_cards["mastercard"].append(f"{card_number}|{month}|{year}|{cvv}")
                elif card_number.startswith('6'):
                    extracted_cards["discover"].append(f"{card_number}|{month}|{year}|{cvv}")
                elif card_number.startswith('8'):
                    extracted_cards["union"].append(f"{card_number}|{month}|{year}|{cvv}")

            # Create output files for each card type
            output_files = {}
            for card_type, cards in extracted_cards.items():
                if cards:
                    output_file_name = f"{card_type}_cards.txt"
                    with open(output_file_name, "w") as f:
                        f.write("\n".join(cards))
                    output_files[card_type] = (output_file_name, len(cards))

            # Calculate time taken
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)

            # Get card counts
            total_cards = sum(count for _, count in output_files.values())
            visa_count = len(extracted_cards["visa"])
            mastercard_count = len(extracted_cards["mastercard"])
            amex_count = len(extracted_cards["amex"])
            discover_count = len(extracted_cards["discover"])
            union_count = len(extracted_cards["union"])

            # Prepare statistics message
            stats_message = (
                "📊 Sorting Statistics!\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"💳 Total cards: {total_cards}\n"
                f"Visa: {visa_count}\n"
                f"MasterCard: {mastercard_count}\n"
                f"Amex: {amex_count}\n"
                f"Discover: {discover_count}\n"
                f"Union: {union_count}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"⏱️ Time taken: {time_taken} seconds"
            )

            # Edit the original processing message to show stats
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text=stats_message
            )

            # Send the output files back to the user with counts in captions
            for card_type, (output_file, count) in output_files.items():
                with open(output_file, "rb") as f:
                    bot.send_document(
                        message.chat.id,
                        f,
                        caption=f"📁 {card_type.capitalize()} Cards - {count}"
                    )
                # Remove the temporary output files after sending
                os.remove(output_file)

            # Now send the completion message after all files are sent
            bot.send_message(message.chat.id, "✅ Sorting Complete!")

        except Exception as e:
            error_msg = f"❗ An error occurred: {e}"
            if 'processing_msg' in locals():
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=processing_msg.message_id,
                    text=error_msg
                )
            else:
                bot.reply_to(message, error_msg)
    else:
        bot.reply_to(message, "❗ Please reply to a document file with /sort to extract card information.")
        
@bot.message_handler(func=lambda message: message.text.lower().startswith(('/split', '!split', '.split')))
def split_command(message):  
    user_id = message.from_user.id
    if not is_user_in_channel(user_id):
        force_user_to_join(user_id)
        return  # Only return if user needs to join channel
    
    if not message.reply_to_message or not message.reply_to_message.document:  
        bot.reply_to(message, "Please reply to a text document and send `/split <amount>`.", parse_mode="Markdown")  
        return  
  
    try:  
        try:  
            amount = int(message.text.split()[1])  
        except (IndexError, ValueError):  
            bot.reply_to(message, "Please type `/split <amount>` in the correct format.\nExample: `/split 4`", parse_mode="Markdown")  
            return  
  
        if amount > 15:  
            bot.reply_to(message, "❌ The maximum split limit is 15 parts. Please choose a number between 1 and 15.", parse_mode="Markdown")  
            return  
  
        processing_msg = bot.reply_to(message, "⏳ Processing...")  
  
        file_id = message.reply_to_message.document.file_id  
        file_info = bot.get_file(file_id)  
        file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'  
        response = requests.get(file_url)  
        file_name = message.reply_to_message.document.file_name  
  
        with open(file_name, 'wb') as file:  
            file.write(response.content)  
  
        # Read lines and remove empty lines and newlines  
        with open(file_name, 'r', encoding='utf-8') as file:  
            lines = [line.strip() for line in file if line.strip()]  # remove empty and strip newlines  
  
        total_lines = len(lines)  
        lines_per_file = total_lines // amount  
        remaining_lines = total_lines % amount  
  
        start = 0  
        for i in range(amount):  
            end = start + lines_per_file + (1 if i < remaining_lines else 0)  
            part_lines = lines[start:end]  
  
            part_file_name = f"Part_{i+1}_of_{amount}_Lines_{len(part_lines)}.txt"  
            with open(part_file_name, 'w', encoding='utf-8') as part_file:  
                part_file.write('\n'.join(part_lines))  # join without adding trailing newline  
  
            with open(part_file_name, 'rb') as part_file:  
                bot.send_document(message.chat.id, part_file, caption=f"📄 Part {i+1} of {amount} | Lines: {len(part_lines)}")  
  
            start = end  
            os.remove(part_file_name)  
  
        os.remove(file_name)  
  
        bot.reply_to(message, "✅ The file has been successfully split!")  
        bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)  
  
    except Exception as e:  
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")  

    except Exception as e:
        bot.reply_to(message, f"❌ an error occurred: {str(e)}")
        

# Start broadcast
@bot.message_handler(func=lambda message: message.text == "💓 Broadcast" and str(message.chat.id) == ADMIN_ID)
def type_command(message):
    bot.reply_to(message, "Please send the message (text, photo, video, etc.) you want to broadcast.")
    bot.register_next_step_handler(message, ask_broadcast_confirmation)

# Store message temporarily
pending_broadcast = {}

# Ask for confirmation
def ask_broadcast_confirmation(message):
    if str(message.chat.id) != ADMIN_ID:
        return

    # Save the message to broadcast
    pending_broadcast[message.chat.id] = message

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("✅ Yes", "❌ No")
    bot.send_message(message.chat.id, "Are you sure you want to send this to all users?", reply_markup=markup)
    bot.register_next_step_handler(message, process_broadcast_confirmation)

# Process confirmation
def process_broadcast_confirmation(message):
    if str(message.chat.id) != ADMIN_ID:
        return

    if message.text.strip().lower() in ["✅ yes", "yes"]:
        message_to_send = pending_broadcast.get(message.chat.id)
        if message_to_send:
            success_count = 0
            failed_count = 0
            users = users_collection.find({})
            for user in users:
                try:
                    chat_id = user["user_id"]
                    if message_to_send.photo:
                        bot.send_photo(chat_id, message_to_send.photo[-1].file_id, caption=message_to_send.caption or "")
                    elif message_to_send.video:
                        bot.send_video(chat_id, message_to_send.video.file_id, caption=message_to_send.caption or "")
                    elif message_to_send.document:
                        bot.send_document(chat_id, message_to_send.document.file_id, caption=message_to_send.caption or "")
                    elif message_to_send.audio:
                        bot.send_audio(chat_id, message_to_send.audio.file_id, caption=message_to_send.caption or "")
                    elif message_to_send.voice:
                        bot.send_voice(chat_id, message_to_send.voice.file_id)
                    elif message_to_send.text:
                        bot.send_message(chat_id, message_to_send.text)
                    else:
                        bot.send_message(chat_id, "Unsupported message type.")
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to send to {user['user_id']}: {e}")

            bot.send_message(message.chat.id, f"✅ Broadcast completed.\n\n"
                                              f"• Successful: {success_count}\n"
                                              f"• Failed: {failed_count}")
        else:
            bot.send_message(message.chat.id, "No message to broadcast.")
        start_command(message)

    else:
        bot.send_message(message.chat.id, "❎ Broadcast cancelled.")
        start_command(message)


# Broadcast
# Store the forwarded message temporarily
pending_forward = {}

@bot.message_handler(func=lambda message: message.text == "👻 Forwarded" and str(message.chat.id) == ADMIN_ID)
def broadcast_command(message):
    bot.reply_to(message, "Please forward the message you want to broadcast.")
    bot.register_next_step_handler(message, ask_forward_confirmation)

# Ask for confirmation
def ask_forward_confirmation(message):
    if not message.forward_from and not message.forward_from_chat:
        bot.reply_to(message, "❌ Please forward a valid message.")
        return

    # Store the forwarded message
    pending_forward[message.chat.id] = {
        "message_id": message.message_id,
        "from_chat_id": message.chat.id
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("✅ Yes", "❌ No")
    bot.send_message(message.chat.id, "Are you sure you want to forward this to all users?", reply_markup=markup)
    bot.register_next_step_handler(message, process_forward_confirmation)

# Process confirmation
def process_forward_confirmation(message):
    if message.text.lower() in ["✅ yes", "yes"]:
        data = pending_forward.get(message.chat.id)
        if not data:
            bot.send_message(message.chat.id, "No message found to broadcast.")
            return

        success, failed = 0, 0
        users = users_collection.find({})
        for user in users:
            try:
                bot.forward_message(
                    chat_id=user['user_id'],
                    from_chat_id=data['from_chat_id'],
                    message_id=data['message_id']
                )
                success += 1
            except Exception as e:
                print(f"Failed to send to {user['user_id']}: {e}")
                failed += 1

        bot.send_message(message.chat.id, f"✅ Broadcast completed!\n\n"
                                          f"• Successful: {success}\n"
                                          f"• Failed: {failed}")
        start_command(message)

    else:
        bot.send_message(message.chat.id, "❎ Forward broadcast cancelled.")
        start_command(message)

# Export Users
@bot.message_handler(func=lambda message: message.text == "📤 Export Users" and str(message.chat.id) == ADMIN_ID)
def export_users(message):
    try:
        users = list(users_collection.find({}, {"_id": 0}))
        if not users:
            bot.reply_to(message, "No users found to export.")
            return

        filename = "users_export.json"
        with open(filename, "w") as file:
            json.dump(users, file, indent=4)

        with open(filename, "rb") as file:
            bot.send_document(message.chat.id, file)

        os.remove(filename)
        bot.reply_to(message, "User data exported and file removed!")
    except Exception as e:
        bot.reply_to(message, f"Failed to export user data: {e}")

# Import Users
@bot.message_handler(func=lambda message: message.text == "📥 Import Users" and str(message.chat.id) == ADMIN_ID)
def import_users(message):
    bot.reply_to(message, "📤 Please upload a JSON file containing user data.")
    bot.register_next_step_handler(message, process_import)

def process_import(message):
    if not message.document:
        bot.reply_to(message, "❌ No file uploaded. Please send a valid JSON file.")
        return

    try:
        # Send loading message
        processing_msg = bot.send_message(message.chat.id, "⏳ Processing file, please wait...")

        # Download the file
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save file
        filename = f"users_import_{message.chat.id}.json"
        with open(filename, "wb") as file:
            file.write(downloaded_file)

        # Load user data
        with open(filename, "r") as file:
            users = json.load(file)

        # Get all existing user_ids to speed up check
        existing_ids = set(user["user_id"] for user in users_collection.find({}, {"user_id": 1}))

        imported_count = 0
        for user in users:
            user_id = user.get("user_id")
            if user_id and user_id not in existing_ids:
                users_collection.insert_one(user)
                imported_count += 1

        # Clean up temp file
        os.remove(filename)

        # Edit the "Processing..." message to final result
        if imported_count > 0:
            bot.edit_message_text(
                f"✅ Successfully imported {imported_count} users!",
                chat_id=message.chat.id,
                message_id=processing_msg.message_id
            )
        else:
            bot.edit_message_text(
                "ℹ️ All users already exist. No new users were imported.",
                chat_id=message.chat.id,
                message_id=processing_msg.message_id
            )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Failed to import user data:\n{e}")
        if os.path.exists(filename):
            os.remove(filename)

# Delete All Users with confirmation
@bot.message_handler(func=lambda message: message.text == "❌ Delete All Users" and str(message.chat.id) == ADMIN_ID)
def confirm_delete_users(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("✅ Yes", "❌ No")
    bot.send_message(
        message.chat.id,
        "⚠️ Are you sure you want to delete all users?\nChoose an option below:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_delete_confirmation)

def process_delete_confirmation(message):
    if str(message.chat.id) != ADMIN_ID:
        return

    if message.text.strip().lower() in ["✅ yes", "yes"]:
        try:
            result = users_collection.delete_many({})
            if result.deleted_count > 0:
                bot.send_message(message.chat.id, f"✅ Successfully deleted {result.deleted_count} users.")
            else:
                bot.send_message(message.chat.id, "No users found to delete.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Failed to delete users: {e}")
    else:
        bot.send_message(message.chat.id, "❎ Deletion cancelled.")
    
    start_command(message)  # Back to main menu

@bot.message_handler(func=lambda message: message.text.lower().startswith(('/email', '!email', '.email')))
def handle_email_command(message):
    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to a message containing email:password data (document or text).")
        return

    # Send processing message
    processing_msg = bot.reply_to(message, "⏳ Processing...")

    text_data = ''
    is_document = False

    # Check if the replied message is a document
    if message.reply_to_message.document:
        is_document = True
        try:
            file_id = message.reply_to_message.document.file_id
            file_info = bot.get_file(file_id)
            file = requests.get(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}')
            text_data = file.text.strip()
        except:
            bot.edit_message_text("Failed to download or read the document.", message.chat.id, processing_msg.message_id)
            return

    # Check if the replied message is text
    elif message.reply_to_message.text:
        text_data = message.reply_to_message.text.strip()

    # Extract email:password pairs
    matches = extract_emails(text_data)
    total_email = len(matches)

    # If no valid emails
    if total_email == 0:
        bot.edit_message_text("No valid email:password pairs found.", message.chat.id, processing_msg.message_id)
        return

    # Build response
    header = f"Total Email : {total_email}\n\n"
    body = ""

    for email, password in matches:
        # Use Markdown formatting for all text responses
        body += f"━━━━━━━━━━━━━━━━━━\nEmail : `{email}`\nPassword : `{password}`\n"

    body += "━━━━━━━━━━━━━━━━━━"

    # If more than 20 emails, always send as document file
    if total_email > 20:
        filename = f"email_result_{message.from_user.id}.txt"
        with open(filename, 'w') as f:
            f.write(header + body.replace('`', ''))  # Remove backticks for file output
        with open(filename, 'rb') as f:
            bot.delete_message(message.chat.id, processing_msg.message_id)
            bot.send_document(message.chat.id, f)
        os.remove(filename)
    else:
        # Edit message with Markdown response
        bot.edit_message_text(header + body, message.chat.id, processing_msg.message_id, parse_mode='Markdown')
        

@bot.message_handler(commands=['db'])
def daily_stats(message):
    try:
        # Get system stats
        ping_start = time.time()
        bot.send_chat_action(message.chat.id, 'typing')
        ping_end = time.time()
        ping = int((ping_end - ping_start) * 1000)

        cpu_usage = psutil.cpu_percent(interval=1)
        disk_usage = psutil.disk_usage('/').percent
        ram_usage = psutil.virtual_memory().percent
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        user_count = users_collection.count_documents({})

        # Build message
        stats_message = (
            "📊 *Daily Statistics:*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💠 *Date:* `{today}`\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💠 *Ping:* `{ping}ms`\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💠 *CPU:* `{cpu_usage}%`\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💠 *Disk:* `{disk_usage}%`\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💠 *RAM:* `{ram_usage}%`\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💠 *Users used bot:* `{user_count}`\n"
            "━━━━━━━━━━━━━━━━━━"
        )

        bot.send_message(message.chat.id, stats_message, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Failed to fetch statistics:\n{e}")

def polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    print("Bot started...")
    polling()
