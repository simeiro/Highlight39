import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import requests
import typing
import random
import setting

Intents = discord.Intents.all()
Intents.message_content = True
Intents.members = True
bot = commands.Bot(command_prefix="39!", intents=Intents)
bot.remove_command('help') #初期helpコマンドの削除
url = "https://vocadb.net/api/songs/highlighted?fields=PVs&languagePreference=Japanese"

async def request_judge(ctx):
    data = await setting.guilds_collection.find_one({
        "guild_id": ctx.guild.id
    })
    if data == None:
        await ctx.send("この機能は自動送信機能に登録していないと使用できません\n39!setで登録してください")
        return -1
    if data["api_requests"] >= 5:
        await ctx.send("本日のリクエスト上限に達しました\nリクエスト数は午前0時にリセットされます")
        return -1
    return data["api_requests"]

def make_text(data, num=None):
    text=""
    nico_text=""
    other_text=""
    if num is None: #変数1つの場合
        date_str = data["publishDate"][:data["publishDate"].rfind("T")]
        text += data["defaultName"] + " (" + data["artistString"] +" , " 
        text += date_str + ")\n" #日付を取得
        for pvs in data["pvs"]:
            if "youtu.be" in pvs["url"]:
                text += "<" + pvs["url"] + ">\n"
                break
            elif "nicovideo" in pvs["url"]:
                nico_text += "<" + pvs["url"] + ">\n"
            else:
                other_text += "<" + pvs["url"] + ">\n"
    else:
        date_str = data[num]["publishDate"][:data[num]["publishDate"].rfind("T")]
        # date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        # datetime_obj = datetime.combine(date_obj, datetime.min.time())
        # if datetime_obj < datetime.now() - timedelta(days=21): #3週間前以降の情報は取得しない
        #     return ""
        text += data[num]["defaultName"] + " (" + data[num]["artistString"] +" , " 
        text += date_str + ")\n" #日付を取得
        for pvs in data[num]["pvs"]:
            if "youtu.be" in pvs["url"]:
                text += "<" + pvs["url"] + ">\n"
                break
            elif "nicovideo" in pvs["url"]:
                nico_text += "<" + pvs["url"] + ">\n"
            else:
                other_text += "<" + pvs["url"] + ">\n"

    if "youtu.be"  in text:
        return text
    if "nicovideo"  in nico_text:
        text += nico_text
        return text
    if other_text != "":
        text += other_text
        return text
    text += "-----urlなし-----"
    return text

def make_ids(data, num: int):
    date_str = data[num]["publishDate"][:data[num]["publishDate"].rfind("T")]
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    datetime_obj = datetime.combine(date_obj, datetime.min.time())
    if datetime_obj < datetime.now() - timedelta(days=21): #3週間前以降の情報は取得しない
        return "empty"
    return str(data[num]["id"])

@bot.command(aliases=["s"])
async def song(ctx, num:typing.Optional[int] = None):
    request_num = await request_judge(ctx)
    if request_num == -1:
        return
    if num is None:
        num = 5
    if(num > 20 or num < 1):
        await ctx.send("値の範囲は1~20までです")
        return
    async with ctx.channel.typing():
        text=""
        vocadb_data = requests.get(url).json()
        for i in range(num):
            text += make_text(vocadb_data, i)
        await ctx.send(text)
    
    update = {"$set": {"api_requests": request_num + 1}}
    await setting.guilds_collection.update_one({
        "guild_id": ctx.guild.id
    },update)


@bot.command()
async def set(ctx):
    data = await setting.guilds_collection.find_one({
        "guild_id": ctx.guild.id
    })
    if data == None:
        await setting.guilds_collection.insert_one({
            "guild_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "api_requests": 0
        })
        await ctx.send("設定が完了しました\n再設定する場合は39!deleteで削除を行い再度39!setを実行してください")
    else:
        await ctx.send("既に追加済みです")

@bot.command()
async def delete(ctx):
    result = await setting.guilds_collection.delete_many({
        "guild_id": ctx.guild.id
    })
    if result.deleted_count == 0:
        await ctx.send("登録情報が見つかりませんでした\n39!setで登録することができます")
    else:
        await ctx.send("削除しました")

@bot.command(aliases=["r"])
async def rand(ctx):
    request_num = await request_judge(ctx)
    if request_num == -1:
        return
    for i in range(20):#最近のsongidを取得
        recently_num = await setting.songs_collection.find_one({
            "ranking": i
        })
        if recently_num != None:
            break
    while True:
        rand_num = random.randint(0, int(recently_num["song_id"]))
        rand_url = f"https://vocadb.net/api/songs/{rand_num}?fields=PVs&lang=Japanese"
        async with ctx.channel.typing():
            response = requests.get(rand_url)
            try:
                response.raise_for_status()  #idの曲情報が存在するか判別
                vocadb_data = response.json()
                await ctx.send(make_text(vocadb_data))
                update = {"$set": {"api_requests": request_num + 1}}
                await setting.guilds_collection.update_one({
                    "guild_id": ctx.guild.id
                },update)
                break
            except:
                continue

@bot.command()
async def song_set(ctx):
    if ctx.author.id != int(setting.OWNER_ID):
        return
    await setting.songs_collection.delete_many({})
    vocadb_data = requests.get(url).json()
    for i in range(20):
        id = make_ids(vocadb_data, i)
        await setting.songs_collection.insert_one({
            "song_id": id,
            "ranking": i
        })
    await ctx.send("セットしました")

@tasks.loop(minutes=1)
async def send_data():
    now = datetime.now()
    if now.hour == 0 and now.minute == 0:
        update = {"$set": {"api_requests": 0}}
        await setting.guilds_collection.update_many({}, update)
    if now.minute == 39:
        vocadb_data = requests.get(url).json()
        text = "新たなハイライト曲です\n\n"
        before_ids=[]
        for i in range(20):
            before_id = await setting.songs_collection.find_one({
                "ranking": i
            })
            if before_id == None:
                continue
            before_ids.append(before_id["song_id"])
        await setting.songs_collection.delete_many({})#id取得後data削除
        for i in range(20):
            after_id = make_ids(vocadb_data, i)
            if after_id == "empty":
                continue
            else:
                await setting.songs_collection.insert_one({
                    "song_id": after_id,
                    "ranking": i
                })
            if after_id not in before_ids:
                text += make_text(vocadb_data, i)
        if text == "新たなハイライト曲です\n\n":
            return
        channel_ids = await setting.guilds_collection.find({}, {"channel_id": 1}).to_list(length=None)
        for channel_id in channel_ids:
            id = int(channel_id["channel_id"])
            channel = bot.get_channel(id)
            await channel.send(text)


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="39!help",description=setting.description,color=0x88cccc)
    await ctx.send(embed=embed)

@bot.event
async def on_guild_join(guild):
    channel = guild.system_channel
    if channel is not None:
        await channel.send(setting.invite_msg)

@bot.event
async def on_guild_remove(guild):
    await setting.guilds_collection.delete_many({
        "guild_id": guild.id
    })

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print('Bot is ready.')
    send_data.start() #@tasks.loop
    await bot.change_presence(activity=discord.Game(name="39!help"))
    owner = bot.get_user(int(setting.OWNER_ID))
    await owner.send("起動しました")

bot.run(setting.TOKEN)
