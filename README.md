<h1 align="center">

BetterBio

</h1>
<p align="center">
a self-hosted link-in-bio style site designed to mimic a discord profile
</p>

# what?
BetterBio is a "links in bio" site, akin to Carrd or Beacons, that's designed to mimic the look and feel of a Discord profile.

# why?
I like the idea of having a Carrd, but found the limitations of the free plan to be too.. well, limiting. I also thought it would be cool to be able to show my current Discord online status, status text and type.

# how?
## from pypi
You can install it from PyPI using pip with `install betterbio` on a Python version >=3.10 and run it with `betterbio` (assuming python is in your PATH, if not, you can set up a venv and install it there)

## docker
```bash
docker run -d \
  -p 8080:8080 \
  -v /path/to/betterbio/data:/home/betterbio/.betterbio \
  enhancedrock/betterbio:latest
```

## docker-compose
```yaml
---
services:
  betterbio:
    image: enhancedrock/betterbio:latest
    container_name: betterbio
    volumes:
      - /path/to/betterbio/data:/home/betterbio/.betterbio
    ports:
      - 8080:8080
    restart: unless-stopped
```

# demo
You can view my own personal betterbio @ https://enhancedrock.tech.
Here's a screenshot:
<img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/09c4690da2e80dcf07be34b37ce0a672e7389171_image.png">

# configuring
BetterBio comes with a default config.json that will be copied to ~/.betterbio/config.json. (This is also where all your other BetterBio files will live)
<br>
Here's how it'll look:
```json
{
    "bot": {
        "enabled": false,
        "token": "YOUR_DISCORD_BOT_TOKEN_HERE",
        "user_id": 123456789012345678
    },
    "theme": {
        "background_color": "#0c0c0c",
        "profile_color": "#1e1e1e",
        "text_color": "#ffffff",
        "title": "BetterBio"
    },
    "userdata": {
        "name": "Hey there!",
        "username": "hey_hey",
        "pronouns": "yeah/you",
        "bio": "This is a sample profile.\nGo take a look at ~/.betterbio/config.json to set up your own!",
        "pfp": "https://raw.githubusercontent.com/enhancedrock/enhancedrock/refs/heads/main/squishypfp.png",
        "banner": "https://raw.githubusercontent.com/enhancedrock/enhancedrock/refs/heads/main/squishypfp.png",
        "connections": [
            {
                "label": "Github",
                "url": "https://github.com/enhancedrock/BetterBio/",
                "iconurl": "https://cdn-icons-png.flaticon.com/512/25/25231.png"
            }
        ]
    },
    "port": 8080,
    "host": "0.0.0.0"
}
```
To use the Discord bot integration (will show your status text & emoji, your Discord join date, and if your online on your page), set `bot/enabled` to `true`, set `bot/user_id` to your [Discord user ID](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID), set up a bot on the [Discord Developer Portal](https://discord.com/developers/applications) with the Presence and Server Members Intent set to on, reset the token, then copy & paste that into `bot/token`, and lastly invite it into a server with yourself.

For the theme settings, `theme/background_color` dictates the colour of the background of the page, `theme/profile_color` dictates the colour of your profile box itself (note: you can supply two hex codes in a list like `["#181B2F", "#08080D"]` to make a gradient), `theme/text_color` dictates the color of text on the page, and lastly `theme/title` dictates the webpage's title.

For userdata, it's all relatively self-explanatory, the `userdata/pfp` and `userdata/banner` links will be used should the bot integration be disabled, and connections will show as clickable links below your bio.

`port` and `host` will dictate what port and host Flask will use. (Don't change this when using Docker.)

In your ~/.betterbio folder, you'll notice that there'll be a pages and static folder - any markdown files in the pages folder will have their contents shown to the right of your profile on a Desktop/landscape browser when selected (a `about`, `ABOUT`, `readme` or `README` page will be initially opened should one exist), and any files in the static folder will be made available at yourbetterbiohost/files. You can also place a favicon.ico in the root of ~/.betterbio, and that will be displayed instead of the default one.
