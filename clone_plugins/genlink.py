# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import base64
import logging
from pyrogram import Client, filters, enums
from config import LOG_CHANNEL  # Ensure LOG_CHANNEL is correctly set in config.py
from clone_plugins.users_api import get_user, get_short_link  # Optional: for link shortening

logger = logging.getLogger(__name__)

# ------------------ /start Handler ------------------ #
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(bot, message):
    """
    This handler processes the start parameter. When a user clicks on the shareable link,
    they are sent a /start command with a Base64 parameter (e.g., ?start=file_1234).
    It decodes the parameter and copies the file from the LOG_CHANNEL to the user.
    """
    if len(message.command) > 1:
        param = message.command[1]
        # Fix missing Base64 padding if necessary
        param += "=" * (-len(param) % 4)
        try:
            decoded = base64.urlsafe_b64decode(param).decode("ascii")
            logger.info(f"Decoded parameter: {decoded}")
        except Exception as e:
            logger.error(f"Error decoding parameter: {e}")
            return await message.reply(f"Invalid start parameter. Error: {e}")

        if decoded.startswith("file_"):
            msg_id_str = decoded.split("_", 1)[1]
            if not msg_id_str.isdigit():
                logger.error("File identifier is not numeric.")
                return await message.reply("Invalid file identifier.")
            msg_id = int(msg_id_str)
            try:
                # Copy the file from the LOG_CHANNEL to the user's chat.
                copied_msg = await bot.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=LOG_CHANNEL,
                    message_id=msg_id
                )
                logger.info(f"Copied message ID {msg_id} to user {message.chat.id}.")
            except Exception as e:
                logger.error(f"Error copying message from LOG_CHANNEL: {e}")
                return await message.reply(f"Could not fetch the file. Error: {e}")
        else:
            logger.error("Start parameter does not start with 'file_'.")
            return await message.reply("Unknown start parameter.")
    else:
        # No parameter provided: normal /start
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
        logger.info(f"Copied file to LOG_CHANNEL. New message ID: {post.id}")
    except Exception as e:
        logger.error(f"Error copying file to LOG_CHANNEL: {e}")
        return await message.reply(f"Error copying file to LOG_CHANNEL: {e}")

    # Use the message ID in the LOG_CHANNEL to form the file identifier.
    file_id = str(post.id)
    identifier = f"file_{file_id}"
    outstr = base64.urlsafe_b64encode(identifier.encode("ascii")).decode().strip("=")
    logger.info(f"Generated identifier: {identifier} and encoded as: {outstr}")

    # Get the bot's username (to form the share link).
    bot_username = (await client.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={outstr}"
    logger.info(f"Generated share link: {share_link}")

    # Optionally use short link if available.
    user_id = message.from_user.id
    user = await get_user(user_id)
    if user.get("shortener_api"):
        try:
            short_link = await get_short_link(user, share_link)
            await message.reply(
                f"<b>⭕ Here is your link:\n\n🖇️ Short Link :- {short_link}</b>"
            )
        except Exception as e:
            logger.error(f"Error generating short link: {e}")
            await message.reply(
                f"<b>⭕ Here is your link (shortener error, showing original link):\n\n🔗 Original Link :- {share_link}</b>"
            )
    else:
        await message.reply(
            f"<b>⭕ Here is your link:\n\n🔗 Original Link :- {share_link}</b>"
        )
