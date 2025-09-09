import discord
from discord.ext import commands, tasks
import time
import asyncio
from pymongo import MongoClient
import datetime
import random
import aiohttp
import urllib.request
import re
from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
import os
import io
import yt_dlp
import json
from pydub import AudioSegment
import subprocess

database = MongoClient("mongo url")
discord_database = database["discord"]
basic_setup=discord_database["basic_setup"]
welcome_database = discord_database["welcome_db"]
auto_ping_database = discord_database["auto_ping"]
bot_logs = discord_database["BotLogGuilds"]
error_log_db = discord_database["ErrorLog"]
event_log_db = discord_database["EventLog"]
ban_words_list = discord_database["BanWordList"]
level_channel = discord_database["LevelChannel"]
set_verification = discord_database["Verification"]
birthday_database = database["birthday_db"]
birth_day_chennel=birthday_database["channel_db"]
levelup_database = database["levelup_db"]
Smmdb = database["SmmDb"]
Add_cash_db = Smmdb["AddCash"]
Service_logs = Smmdb["ServiceLogs"]
Smm_db = Smmdb["SMM_PANEL"]
delete_data_db = database["DELETED"]
Quiz_db = database["QuizDB"]


GOOGLE_API_KEY = "googleapikey"
DISCORD_KEY = "discord token"
OPENAI_KEY = "openapikey"
GIPHY_KEY = "giphykey"


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)
start_time = time.time()





async def log_command_error(message: str):
    error_log_db.insert_one({"msg" : message , "by" : "taskora bot 🤖", "status": 0})
    


async def send_event_log(message):
    event_log_db.insert_one({"msg" : message , "by" : "taskora bot 🤖", "status": 0})
    
    


def create_circle_avatar(image: Image.Image) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    circular_avatar = ImageOps.fit(image, image.size, centering=(0.5, 0.5))
    circular_avatar.putalpha(mask)
    return circular_avatar


async def create_embed(title: str, description: str, image_filename: str, image_bytes: io.BytesIO):
    file = discord.File(image_bytes, filename=image_filename)
    embed = discord.Embed(title=title, description=description, color=discord.Color.random())
    embed.set_image(url=f"attachment://{image_filename}")
    return embed, file

async def fetch_avatar(member: discord.Member):
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response = requests.get(avatar_url)
    if response.status_code != 200:
        return None
    return Image.open(io.BytesIO(response.content))



def get_rank_by_reps(reps: int) -> str:
    ranks = [(0, "E"),(2000, "D"),(5000, "C"),(50000, "B"),(100000, "A"),(250000, "S"),(500000,"SS")]
    if reps < 0:
        return "Invalid"
    for threshold, rank in reversed(ranks):
        if reps >= threshold:
            return rank
        
def add_time_to_current_date(hours):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')




class LevelSystem:
    def __init__(self, min_rep=500, max_rep=500000, max_level=100):
        self.min_rep = min_rep
        self.max_rep = max_rep
        self.max_level = max_level
        self.level_thresholds = self.generate_thresholds()

    def generate_thresholds(self):
        thresholds = []
        step = (self.max_rep - self.min_rep) / (self.max_level - 1)
        for i in range(self.max_level):
            thresholds.append(int(self.min_rep + i * step))
        return thresholds

    def get_level(self, reps):
        for level, threshold in enumerate(self.level_thresholds, start=1):
            if reps < threshold:
                return max(1, level - 1)
        return self.max_level
    
    def level_to_reps(self, level):
        if level < 1:
            return self.min_rep
        elif level >= self.max_level:
            return self.max_rep
        return self.level_thresholds[level - 1]


 

@bot.slash_command(name="huntercard", description="create a hunter card")
async def slap(ctx: discord.ApplicationContext):
    await ctx.defer()
    levelup_database_guild = levelup_database[str(ctx.guild_id)]
    user_data = levelup_database_guild.find_one({"id": ctx.author.id})
    if user_data:
        user1_avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        response1 = requests.get(user1_avatar_url, stream=True)
        if response1.status_code == 200:
            user1_avatar = Image.open(io.BytesIO(response1.content)).resize((540, 540))
        img = Image.open("hunter.jpg")
        img.paste(user1_avatar, (108, 242))
        draw = ImageDraw.Draw(img)
        hunter_types = {1: "Fighter", 2: "Mage", 3: "Tank", 4: "Assassin", 5: "Healer", 6: "Support", 7: "Summoner", 8: "Beast Tamer", 9: "Archer"}
        draw.text((1350,310), get_rank_by_reps(int(user_data["reps"])), fill='black', font=ImageFont.truetype("Sora Regular 400.ttf",70))
        draw.text((850,330), str(ctx.author.id), fill='black', font=ImageFont.truetype("Sora Regular 400.ttf", 40))
        draw.text((850,500), ctx.author.name, fill='black', font=ImageFont.truetype("Sora Regular 400.ttf", 40))
        outcome = random.randint(1,9)
        for row in range(3):
            for col in range(3):
                x1 = 770 + col * (300 + 20)
                y1 = 640 + 10 + row * (40 + 20)
                x2 = x1 + 300
                y2 = y1 + 40
                draw.rectangle([x1, y1, x2, y2], outline='black', width=3)
                if outcome == row*3 + col + 1:
                    text = f"{hunter_types[row*3 + col + 1]}"
                else:
                    text = " ----- "
                bbox = draw.textbbox((0, 0), text, font=ImageFont.truetype("Sora Regular 400.ttf", 30))
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = x1 + (300 - text_width) // 2
                text_y = y1 + (40 - text_height) // 2
                draw.text((text_x, text_y), text, fill='black', font=ImageFont.truetype("Sora Regular 400.ttf", 30))
        img.save("hunter_license_filled.png")
        file = discord.File("hunter_license_filled.png", filename="hunter_license.png")
        embed = discord.Embed(title="Hunter License", description=f"{ctx.author.mention}'s Hunter Card", color=discord.Color.random())
        embed.set_image(url=f"attachment://hunter_license.png")
        await ctx.respond(embed=embed, file=file)
        try:
            file.close()
            os.remove("hunter_license_filled.png")
        except PermissionError as error: await log_command_error(f"ERROR IN HUNTER CARD COMMAND {error}")




@bot.slash_command(name="slap", description="Fun command to create a Slap image for a user")
async def slap(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    user1 = await bot.fetch_user(member.id)
    user2 = await bot.fetch_user(ctx.author.id)
    user1_avatar_url = user1.avatar.url if user1.avatar else user1.default_avatar.url
    user2_avatar_url = user2.avatar.url if user2.avatar else user2.default_avatar.url
    response1 = requests.get(user1_avatar_url, stream=True)
    response2 = requests.get(user2_avatar_url, stream=True)
    if response1.status_code == 200 and response2.status_code == 200:
        user1_avatar = Image.open(io.BytesIO(response1.content)).resize((190, 190))
        user2_avatar = Image.open(io.BytesIO(response2.content)).resize((180, 180))
        with open("slap.png", "rb") as slap_img:
            slap_image = Image.open(slap_img).resize((837, 736))
        slap_image.paste(user1_avatar, (500, 400))
        slap_image.paste(user2_avatar, (290, 100))
        final_img_bytes = io.BytesIO()
        slap_image.save(final_img_bytes, format="PNG")
        final_img_bytes.seek(0)
        message=f"{member.mention} got **{random.randint(1, 20)}** slaps from {ctx.author.display_name}!"
        embed , file =  await create_embed("👋 Slap!", message, "slap.png", final_img_bytes)
        await ctx.followup.send(embed=embed, file=file)


@bot.slash_command(name="pie", description="Fun command to create a Pie image for a user")
async def pie(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    user_avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response = requests.get(user_avatar_url, stream=True)
    if response.status_code == 200:
        avatar_bytes = io.BytesIO(response.content)
        user_avatar = Image.open(avatar_bytes).resize((328, 328))
        pie_img = Image.open("pie.png").convert("RGBA")
        pie_img.paste(user_avatar, (445, 406), user_avatar)
        final_img_bytes = io.BytesIO()
        pie_img.save(final_img_bytes, format="PNG")
        final_img_bytes.seek(0)
        message = f"{member.mention} got pie {random.randint(1, 20)} times from {ctx.author.display_name}!"
        embed, file = await create_embed("🥧 Pie Attack!", message, "pie.png", final_img_bytes)
        await ctx.followup.send(embed=embed, file=file)


@bot.slash_command(name="trash", description="Fun command to create a Trash image for a user")
async def trash(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    user_avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response = requests.get(user_avatar_url, stream=True)
    if response.status_code == 200:
        avatar_bytes = io.BytesIO(response.content)
        user_avatar = Image.open(avatar_bytes).resize((483, 483))
        trash_img = Image.open("trash.png").convert("RGBA")
        trash_img.paste(user_avatar, (480, 0), user_avatar)
        final_img_bytes = io.BytesIO()
        trash_img.save(final_img_bytes, format="PNG")
        final_img_bytes.seek(0)
        message = f"{member.mention} got {random.randint(1, 20)} trash from {ctx.author.display_name}!"
        embed, file = await create_embed("🗑️ Into the Trash!", message, "trash.png", final_img_bytes)
        await ctx.followup.send(embed=embed, file=file)


@bot.slash_command(name="kill", description="Fun command to create a Kill image for a user")
async def kill(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    sword_img = Image.open("sword.png")
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response = requests.get(avatar_url, stream=True)
    if response.status_code == 200:
        avatar_bytes = io.BytesIO(response.content)
        avatar_img = Image.open(avatar_bytes).resize((175, 175))
        sword_img.paste(avatar_img, (295, 670), avatar_img)
        final_img_bytes = io.BytesIO()
        sword_img.save(final_img_bytes, format="PNG")
        final_img_bytes.seek(0)
        message = f"{member.mention} got {random.randint(1, 20)} kills from {ctx.author.display_name}!"
        embed, file = await create_embed("⚔️ Fatal Blow!", message, "kill.png", final_img_bytes)
        await ctx.followup.send(embed=embed, file=file)



@bot.slash_command(name="getout", description="Fun command to create a getout image for a user")
async def getout(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    base_img = Image.open("door.png")
    avatar_img = await fetch_avatar(member)
    if not avatar_img:
        await ctx.followup.send("Failed to fetch the avatar image.")
        return
    avatar_img = avatar_img.resize((240, 220))
    base_img.paste(avatar_img, (405, 20))
    final_buffer = io.BytesIO()
    base_img.save(final_buffer, format="PNG")
    final_buffer.seek(0)
    embed, file = await create_embed(
        title="🚪 Get Out!",
        description=f"{member.mention} got kicked {random.randint(1, 20)} times by {ctx.author.display_name}!",
        image_filename="getout.png",
        image_bytes=final_buffer)
    await ctx.followup.send(embed=embed, file=file)



@bot.slash_command(name="disable", description="Fun command to create a Disable image for a user")
async def disable(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    base_img = Image.open("disability.png")
    avatar_img = await fetch_avatar(member)
    if not avatar_img:
        await ctx.followup.send("Failed to fetch the avatar image.")
        return
    avatar_img = avatar_img.resize((175, 175))
    base_img.paste(avatar_img, (450, 325))
    final_buffer = io.BytesIO()
    base_img.save(final_buffer, format="PNG")
    final_buffer.seek(0)
    embed, file = await create_embed(
        title="♿ Disabled!",
        description=f"{member.mention} has been disabled!",
        image_filename="disable.png",
        image_bytes=final_buffer)
    await ctx.followup.send(embed=embed, file=file)


@bot.slash_command(name="jail", description="Fun command to create a Jail image for a user")
async def jail(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    base_img = Image.open("jail.png").resize((800, 800))
    avatar_img = await fetch_avatar(member)
    if not avatar_img:
        await ctx.followup.send("Failed to fetch the avatar image.")
        return
    avatar_img = avatar_img.resize((800, 800))
    avatar_img.paste(base_img, (0, 0), base_img)
    final_buffer = io.BytesIO()
    avatar_img.save(final_buffer, format="PNG")
    final_buffer.seek(0)
    embed, file = await create_embed(
        title="🚔 Jail Time!",
        description=f"{member.mention} has been locked up!",
        image_filename="jail.png",
        image_bytes=final_buffer)
    await ctx.followup.send(embed=embed, file=file)


@bot.slash_command(name="spank", description="Fun command to create a Spank image for a user")
async def spank(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    base_img = Image.open("sank.png")
    avatar_img = await fetch_avatar(member)
    author_img = await fetch_avatar(ctx.author)
    if not avatar_img or not author_img:
        await ctx.followup.send("Failed to fetch one or both avatar images.")
        return
    avatar_img = avatar_img.resize((140, 140))
    author_img = author_img.resize((160, 160))
    base_img.paste(avatar_img, (700, 505))
    base_img.paste(author_img, (460, 100))
    final_buffer = io.BytesIO()
    base_img.save(final_buffer, format="PNG")
    final_buffer.seek(0)
    embed, file = await create_embed(
        title="🖐 Spank!",
        description=f"{member.mention} got {random.randint(1, 20)} spanks from {ctx.author.display_name}!",
        image_filename="spank.png",
        image_bytes=final_buffer)
    await ctx.followup.send(embed=embed, file=file)


@bot.slash_command(name="rip", description="Fun command to create a Rip image for a user")
async def rip(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    base_img = Image.open("ripe.png").resize((800, 800))
    avatar_img = await fetch_avatar(member)
    if not avatar_img:
        await ctx.followup.send("Failed to fetch the avatar image.")
        return
    avatar_img = avatar_img.resize((350, 350))
    base_img.paste(avatar_img, (235, 385))
    final_buffer = io.BytesIO()
    base_img.save(final_buffer, format="PNG")
    final_buffer.seek(0)
    embed, file = await create_embed(
        title="🕯️ Rest in Peace",
        description=f"RIP {member.mention} 🕯️",
        image_filename="rip.png",
        image_bytes=final_buffer)
    await ctx.followup.send(embed=embed, file=file)


@bot.slash_command(name="wanted", description="Fun command to create a 'WANTED' poster for a user")
async def wanted(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    base_img = Image.open("wanted.png")
    avatar_img = await fetch_avatar(member)
    if not avatar_img:
        await ctx.followup.send("Failed to fetch the avatar image.")
        return
    avatar_img = avatar_img.resize((447, 447))
    base_img.paste(avatar_img, (150, 250))
    final_buffer = io.BytesIO()
    base_img.save(final_buffer, format="PNG")
    final_buffer.seek(0)
    embed, file = await create_embed(
        title="🚨 WANTED!",
        description=f"{member.mention} is WANTED! 🧤",
        image_filename="wanted.png",
        image_bytes=final_buffer)
    await ctx.followup.send(embed=embed, file=file)


@bot.slash_command(name="marry", description="Fun command to generate a marriage image between two users")
async def marry(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    groom_avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
    bride_avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    groom_response = requests.get(groom_avatar_url)
    bride_response = requests.get(bride_avatar_url)
    if groom_response.status_code != 200 or bride_response.status_code != 200:
        await ctx.followup.send("Failed to fetch one or both avatar images.")
        return
    groom_avatar = Image.open(io.BytesIO(groom_response.content)).resize((100, 100))
    bride_avatar = Image.open(io.BytesIO(bride_response.content)).resize((100, 100))
    groom_avatar = create_circle_avatar(groom_avatar)
    bride_avatar = create_circle_avatar(bride_avatar)
    bg_image_path = "shdi.png"
    bg_img = Image.open(bg_image_path).resize((800, 400))
    bg_img.paste(groom_avatar, (95, 150), groom_avatar)
    bg_img.paste(bride_avatar, (630, 160), bride_avatar)
    final_buffer = io.BytesIO()
    bg_img.save(final_buffer, format="PNG")
    final_buffer.seek(0)
    embed = discord.Embed(
        title="🎀 Wedding Ceremony 🎀",
        description=f"💍 {ctx.author.mention} married {member.mention} 💍",
        color=discord.Color.gold())
    embed.set_image(url="attachment://marry.png")
    embed.set_footer(text="May your love last forever! ❤️")
    await ctx.followup.send(embed=embed, file=discord.File(final_buffer, filename="marry.png"))




@bot.slash_command(name="love", description="Fun command to create a Love image for a user")
async def love(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    author_avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
    member_avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response1 = requests.get(author_avatar_url, stream=True)
    response2 = requests.get(member_avatar_url, stream=True)
    if response1.status_code == 200 and response2.status_code == 200:
        author_img = Image.open(io.BytesIO(response1.content)).resize((400, 400))
        member_img = Image.open(io.BytesIO(response2.content)).resize((400, 400))
        combined_img = Image.new("RGB", (800, 400), "white")
        combined_img.paste(author_img, (0, 0))
        combined_img.paste(member_img, (400, 0)) 
        final_img_bytes = io.BytesIO()
        combined_img.save(final_img_bytes, format="PNG")
        final_img_bytes.seek(0)
        love_percentage = random.randint(0, 100)
        file = discord.File(final_img_bytes, filename="love.png")
        embed = discord.Embed(title="💖 Love Match 💖", description=f"{ctx.author.mention} ❤️ {member.mention}", color=discord.Color.random())
        embed.add_field(name="Love Percentage", value=f"**{love_percentage}%**", inline=False)
        embed.set_image(url="attachment://love.png")
        await ctx.followup.send(embed=embed, file=file)



@bot.slash_command(name="hate", description="Fun command to create a Hate image for a user")
async def hate(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    author_avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
    member_avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response1 = requests.get(author_avatar_url, stream=True)
    response2 = requests.get(member_avatar_url, stream=True)
    if response1.status_code == 200 and response2.status_code == 200:
        author_img = Image.open(io.BytesIO(response1.content)).resize((400, 400))
        member_img = Image.open(io.BytesIO(response2.content)).resize((400, 400))
        combined_img = Image.new("RGB", (800, 400), "white")
        combined_img.paste(author_img, (0, 0))
        combined_img.paste(member_img, (400, 0))
        final_img_bytes = io.BytesIO()
        combined_img.save(final_img_bytes, format="PNG")
        final_img_bytes.seek(0)
        hate_percentage = random.randint(0, 100)
        file = discord.File(final_img_bytes, filename="hate.png")
        embed = discord.Embed(title="💔 Hate Match 💔", description=f"{ctx.author.mention} 💔 {member.mention}", color=discord.Color.random())
        embed.add_field(name="Hate Percentage", value=f"**{hate_percentage}%**", inline=False)
        embed.set_image(url="attachment://hate.png")
        await ctx.followup.send(embed=embed, file=file)
        


@bot.slash_command(name="birthday", description="Birthday wish memes")
async def birth_day_wish(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.defer()
    find_in_db = basic_setup.find_one({"token": 99})
    files_name = [f for f in os.listdir("bday") if os.path.isfile(os.path.join("bday", f))]
    base_image_path = random.choice(files_name)
    image_positions = {
        "1": {"size": (310, 310), "pos": (80, 250)},
        "2": {"size": (385, 475), "pos": (175, 390)},
        "3": {"size": (500, 620), "pos": (200, 30)},
        "6": {"size": (450, 550), "pos": (150, 220)},
        "8": {"size": (420, 560), "pos": (145, 350)},
        "9": {"size": (475, 475), "pos": (123, 400)}
    }
    key = base_image_path[0]
    icon_size = image_positions[key]["size"]
    avatar_position = image_positions[key]["pos"]
    base_img = Image.open(f"bday/{base_image_path}")
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    response = requests.get(avatar_url)
    if response.status_code != 200:
        await ctx.followup.send("Failed to fetch the avatar image.")
        return
    avatar_img = Image.open(io.BytesIO(response.content)).resize(icon_size)
    base_img.paste(avatar_img, avatar_position, mask=avatar_img if avatar_img.mode == 'RGBA' else None)
    final_buffer = io.BytesIO()
    base_img.save(final_buffer, format="PNG")
    final_buffer.seek(0)
    embed = discord.Embed(
        title="🎉 Happy Birthday! 🎂",
        description=f"{member.mention}, {random.choice(find_in_db['birthday_wishes'])} 🎁",
        color=discord.Color(random.randint(0 , 0xFFFFFF))
    )
    embed.set_image(url="attachment://birthday_wish.png")
    await ctx.followup.send(embed=embed, file=discord.File(final_buffer, filename="birthday_wish.png"))
    





############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################



@bot.slash_command(name="profile", description="Get info")
async def system_info(interaction: discord.Interaction, user: discord.Member = None):
    await interaction.response.defer()
    user = user or interaction.user
    Quiz_DataBase = Quiz_db[str(interaction.guild.id)]
    rsi = Quiz_DataBase.find_one({"uid": user.id})
    levelup_database_guild = levelup_database[str(interaction.guild.id)]
    top_users = levelup_database_guild.find_one({"id": user.id})
    img = Image.open("card3.png").resize((1200, 600))
    draw = ImageDraw.Draw(img)
    user1_avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    response1 = requests.get(user1_avatar_url, stream=True)
    if response1.status_code == 200:
        user1_avatar = Image.open(io.BytesIO(response1.content)).resize((400, 380))
        user1_avatar = create_circle_avatar(user1_avatar.convert("RGBA"))
        user1_avatar_mask = user1_avatar.split()[3]
        img.paste(user1_avatar, (90, 105), user1_avatar_mask)
    try:
        font = ImageFont.truetype("Sora Regular 400.ttf", 50)
    except:
        font = ImageFont.load_default()
    draw.text((550,10), interaction.guild.name, font=ImageFont.truetype("Sora Regular 400.ttf", 60), fill="green")
    draw.text((570, 120), "NAME : ", font=font, fill="red")
    draw.text((680, 120), user.name or "N/A", font=font, fill="green")
    
    draw.text((570, 200), "RANK : ", font=font, fill="red")
    draw.text((680, 200), str((top_users or {}).get("rank") or "N/A"), font=font, fill="green")

    draw.text((570, 280), "LEVEL : ", font=font, fill="red")
    draw.text((680, 280), str(top_users.get("level") if top_users.get("level") is not None else "N/A") , font=font, fill="green")

    draw.text((570, 360), "STREAK : ", font=font, fill="red")
    draw.text((710, 360), str(top_users.get("streak") if top_users.get("streak") is not None else "N/A"), font=font, fill="green")

    draw.text((570, 440), "REPS : ", font=font, fill="red")
    draw.text((680, 440), str(top_users.get("reps") if top_users.get("reps") is not None else "N/A"), font=font, fill="green")

    draw.text((570, 520), "QUIZPOINTS : ", font=font, fill="red")
    draw.text((780, 520), str(rsi.get("QuizPoints") if rsi.get("QuizPoints") is not None else "N/A"), font=font, fill="green")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    file = discord.File(fp=buffer, filename="profile_card.png")
    embed = discord.Embed(
        title="📊 Profile Card",
        description=f"User Profile Card.",
        color=discord.Color.random())
    embed.set_image(url="attachment://profile_card.png")
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.followup.send(embed=embed, file=file)


                                    
@bot.slash_command(name="gif", description="Search for a GIF from Giphy")
async def gif(ctx: discord.ApplicationContext, search: str):
    await ctx.defer()
    print(ctx.author.id)
    url = f"http://api.giphy.com/v1/gifs/search?q={search}&api_key={GIPHY_KEY}&limit=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await ctx.followup.send("⚠️ Error fetching GIFs. Please try again later.")
                return
            data = await response.json()
    if not data["data"]:
        await ctx.followup.send("❌ No GIFs found for that search term.")
        return
    gif_choice = random.choice(data["data"])["images"]["original"]["url"]
    embed = discord.Embed(title=f"{search} GIF 🎬", color=discord.Color(random.randint(0 , 0xFFFFFF)))
    embed.set_image(url=gif_choice)
    embed.set_footer(icon_url= ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url ,text=f"Request by {ctx.author.name}")
    await ctx.followup.send(embed=embed)


def generate_leaderboard_image(top_users):
    width = 800
    cell_height = 30
    header_height = 30
    height = len(top_users) * cell_height + header_height
    img = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(img)
    draw.rectangle([1, 1, width - 2, height - 2], fill=(70, 130, 180))
    for i in range(len(top_users)):
        y = header_height + i * cell_height
        draw.line([(0, y), (width, y)], fill="black", width=2)
    col_positions = [70, 500, 630, 720, 800]
    for x in col_positions:
        draw.line([(x, 0), (x, height)], fill="black", width=2)
    headers = ["S No.", "NAME", "REPS", "LEVEL", "RANK"]
    positions = [15, 200, 520, 645, 730]
    try:
        font = ImageFont.truetype("Sora Regular 400.ttf", 18)
    except OSError as e:
        pass
        font = ImageFont.load_default()
    for text, pos in zip(headers, positions):
        draw.text((pos, 5), text, fill="black", font=font)
    for row in range(1, len(top_users) + 1):
        user = top_users[row - 1]
        y_pos = header_height + (row - 1) * cell_height + 5
        draw.text((15, y_pos), str(row), fill="black", font=font)
        draw.text((100, y_pos), user["name"], fill="black", font=font)
        draw.text((515, y_pos), str(int(user["reps"])), fill="black", font=font)
        draw.text((655, y_pos), str(user["level"]), fill="black", font=font)
        draw.text((740, y_pos), get_rank_by_reps(int(user["reps"])), fill="black", font=font)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


@bot.slash_command(name="leaderboard", description="View the top 20 users based on reps")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    levelup_database_guild = levelup_database[str(interaction.guild.id)]
    top_users = list(levelup_database_guild.find().sort("reps", -1).limit(20))
    if not top_users:
        return await interaction.followup.send(embed=discord.Embed(description="No users found in the database.", color=discord.Color.random()))
    file = discord.File(generate_leaderboard_image(top_users), filename="leaderboard_card.png")
    embed = discord.Embed(title="🏆Reps Leaderboard", description=f"Top {len(top_users)} users ranked by reps!", color=discord.Color.gold())
    embed.set_image(url="attachment://leaderboard_card.png")
    embed.set_footer(text="Keep earning reps to climb the leaderboard!")
    await interaction.followup.send(embed=embed, file=file)



@bot.slash_command(name="rank", description="Generate a rank card")
async def rank(interaction: discord.Interaction, user: discord.Member = None):
    await interaction.response.defer()
    user = user or interaction.user
    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    levelup_database_guild = levelup_database[str(interaction.guild.id)]
    user_data = levelup_database_guild.find_one({"id": user.id})
    if user_data:
        level_system = LevelSystem()
        response = requests.get(avatar_url)
        with open("avatar.png", "wb") as file:
            file.write(response.content)
        img = Image.open("avatar.png").resize((230, 230))
        img = create_circle_avatar(img)
        bg = Image.open("bt.png").resize((800, 300))
        bgg = bg.copy()
        bgg.paste(img, (30, 30), img)
        title_font = ImageFont.truetype('Sora Regular 400.ttf', 40)
        draw = ImageDraw.Draw(bgg)
        draw.text((300, 10), f"{interaction.guild.name}", (255, 0, 0), font=title_font)
        draw.text((300, 70), f"Name : {user.name}", (0, 255, 0), font=title_font)
        draw.text((300, 190), f"Reps : {int(user_data['reps'])}", (0, 255, 0), font=title_font)
        draw.text((300, 130), f"Streak : {user_data['streak']}", (0, 255, 0), font=title_font)
        draw.text((300, 250), f"Level : {level_system.get_level(int(user_data['reps']))}", (0, 255, 0), font=title_font)
        bgg.save("rank_card.png")
        file = discord.File("rank_card.png", filename="rank_card.png")
        embed = discord.Embed(title=f"{user.name}'s Rank 🥇🏆", color=discord.Color(random.randint(0 , 0xFFFFFF)))
        embed.set_image(url="attachment://rank_card.png")
        embed.add_field(name="Streak", value=str(user_data['streak']), inline=False)
        embed.add_field(name="Reps", value=str(user_data['reps']), inline=False)
        embed.set_thumbnail(url=avatar_url)
        await interaction.followup.send(embed=embed, file=file)
    else:
        embed = discord.Embed(description=f"{interaction.user.mention}, You are not found in the database ❌", color=discord.Color(random.randint(0 , 0xFFFFFF)))
        await interaction.followup.send(embed=embed)
    await asyncio.sleep(1)
    try:
        file.close()
        os.remove("rank_card.png")
    except PermissionError:
            pass



@bot.slash_command(name="serverinfo", description="Displays server information")
async def serverinfo(ctx: discord.Interaction):
    await ctx.response.defer()
    guild = ctx.guild
    width, height = 600, 350
    img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("Sora Regular 400.ttf", 26)
        font = ImageFont.truetype("Sora Regular 400.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        font = ImageFont.load_default()
    draw.rectangle([10, 10, width - 10, 60], fill=(100, 149, 237))
    draw.text((width // 2 - 120, 20), f"{guild.name} Info", font=title_font, fill="black")
    info = [
        ("Category", str(ctx.channel.category) if ctx.channel.category else "No Category"),
        ("Members", str(guild.member_count)),
        ("Owner", str(guild.owner)),
        ("Server ID", str(guild.id)),
        ("Channel ID", str(ctx.channel.id)),
        ("Created At", ctx.channel.created_at.strftime("%Y-%m-%d")),]
    y = 80
    for label, value in info:
        draw.text((40, y), f"{label}:", font=font, fill="white")
        draw.text((250, y), value, font=font, fill="white")
        y += 40
    if guild.icon:
        icon_response = requests.get(guild.icon.url)
        icon_img = Image.open(io.BytesIO(icon_response.content)).convert("RGBA").resize((80, 80))
        mask = Image.new("L", (80, 80), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 80, 80), fill=255)
        img.paste(icon_img, (500, 10), mask)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    file = discord.File(fp=buffer, filename="server_info.png")
    embed = discord.Embed(
        title="🛠️ Server Info Card",
        description=f"Details of **{guild.name}**",
        color=discord.Color.random())
    embed.add_field(name="Category", value=ctx.channel.category, inline=False)
    embed.add_field(name="Members", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Owner", value=ctx.guild.owner, inline=False)
    embed.add_field(name="Server ID", value=ctx.guild.id, inline=False)
    embed.add_field(name="Channel ID", value=ctx.channel.id, inline=False)
    embed.add_field(name="Created At", value=ctx.channel.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.set_image(url="attachment://server_info.png")
    embed.set_footer(text=f"Requested by {ctx.user.name}")
    await ctx.followup.send(embed=embed, file=file)



@bot.slash_command(name="mention", description="Command for mention everyone wirh jokes ")
async def mention_cmd(ctx: discord.ApplicationContext):
    await ctx.defer()
    url = "https://v2.jokeapi.dev/joke/Any"
    response = requests.get(url)
    if response.status_code == 200:
        joke_data = response.json()
        await ctx.followup.send(f"@everyone \n{joke_data['setup']} \n{joke_data['delivery']}",
        allowed_mentions=discord.AllowedMentions(everyone=True))


@bot.slash_command(name="video", description="Help to find YouTube video link from this command")
async def video_search(ctx: discord.ApplicationContext ,search: str):
    await ctx.response.defer()
    search = search.replace(" ", "+")
    html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search}")
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    if video_ids:
        uls = f"https://www.youtube.com/watch?v={video_ids[0]}"
        await ctx.followup.send(f"Video link: {uls}")
    else:
        await ctx.followup.send("No videos found for your search query.")


@bot.slash_command(name="google", description="Google Search Command")
async def google_search(ctx: discord.ApplicationContext ,search: str):
  await ctx.response.defer()
  while True:
    try:
      await ctx.followup.send(f"https://www.google.com/search?q={'+'.join(search.split(' '))}")
      break
    except: pass


def fetch_video_info_song(url):
    try:
        command = [
            "yt-dlp",
            "--dump-json",
            "--cookies", "cookies.txt",
            url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        return info.get("title", "Unknown Title"), info.get("webpage_url", url)
    except subprocess.CalledProcessError as e:
        raise Exception("Failed to fetch video info") from e

def download_audio(url):
    try:
        command = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "--cookies", "cookies.txt",
            "-o", "music.%(ext)s",
            url
        ]
        subprocess.run(command, check=True)
        return "music.mp3"
    except subprocess.CalledProcessError as e:
        raise Exception("Failed to download audio") from e
    


@bot.slash_command(name="song", description="Download and send an audio file from YouTube")
async def song(ctx: discord.ApplicationContext, query: str):
    await ctx.respond("🎵 Downloading audio... Please wait...")
    if not query.startswith(("https://", "http://")):
        search = query.replace(" ", "+")
        html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        if not video_ids:
            await ctx.respond("❌ No videos found for your search query.")
            return
        query = f"https://www.youtube.com/watch?v={video_ids[0]}"

    try:
        title, video_url = await asyncio.to_thread(fetch_video_info_song, query)
        file_path = "music.mp3"
        await asyncio.to_thread(download_audio, query)
        if not os.path.exists(file_path):
            await ctx.respond("❌ Failed to create audio file.")
            return
        audio = AudioSegment.from_file(file_path)
        trimmed_audio = audio[:400 * 1000]  # 400 seconds
        trimmed_audio.export(file_path, format="mp3", bitrate="192k")
        file = discord.File(file_path, filename="music.mp3")
        embed = discord.Embed(
            title="✅ Music Downloaded Successfully!",
            description="Your requested song has been downloaded successfully!",
            color=discord.Color.random())
        embed.add_field(name="🎶 SONG NAME : ", value=title, inline=False)
        embed.add_field(name="🎶 SONG LINK 🔗 : ", value=video_url, inline=False)
        embed.set_footer(text="Enjoy your music! 🎶")
        await ctx.send(embed=embed, file=file)
    except Exception as e:
        await ctx.respond(f"❌ Error: {str(e)}")
    finally:
        try:
            if os.path.exists("music.mp3"):
                os.remove("music.mp3")
        except PermissionError:
            pass


@bot.slash_command(name="check", description="Get bot system details and performance info")
async def system_info(ctx: discord.Interaction):
    await ctx.response.defer()
    embed = discord.Embed(
        title="📊 Bot System Check",
        description="Details about the bot's performance and system status.",
        color=discord.Color.random())
    embed.add_field(name="🏓 Bot Ping", value=f"{round(bot.latency * 1000)}ms", inline=False)
    embed.add_field(name="⏳ Uptime", value=f"{time.strftime('%Hh %Mm %Ss', time.gmtime(int(time.time() - start_time)))}", inline=False)
    embed.add_field(name="👋 Welcome System", value=f"{'✅' if welcome_database.find_one({'guildId' : ctx.guild_id}) else '❌'}", inline=False)
    embed.add_field(name="📊 Level System", value=f"{'✅' if level_channel.find_one({'guildId' : ctx.guild_id}) else '❌'}", inline=False)
    embed.add_field(name="🔔 Auto-Ping System", value=f"{'✅' if auto_ping_database.find_one({'guildId' : ctx.guild_id}) else '❌'}", inline=False)
    embed.add_field(name="🕵️ Verification System", value=f"{'✅' if set_verification.find_one({'guildId': ctx.guild_id}) else '❌'}", inline=False)
    embed.add_field(name="🎂 Birthday System", value=f"{'✅' if birth_day_chennel.find_one({'guildId': ctx.guild_id}) else '❌'}", inline=False)
    embed.add_field(name="🛠️ Bot Logs System", value=f"{'✅' if bot_logs.find_one({'guildId': ctx.guild_id}) else '❌'}", inline=False)
    embed.set_footer(
        text=f"Requested by {ctx.user.name}",
        icon_url=ctx.user.avatar.url if ctx.user.avatar else ctx.user.default_avatar.url)
    await ctx.followup.send(embed=embed)


############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################




@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.MissingPermissions):
        message = "🚫 You don’t have the required permissions to use this command."
    elif isinstance(error, commands.BotMissingPermissions):
        message = "🤖 I don’t have the required permissions to run this command."
    elif isinstance(error, commands.MissingRole):
        message = f"🚫 You need the role `{error.missing_role}` to use this command."
    elif isinstance(error, commands.MissingAnyRole):
        message = "🚫 You need one of the required roles to use this command."
    elif isinstance(error, commands.NoPrivateMessage):
        message = "🔒 This command can’t be used in DMs."
    elif isinstance(error, commands.CommandOnCooldown):
        message = f"⏳ This command is on cooldown. Try again in {round(error.retry_after, 1)}s."
    elif isinstance(error, commands.BadArgument):
        message = "❌ You provided an invalid argument."
    elif isinstance(error, commands.MissingRequiredArgument):
        message = "⚠️ You are missing a required argument."
    elif isinstance(error, commands.NotOwner):
        message = "🔐 Only the bot owner can use this command."
    elif isinstance(error, commands.CheckFailure):
        message = "🚫 You don’t meet the conditions to use this command."
    elif isinstance(error, discord.Forbidden):
        message = "⚠️ I don’t have permission to perform that action."
    elif isinstance(error, discord.HTTPException):
        message = "🌐 A network error occurred while processing the command."
    elif isinstance(error, commands.CommandInvokeError):
        message = f"💥 An unexpected error occurred while executing the command:\n`{error.original}`"
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        message = f"❗ An unknown error occurred. {error}"
    try:
        await log_command_error(message)
    except: pass


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        message = "🚫 You don’t have the required permissions to use this command."
    elif isinstance(error, commands.BotMissingPermissions):
        message = "🤖 I don’t have the required permissions to run this command."
    elif isinstance(error, commands.MissingRole):
        message = f"🚫 You need the role `{error.missing_role}` to use this command."
    elif isinstance(error, commands.MissingAnyRole):
        message = "🚫 You need one of the required roles to use this command."
    elif isinstance(error, commands.NoPrivateMessage):
        message = "🔒 This command can’t be used in DMs."
    elif isinstance(error, commands.CommandOnCooldown):
        message = f"⏳ This command is on cooldown. Try again in {round(error.retry_after, 1)}s."
    elif isinstance(error, commands.BadArgument):
        message = "❌ You provided an invalid argument."
    elif isinstance(error, commands.MissingRequiredArgument):
        message = "⚠️ You are missing a required argument."
    elif isinstance(error, commands.NotOwner):
        message = "🔐 Only the bot owner can use this command."
    elif isinstance(error, commands.CheckFailure):
        message = "🚫 You don’t meet the conditions to use this command."
    elif isinstance(error, discord.Forbidden):
        message = "⚠️ I don’t have permission to perform that action."
    elif isinstance(error, discord.HTTPException):
        message = "🌐 A network error occurred while processing the command."
    elif isinstance(error, commands.CommandInvokeError):
        message = f"💥 An unexpected error occurred while executing the command:\n`{error.original}`"
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        message = f"❗ An unknown error occurred. {error}"
    try:
        await log_command_error(message)
    except: pass



@tasks.loop(minutes=5)
async def auto_update_levels():
    level_system = LevelSystem()
    for collection_name in levelup_database.list_collection_names():
        collection = levelup_database[collection_name]
        for document in collection.find({}):
            new_level = level_system.get_level(document["reps"])
            if new_level > document["level"]:
                find_in_db = basic_setup.find_one({"token": 99})
                guild = await bot.fetch_guild(int(collection_name))
                member = await guild.fetch_member(document["id"])
                titles = find_in_db["level_name"][0]["auto"]
                avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
                response = requests.get(avatar_url)
                if response.status_code != 200:
                    await log_command_error(f"Failed to fetch avatar for {member.name} in auto updated level")
                    continue
                base_img = Image.open("rankcard.png").convert("RGBA")
                avatar_img = create_circle_avatar(Image.open(io.BytesIO(response.content)).resize((530, 530)))
                base_img.paste(avatar_img, (112, 263), avatar_img)
                draw = ImageDraw.Draw(base_img)
                font_main = ImageFont.truetype("Sora Regular 400.ttf", 70)
                font_sub = ImageFont.truetype("Sora Regular 400.ttf", 60)
                font_num = ImageFont.truetype("Sora Regular 400.ttf", 60)
                font_large = ImageFont.truetype("Sora Regular 400.ttf", 90)
                font_progress = ImageFont.truetype("Sora Regular 400.ttf", 70)
                current_level = level_system.get_level(document['reps'])
                next_title = titles[current_level + 1] if current_level + 1 < len(titles) else "Max Title"
                next_next_title = titles[current_level + 2] if current_level + 2 < len(titles) else "Max Title"
                draw.text((600, 30), f"{guild.name}", fill='green', font=font_main)
                draw.text((960, 310), f"@{member.name}", fill='black', font=font_main)
                draw.text((1350, 700), f"Reps : {document['reps']}", fill='black', font=font_num)
                draw.text((750, 460), f"New Title {next_title}", fill='black', font=font_sub)
                draw.text((750, 580), f"Next Title {next_next_title}", fill='black', font=font_sub)
                rep_diff = level_system.level_to_reps(document['level'] + 1) - level_system.level_to_reps(document['level'])
                draw.text((250, 950), f"+{rep_diff}", fill='black', font=font_large)
                progress_width = int(1070 * (document["reps"] / level_system.max_rep))
                progress_width = max(0, min(1070, progress_width))
                draw.rounded_rectangle([(630, 770), (1700, 900)], radius=50, fill="lightgray")
                draw.rounded_rectangle([(630, 770), (630 + progress_width, 900)], radius=50, fill="grey")
                draw.text((1000, 800), f"{document['reps']} / {level_system.max_rep}", fill='black', font=font_progress)
                final_buffer = io.BytesIO()
                base_img.save(final_buffer, format="PNG")
                final_buffer.seek(0)
                level_channel_db = level_channel.find_one({"guildId":guild.id})
                if level_channel_db:
                    target_channel = await bot.fetch_channel(level_channel_db["channelId"])
                    embed = discord.Embed(title="card", description=f"{member.mention}", color=discord.Color.random())
                    embed.set_image(url="attachment://rankupcard.png")
                    await target_channel.send(embed=embed, file=discord.File(final_buffer, filename="rankupcard.png"))
                    collection.update_one({"id": document["id"]}, {"$set": {"level": new_level}})




@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.guild is None:
        return
    existing = ban_words_list.find_one({"guildId": str(message.guild.id)})
    if existing:
        for banned_word in message.content.lower().split(" "):
            if banned_word in existing["BanWord"]:
                await message.delete()
                await message.channel.send(
                    f"🚫 {message.author.mention}, your message contained a banned word and was deleted.",
                    delete_after=10)
                break
    smmdb = Smm_db.find_one({"id": message.author.id})
    if not smmdb:
        Smm_db.insert_one({"id":message.author.id , "cash": 0.000 , "history_in":[], "history_out":[]})
    Quiz_DataBase = Quiz_db[str(message.guild.id)]
    rsi = Quiz_DataBase.find_one({"uid": message.author.id})
    if not rsi:
        Quiz_DataBase.insert_one({
                "uid": message.author.id , "QuizNumber":0, "QuizPoints": 0,
                "CorrectAnswer": 0, "WrongAnswer": 0, "SkipAnswer":0})
        
    levelup_database_guild = levelup_database[str(message.guild.id)]
    user_data = levelup_database_guild.find_one({"id": message.author.id})
    now = datetime.datetime.now(datetime.timezone.utc)
    if not user_data:
        levelup_database_guild.insert_one({"id": message.author.id, "last_active": now, 
            "name":message.author.name, "rank":"A", "level":0 ,  "streak": 0, "last_login": None, 
            "reps": 0.5, "daily": 0.5,"weekly": 0.5,"monthly": 0.5,"last_message": str(datetime.date.today())})
    else:
        levelup_database_guild.update_one(
            {"id":  message.author.id},
            {
            "$inc": { "reps": 0.5, "daily": 0.5, "weekly": 0.5, "monthly": 0.5},
            "$set": {"last_message": str(datetime.date.today()), "last_active": now}
            })
    await bot.process_commands(message)


@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot or message.guild is None:
        return
    check_gulid = bot_logs.find_one({"guildId": message.guild.id})
    if check_gulid:
        DeleteData = delete_data_db[str(message.guild.id)]
        DeleteData.insert_one({
        "author_id": message.author.id,
        "content": message.content or None,
        "channel_id": message.channel.id,
        "timestamp": message.created_at.isoformat(),
        "deleted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "attachments": [a.url for a in message.attachments]
    })


    
@tasks.loop(hours=1)
async def check_birthday_leaderboard():
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    for document in birth_day_chennel.find({}):
            try:
                guild = await bot.fetch_guild(int(document["guildId"]))
                guild_db = birthday_database[str(guild.id)]
                for birthday_entry in guild_db.find({}):
                    if str(today) == birthday_entry["dob"]:
                        member = await guild.fetch_member(birthday_entry['userId'])
                        await send_event_log(f"🎂 Sending birthday wish to {member.name} ({member.id})")
                        setup_data = basic_setup.find_one({"token": 99})
                        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
                        response = requests.get(avatar_url)
                        if response.status_code != 200:
                            await log_command_error(f"❌ Failed to fetch avatar for {member.name}")
                            continue 
                        files_name = [f for f in os.listdir("bday") if os.path.isfile(os.path.join("bday", f))]
                        base_image_path = random.choice(files_name)
                        base_image_key = base_image_path[0]
                        image_positions = {
                                "1": {"size": (310, 310), "pos": (80, 250)},
                                "2": {"size": (385, 475), "pos": (175, 390)},
                                "3": {"size": (500, 620), "pos": (200, 30)},
                                "6": {"size": (450, 550), "pos": (150, 220)},
                                "8": {"size": (420, 560), "pos": (145, 350)},
                                "9": {"size": (475, 475), "pos": (123, 400)}
                                }    
                        if base_image_key not in image_positions:
                            await log_command_error(f"⚠️ No position data for image starting with '{base_image_key}'")
                            continue
                        position_data = image_positions[base_image_key]
                        base_img = Image.open(f"bday/{base_image_path}").convert("RGBA")
                        avatar_img = Image.open(io.BytesIO(response.content)).convert("RGBA").resize(position_data["size"])
                        base_img.paste(avatar_img, position_data["pos"], mask=avatar_img)
                        final_buffer = io.BytesIO()
                        base_img.save(final_buffer, format="PNG")
                        final_buffer.seek(0)
                        target_channel = await bot.fetch_channel(document["channelId"])
                        try:
                            embed = discord.Embed(
                                title="🎉 Happy Birthday! 🎂",
                                description=f"{member.mention}, {random.choice(setup_data['birthday_wishes'])} 🎁",
                                color=discord.Color.random())
                            embed.set_image(url="attachment://birthday_wish.png")
                            await target_channel.send(
                                        embed=embed,
                                        file=discord.File(final_buffer, filename="birthday_wish.png")
                                    )
                            await send_event_log(f"✅ Birthday wish sent in {target_channel.name}")
                            next_year_dob = f"{datetime.datetime.today().year + 1}-{today[5:]}"
                            guild_db.update_one({"userId": member.id}, {"$set": {"dob": next_year_dob}})
                            break
                        except Exception as e:
                            await log_command_error(f"⚠️ Error sending birthday message in {target_channel.name}: {e}")
            except Exception as outer_error:
                await log_command_error(f"⚠️ General Error: {outer_error}")
         





@tasks.loop(minutes=30)
async def mention_all():
    for check_mention in auto_ping_database.find({}):
        try:
            new_time = datetime.datetime.strptime(check_mention["new"], "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            new_time = datetime.datetime.strptime(check_mention["new"], "%Y-%m-%d %H:%M:%S")
        if new_time < datetime.datetime.now():
            guild = bot.get_guild(check_mention["guildId"])
            if guild:
                channel = guild.get_channel(check_mention["channelId"])
                if channel:
                    response = requests.get("https://v2.jokeapi.dev/joke/Any")
                    if response.status_code == 200:
                        joke_data = response.json()
                        embed = discord.Embed(
                            title="Joke of the Day! ",
                            description=f"{joke_data['setup']}\n\n**Answer**: {joke_data['delivery']}",
                            color=discord.Color.random())
                        embed.set_footer(text="Auto Mention Bot")
                        await channel.send("@everyone",embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))        
                        auto_ping_database.update_one({"guildId" : check_mention["guildId"],
                                                       "channelId" : check_mention["channelId"]},
                                                      {"$set": {
                                                          "last" : check_mention["new"],
                                                          "new" : add_time_to_current_date(check_mention["time"])}})


@bot.event
async def on_member_join(member: discord.Member):
    find_in_db = basic_setup.find_one({"token": 99})
    find_in_db_1 = welcome_database.find_one({"guildId": member.guild.id})
    if find_in_db_1:
        avatar_url = member.avatar.url if member.avatar else None
        folder_path = "wellcome"
        image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
        if image_files:
            random_image = random.choice(image_files)
            image_path = os.path.join(folder_path, random_image)
            file = discord.File(image_path, filename="welcome.jpg")
            image_url = "attachment://welcome.jpg"
        else:
            file = None
            image_url = None
        
        embed = discord.Embed(
            title=f"Welcome to Our {member.guild.name} Server",
            description=random.choice(find_in_db["welcome_message"]),
            color=discord.Color.random()
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="USER NAME", value=f"{member.mention}", inline=False)
        embed.add_field(name="JOIN DATE", value=f"{datetime.datetime.now().strftime('%d %b, %Y')}", inline=False)
        embed.add_field(name="USERID", value=f"{member.id}", inline=False)
        if image_url:
            embed.set_image(url=image_url)
        embed.set_footer(text="MADE BY ERROR", icon_url=find_in_db["owner_icon"])
        
        channel_id = find_in_db_1["channelId"]
        welcome_channel = bot.get_channel(channel_id)
        if welcome_channel:
            if file:
                await welcome_channel.send(embed=embed, file=file)
            else:
                await welcome_channel.send(embed=embed)
        else:
            await log_command_error("Error: Welcome channel not found!")



@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    check_birthday_leaderboard.start()
    mention_all.start()
    auto_update_levels.start()

bot.run(DISCORD_KEY)
