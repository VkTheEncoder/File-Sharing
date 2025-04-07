import sys
import glob
import importlib
from pathlib import Path
from pyrogram import idle
import logging
import logging.config

# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

# Load logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script 
from datetime import date, datetime 
import pytz
from aiohttp import web
from TechVJ.server import web_server

import asyncio
from pyrogram import idle
from plugins.clone import restart_bots
from TechVJ.bot import StreamBot
from TechVJ.utils.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

# ---------------------------------------------------
# Modified Plugin Loader:
# This will load all .py files from both "plugins" and "clone_plugins" folders.
# ---------------------------------------------------
plugin_patterns = ["plugins/*.py", "clone_plugins/*.py"]
files = []
for pattern in plugin_patterns:
    files.extend(glob.glob(pattern))

StreamBot.start()
loop = asyncio.get_event_loop()

async def start():
    print('\nInitializing Tech VJ Bot')
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username
    await initialize_clients()
    
    for file_path in files:
        with open(file_path) as file_handle:
            path_obj = Path(file_handle.name)
            plugin_name = path_obj.stem  # Gets filename without extension
            
            # Determine the import path based on the folder
            if "clone_plugins" in file_path:
                import_path = f"clone_plugins.{plugin_name}"
            else:
                import_path = f"plugins.{plugin_name}"
            
            spec = importlib.util.spec_from_file_location(import_path, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[import_path] = module
            print("Tech VJ Imported => " + plugin_name)
    
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    
    me = await StreamBot.get_me()
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    current_time = now.strftime("%H:%M:%S %p")
    
    # Start the web server for keepalive or other purposes
    app_runner = web.AppRunner(await web_server())
    await StreamBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, current_time))
    await app_runner.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app_runner, bind_address, PORT).start()
    
    if CLONE_MODE:
        await restart_bots()
    
    print("Bot Started Powered By @THe_vK_3")
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
