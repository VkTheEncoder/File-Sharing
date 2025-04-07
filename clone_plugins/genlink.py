# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import base64
from pyrogram import Client, filters, enums
from config import LOG_CHANNEL  # Ensure LOG_CHANNEL is set in your config file
from clone_plugins.users_api import get_user, get_short_link  # Optional: if you use these for shortening links

# ------------------ /start Handler ------------------ #
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(bot, message):
    """
    This handler processes the start parameter. When a user clicks on the shareable link,
    they are sent a /start command with a Base64 parameter (e.g., ?start=file_1234). This handler:
      1. Decodes the parameter.
      2. Checks if it starts with 'file_'.
      3. Copies the file (message) from the LOG_CHANNEL to the user.
    """
    if len(message.command) > 1:
        param = message.command[1]
        # Fix missing Base64 padding if needed.
        param += "=" * (-len(param) % 4)
        try:
            decoded = base64.urlsafe_b64decode(param).decode("ascii")
        except Exception as e:
            return await message.reply(f"Invalid start parameter. Error: {e}")

        if decoded.startswith("file_"):
            msg_id_str = decoded.split("_", 1)[1]
            if not msg_id_str.isdigit():
                return await message.reply("Invalid file identifier.")
            msg_id = int(msg_id_str)
            try:
                # Copy the file from the LOG_CHANNEL to the user's chat.
                await bot.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=LOG_CHANNEL,
                    message_id=msg_id
                )
            except Exception as e:
                return await message.reply(f"Could not fetch the file. Error: {e}")
        else:
            return await message.reply("Unknown start parameter.")
    else:
        # Normal /start command (without parameter)
        await message.reply(
            "Hello! I'm your clone bot.\nReply to a supported file (video, audio, or document) with /link to generate a shareable link."
        )


# ------------------ /link Handler ------------------ #
@Client.on_message(filters.command("link") & filters.private)
async def gen_link_s(client: Client, message):
    """
    When a user replies to a message (with a video, audio, or document) with /link,
    this handler copies the message to the LOG_CHANNEL, encodes the message ID,
    and sends back a shareable link.
    """
    replied = message.reply_to_message
    if not replied:
        return await message.reply("Reply to a message to get a shareable link.")

    file_type = replied.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await message.reply("Please reply to a supported media (video, audio, or document).")

    try:
        # Copy the file to the LOG_CHANNEL.
        post = await replied.copy(LOG_CHANNEL)
    except Exception as e:
        return await message.reply(f"Error copying file to LOG_CHANNEL: {e}")

    # Use the message ID in the LOG_CHANNEL to form the file identifier.
    file_id = str(post.id)
    string = f"file_{file_id}"
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

    # Get the bot's username (to form the share link).
    bot_username = (await client.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={outstr}"

    # Optionally, you can check if the user has a shortener API and generate a short link.
    # In this example, we'll just return the original link.
    # If you want to use get_short_link, ensure your get_user() and get_short_link() functions are working.
    user_id = message.from_user.id
    user = await get_user(user_id)
    if user.get("shortener_api"):
        short_link = await get_short_link(user, share_link)
        await message.reply(
            f"<b>⭕ Here is your link:\n\n🖇️ Short Link :- {short_link}</b>"
        )
    else:
        await message.reply(
            f"<b>⭕ Here is your link:\n\n🔗 Original Link :- {share_link}</b>"
        )
