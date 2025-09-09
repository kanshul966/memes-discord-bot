# 🤖 Taskora Discord Bot

Taskora is a **multi-purpose Discord bot** built with [discord.py](https://discordpy.readthedocs.io/) and MongoDB.
It includes moderation, leveling, birthday reminders, quizzes, music, memes, and fun image-based commands.

---

## ✨ Features Overview

✅ **Leveling System** – Earn reps & levels by chatting.
✅ **Fun Commands** – Generate memes, gifs, and custom images.
✅ **Birthday System** – Auto-sends birthday wishes with images.
✅ **Music & Media** – Download YouTube audio & search videos.
✅ **Moderation Tools** – Auto-ban words, logs, server info.
✅ **Utility Commands** – Google search, Giphy, event logs.
✅ **Custom Cards** – Profile cards, rank cards, hunter licenses.

---

## 📦 Requirements

* Python **3.9+**
* MongoDB (Atlas or Local)
* Libraries:

```bash
pip install discord.py pymongo pillow yt-dlp requests aiohttp pydub
```

---

## ⚙️ Setup

1. **Clone this repo**

   ```bash
   git clone https://github.com/kanshul966/memes-discord-bot
   cd memes-discord-bot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables / update keys** in `main.py`:

   * `DISCORD_KEY` → Your bot token
   * `MONGO_URI` → Your MongoDB connection string
   * Optional: `GOOGLE_API_KEY`, `OPENAI_KEY`, `GIPHY_KEY`

4. **Run the bot**

   ```bash
   python main.py
   ```

---

## 🛠 Commands & Features

### 🎉 Fun Commands

| Command           | Description                           |
| ----------------- | ------------------------------------- |
| `/slap @user`     | Create a meme of slapping a user.     |
| `/pie @user`      | Throw a pie at someone.               |
| `/trash @user`    | Put someone’s avatar in a trash can.  |
| `/kill @user`     | Fake kill meme image.                 |
| `/getout @user`   | Kick user meme with door image.       |
| `/disable @user`  | Meme putting someone in a wheelchair. |
| `/jail @user`     | Jail someone’s avatar.                |
| `/spank @user`    | Spank meme with avatars.              |
| `/rip @user`      | RIP gravestone meme.                  |
| `/wanted @user`   | Create a WANTED poster.               |
| `/marry @user`    | Wedding meme (author + user).         |
| `/love @user`     | Love percentage match.                |
| `/hate @user`     | Hate percentage match.                |
| `/birthday @user` | Send birthday wish meme.              |

---

### 🏆 Leveling System

| Command            | Description                                                        |
| ------------------ | ------------------------------------------------------------------ |
| `/rank [@user]`    | Show user’s rank card with reps & level.                           |
| `/profile [@user]` | Generate detailed profile card (quiz points, reps, level, streak). |
| `/leaderboard`     | Display top 20 users ranked by reps.                               |
| **Auto Features**  | Gain reps when chatting. Auto level-up card posted.                |

---

### 🎂 Birthday System

* Stores birthdays per server.
* Sends **custom birthday memes** on the day.
* Resets date for next year automatically.

---

### 🎶 Music & Media

| Command            | Description                                      |
| ------------------ | ------------------------------------------------ |
| `/song <query>`    | Download & send YouTube audio (trimmed to 400s). |
| `/video <query>`   | Get first YouTube video link.                    |
| `/gif <search>`    | Search for GIFs using Giphy API.                 |
| `/google <search>` | Quick Google search link.                        |

---

### 🛡 Moderation & Utility

| Command         | Description                                            |
| --------------- | ------------------------------------------------------ |
| Auto ban filter | Deletes messages with banned words.                    |
| Deleted msg log | Saves deleted messages in DB.                          |
| `/serverinfo`   | Server information card with icon.                     |
| `/check`        | Bot performance info (ping, uptime, features enabled). |
| `/mention`      | Ping everyone with a random joke.                      |
| Auto Mention    | Sends jokes with @everyone on schedule.                |

---

### 🔗 Website Integration

| Command         | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| `/feature`      | Shows bot features & links to Taskora docs.                                 |
| Feature Buttons | Direct buttons: 🌍 Website, 📌 Features, 😂 Memes, 🎮 Games, 🎶 Music, etc. |

---

## 📂 MongoDB Collections

* `discord.basic_setup` → Server setup info
* `discord.welcome_db` → Welcome system
* `discord.auto_ping` → Auto mention schedule
* `discord.BotLogGuilds` → Logging
* `discord.LevelChannel` → Level system configs
* `discord.Verification` → Verification settings
* `birthday_db.channel_db` → Birthday channels
* `levelup_db` → User leveling data per guild
* `QuizDB` → Quiz/game points

---

## 🖼 Preview (Generated Images)

* 🎖 Rank Cards
* 🏆 Leaderboards
* 🎂 Birthday memes
* 💍 Marriage memes
* 💖 Love/Hate cards
* 🛡 Moderation image templates

---

## 🚀 Roadmap

* [ ] Music queue & streaming system.
* [ ] Web dashboard for settings.
* [ ] Economy system & shop.
* [ ] AI chat integration.

---

## 📜 License

MIT License © 2025 \[Your Name]

---
