# clone_genlink.py
#
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import base64
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from clone_plugins.users_api import get_user, get_short_link


# Optional: same "allowed" filter as main bot
async def allowed(_, __, message):
    # If you want everyone to be able to use /link, set PUBLIC_FILE_STORE = True
    # Or restrict it to ADMINS only, etc.
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False


@Client.on_message(filters.command("link") & filters.create(allowed))
async def gen_link_s(bot, message):
    """
    Reply to a video/audio/document message and get a shareable link
    just like your main bot does.
    """
    username = (await bot.get_me()).username
    replied = message.reply_to_message
    if not replied:
        return await message.reply("Reply to a message to get a shareable link.")

    # 1) Copy the replied message to LOG_CHANNEL
    try:
        post = await replied.copy(LOG_CHANNEL)
    except ChannelInvalid:
        return await message.reply(
            "LOG_CHANNEL seems invalid. Make sure the bot is an admin in that channel."
        )
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("Invalid LOG_CHANNEL username or ID.")
    except Exception as e:
        return await message.reply(f"Error copying message: {e}")

    # 2) Use the channel message's ID
    file_id = str(post.id)  # e.g. 1234
    # Create the string "file_<msg_id>"
    string = f"file_{file_id}"

    # 3) Base64-encode the string
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

    # 4) Build your final share link
    user_id = message.from_user.id
    user = await get_user(user_id)

    if WEBSITE_URL_MODE:
        # If you prefer your own domain
        share_link = f"{WEBSITE_URL}?Tech_VJ={outstr}"
    else:
        # Telegram deep-link
        share_link = f"https://t.me/{username}?start={outstr}"

    # 5) Optional: short-link if user has shortener API
    if user.get("base_site") and user.get("shortener_api") is not None:
        short_link = await get_short_link(user, share_link)
        await message.reply(
            f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>"
        )
    else:
        await message.reply(
            f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>"
        )
