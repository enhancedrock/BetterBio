"""Main entry point"""
import os
import shutil
import signal
import sys
import threading
import asyncio
import json
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
import discord
from .logger import Logger
logger = Logger(name="betterbio", log_level="DEBUG").logger

USER_ONLINE_STATUS = None
STATUS_TEXT = None
STATUS_EMOJI = None
AVATAR_URL = None
BANNER_URL = None
CONFIG = {}
BOT_CONFIG = {}

SHUTDOWN_EVENT = threading.Event()

def load_config():
    """Load configuration from config.json"""
    global CONFIG
    global BOT_CONFIG
    data_dir = os.path.join(os.path.expanduser("~"), ".betterbio")
    config_path = os.path.join(data_dir, "config.json")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            CONFIG = json.load(f)
            logger.debug("Configuration loaded successfully")
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        logger.error("Failed to load configuration: %s", e)
        exit(1)
    
    BOT_CONFIG = CONFIG.get("bot", {})

def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info("Received termination signal. Shutting down...")
    SHUTDOWN_EVENT.set()
    sys.exit(0)

def ensure_files():
    """Ensure necessary files and directories exist"""
    data_dir = os.path.join(os.path.expanduser("~"), ".betterbio")
    os.makedirs(data_dir, exist_ok=True)
    config_path = os.path.join(data_dir, "config.json")
    if not os.path.exists(config_path):
        # copy internal config.json
        src_dir = Path(__file__).parent
        internal_config = src_dir / "config.json"

        if internal_config.exists():
            shutil.copy2(internal_config, config_path)
            logger.info("No config.json found - Created one @ %s/config.json", data_dir)
        else:
            logger.warning("No config.json found")
    new_dir = os.path.join(data_dir, "static")
    if not os.path.exists(new_dir):
        os.makedirs(new_dir, exist_ok=True)
    new_dir = os.path.join(data_dir, "pages")
    if not os.path.exists(new_dir):
        os.makedirs(new_dir, exist_ok=True)

class DiscordBot(discord.Client):
    """Discord online status integration"""
    def __init__(self):
        intents = discord.Intents.default()
        intents.presences = True
        intents.members = True
        super().__init__(intents=intents)
    
    async def update_status(self):
        """Update users status"""
        global USER_ONLINE_STATUS
        global STATUS_TEXT
        global STATUS_EMOJI
        global AVATAR_URL
        global BANNER_URL
        await self.wait_until_ready()
        user_id = CONFIG.get("bot", {}).get("user_id")
        
        if not user_id:
            logger.error("No user_id specified in config for Discord bot.")
            return

        while not SHUTDOWN_EVENT.is_set():
            try:
                user = self.get_user(user_id)
                if user:
                    for guild in self.guilds:
                        member = guild.get_member(user_id)
                        if member:
                            USER_ONLINE_STATUS = str(member.status)
                            for act in member.activities:
                                if isinstance(act, discord.CustomActivity):
                                    STATUS_TEXT = (str(act.name))
                                    logger.debug("Emoji = %s", act.emoji)
                                    if act.emoji:
                                        if isinstance(act.emoji, str):
                                            STATUS_EMOJI = act.emoji
                                        elif hasattr(act.emoji, 'name') and act.emoji.name:
                                            # Handle PartialEmoji objects
                                            if act.emoji.id is None:
                                                # Unicode emoji - convert to Twemoji URL
                                                codepoint = hex(ord(act.emoji.name))[2:]
                                                STATUS_EMOJI = f"https://twemoji.maxcdn.com/v/latest/72x72/{codepoint}.png"
                                            else:
                                                # Custom Discord emoji
                                                STATUS_EMOJI = act.emoji.url
                                        else:
                                            STATUS_EMOJI = str(act.emoji)
                                    else:
                                        STATUS_EMOJI = None
                            logger.debug("Updated user status to %s", USER_ONLINE_STATUS)
                            AVATAR_URL = user.avatar.url if user.avatar else None
                            BANNER_URL = user.banner.url if user.banner else None
                            break
            except Exception as e:
                logger.error("Error updating status: %s", e)
            
            await asyncio.sleep(30)
    
    async def on_ready(self):
        logger.info("Discord bot logged in as %s", self.user)
        self.loop.create_task(self.update_status())

def run_bot():
    """Run the Discord bot"""
    if not BOT_CONFIG.get('enabled', False):
        logger.info("Discord bot integration is disabled in config.")
        return
    
    token = BOT_CONFIG.get('token')
    if not token:
        logger.error("Discord bot token not found in config.")
        return
    
    bot = DiscordBot()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(bot.start(token))
    except Exception as e:
        logger.error("Discord bot encountered an error: %s", e)
    finally:
        loop.close()

def main():
    """flask,,"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    ensure_files()
    load_config()

    app = Flask(__name__)

    @app.route('/api/status/online')
    def onlinetype():
        return jsonify(USER_ONLINE_STATUS or "offline")
    
    @app.route('/api/status/text')
    def statustext():
        return jsonify(STATUS_TEXT or "")
    
    @app.route('/api/status/emoji')
    def statusemoji():
        return jsonify(STATUS_EMOJI or "")
    
    @app.route('/api/profile/theme')
    def profiletheme():
        return jsonify(CONFIG.get("theme", {}))
    
    @app.route('/api/profile/info')
    def profileinfo():
        return jsonify(CONFIG.get("userdata", {}))
    
    @app.route('/api/profile/avatar')
    def profileavatar():
        return jsonify(AVATAR_URL or "")
    
    @app.route('/api/profile/banner')
    def profilebanner():
        return jsonify(BANNER_URL or "")
    
    @app.route('/')
    def index():
        src_dir = Path(__file__).parent / "html"
        index_path = src_dir / "index.html"
        if index_path.exists():
            return send_from_directory(src_dir, "index.html")
        else:
            return "<h1>BetterBio</h1><p>index.html not found in package</p>", 404

    @app.route('/files/<path:path>')
    def static_files(path):
        file_dir = os.path.join(os.path.expanduser("~"), ".betterbio", "static")
        full_path = os.path.join(file_dir, path)
        logger.debug("Attempting to serve static file: %s", full_path)
        logger.debug("File exists: %s", os.path.exists(full_path))
        logger.debug("Static directory exists: %s", os.path.exists(file_dir))
        if os.path.exists(file_dir):
            logger.debug("Files in static directory: %s", os.listdir(file_dir))
        return send_from_directory(file_dir, path)

    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    try:
        app.run(host='127.0.0.1', port=8080, static_files=None)
    except KeyboardInterrupt:
        logger.info("Shutting down Flask server...")
    finally:
        SHUTDOWN_EVENT.set()

if __name__ == "__main__":
    main()
