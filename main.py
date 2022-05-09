import discord
import sys
from discord.ext.commands import Bot, CommandNotFound
import discord_slash
from discord_slash import SlashContext
import time, math
from datetime import datetime, timedelta, timezone
import pytz
import os
from replit import db
from keep_alive import keep_alive
import threading
import asyncio
import requests
import json
import random
from slash_commands import slash_commands

AppID = os.environ["Lexik_AppID"]
TOKEN = os.environ["Lexik_TOKEN"]

extensions = [
    "database_class", "dev_class", "vip_class", "boost_class", "stats_class"
]

intents = discord.Intents.all()

actual_time = pytz.utc.localize(datetime.now())

bot = Bot(command_prefix="/", intents=intents)
slash = discord_slash.SlashCommand(bot, override_type=True)
bot.start_time = actual_time.astimezone(pytz.timezone('Europe/Prague'))

if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Nepodařilo se načíst {}\n{}'.format(extension, exc))


@bot.event
async def on_ready():
    #await discord_slash.utils.manage_commands.remove_all_commands_in(bot_id=AppID, bot_token=TOKEN,guild_id=671711873665597450)
    print("{0.user} je připraven na věc!".format(bot))
    #await slash_commands(bot, AppID, TOKEN)
    sys.setrecursionlimit(10**6)
    threading.Timer(
        10.0, await timer(status=240,
                          start=0,
                          role=1079,
                          channel=359,
                          server_status=30)).start()


async def timer(status: int,
                start: int,
                role: int,
                channel: int,
                server_status: int,
                players: str = "0 hráčů"):
    actual_time = pytz.utc.localize(datetime.now())
    bot.start_time = actual_time.astimezone(pytz.timezone('Europe/Prague'))

    if server_status >= 30:
        server_status = 0
        await status_timer()
    if role >= 1080:
        role = 0
        await role_check()
    if channel >= 360:
        channel = 0
        await channel_timer()
    if status >= 240:
        data = False
        #data = jsonurl("https://lexten.cz/discordauth/json.php?players=true&ip="+db["ip"])
        if data:
            players = data
        else:
            players = "0 hráčů"
        status = 0
    else:
        status = 0
        #status = status + 1
    if start == 0:
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="/refreshvip"))
        start = 0
        #start = 1
    else:
        await bot.change_presence(activity=discord.Game(name=players))
        start = 0
    await asyncio.sleep(10)
    await timer(status, start, role + 1, channel + 1, server_status + 1,
                players)


async def status_timer():
    message = db["status"]

    try:
        getdata = jsonurl("https://lexten.cz/scripts/fh_status.php")
    except:
        print("Nepodařilo se načíst server status")

    players = []
    print(getdata["players_list"])
    print(len(getdata["players_list"]))
    if len(getdata["players_list"]) >= 0:
        for i in range(1, len(getdata["players_list"])):
            if "stats" in getdata["players_list"][i]:
                if getdata["players_list"][i]["name"] != "":
                    players.append(
                        "[" + getdata["players_list"][i]["name"] + "](" +
                        getdata["players_list"][i]["stats"] +
                        ") \t•\t **Čas:** " +
                        str(round(getdata["players_list"][i]["time"] /
                                  60, 1)) + " minut")
            else:
                if getdata["players_list"][i]["name"] != "":
                    players.append(
                        getdata["players_list"][i]["name"] +
                        " \t•\t** Čas:** " +
                        str(round(getdata["players_list"][i]["time"] /
                                  60, 1)) + " minut")

        embed = discord.Embed(
            color=0xfc034e,
            title=getdata["hostname"],
            description=(getdata["is_running"] is True and ":green_circle:"
                         or ":red_circle:") +
            "** | IP: [82.208.17.49:27479](https://tinyurl.com/join-lexten) • Web: https://lexten.cz**\n\n**Hráči ("
            + str(getdata["players"] - 1) + "/26):**\n> " +
            (getdata["players"] != 0 and '\n> '.join(players) or ""))
        embed.set_image(
            url="https://lexten.cz/scripts/actualmap_image.php?v=" +
            str(random.getrandbits(128)))
        embed.set_footer(text="Aktualizováno " + str(getdata["last_query"]))

    for guilds in bot.guilds:
        if guilds.id == message[2]:
            guild = discord.utils.get(bot.guilds, name=guilds.name)
            channel = discord.utils.get(guild.channels, id=message[1])

            msg = discord.utils.get(await
                                    channel.history(limit=1000).flatten(),
                                    id=message[0])

            try:
                return await msg.edit(embed=embed)
            except:
                print("Nepodarilo se upravit server status")
        else:
            continue


async def channel_timer():
    tcmatches = db.prefix("tc_")
    for i in range(0, len(tcmatches)):
        guilds = bot.get_guild(db[tcmatches[i]][0])
        channel = discord.utils.get(guilds.channels, id=db[tcmatches[i]][1])
        if channel is not None:
            if db[tcmatches[i]][2] < int(bot.start_time.timestamp()) and len(
                    channel.members) == 0:
                print(
                    str(bot.start_time.strftime("[%H:%M:%S]")) + " Kanál " +
                    channel.name + " smazan")
                await channel.delete()
                del db[tcmatches[i]]

    print(
        str(bot.start_time.strftime("[%H:%M:%S]")) + " Vytvořeno " +
        str(len(tcmatches)) + " docasnych kanalu.")


async def role_check():
    matches = db.prefix('tg_')
    if len(matches) > 0:
        for i in range(0, len(matches)):
            if int(time.time()) > int(db[matches[i]][1]):
                for guilds in bot.guilds:
                    if guilds.id != 671711873665597450:
                        continue
                    guild = discord.utils.get(bot.guilds, name=guilds.name)
                    user = guild.get_member(db[matches[i]][2])
                    if user:
                        role = guild.get_role(db[matches[i]][0])
                        if role is None:
                            print(guild.name + " | Neexistující role")
                            continue
                        await asyncio.sleep(5)
                        remove = await user.remove_roles(role)

                        await asyncio.sleep(5)
                        if role not in user.roles and (matches[i] in db):
                            del (db[matches[i]])
                        else:
                            print("Nepodařila se odebrat role " + role.name +
                                  " hráči " + user.name)
                    else:
                        print(guild.name + " | Uživatel " +
                              str(db[matches[i]][2]) + " nenalezen")
                        continue

    print(
        str(bot.start_time.strftime("[%H:%M:%S]")) +
        " Docasne role zkontrolovany.")
    return True


def jsonurl(url):
    r = requests.get(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'})
    if not r:
        return "1"
    rlist = json.dumps(r.json(), sort_keys=True, indent=4)
    return json.loads(rlist)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return


@bot.event
async def on_message(message):
    if (message.author == bot.user):
        return
    detect = [
        "ahoj", "čau", "cau", "cus", "čus", "cc", "cs", "zdar", "nazdar"
    ]
    pozdrav = ["Ahooj", "Nazdaar", "cs", "cc", "čaau", "čuus", "zdaar"]
    messl = message.content.lower()
    if (any(detectx in messl
            for detectx in detect)) and (bot.user.mentioned_in(message) or
                                         "lexik" in messl or "lexík" in messl):
        await message.channel.send(pozdrav[random.randint(0,
                                                          len(pozdrav) - 1)])

    if "calladmin" in messl:
        if bot.user.mentioned_in(message):
            if message.author.discriminator != "0000":
                return
            actual_time = int(time.time())
            await asyncio.sleep(db["calladmin_check"])
            data = jsonurl(
                "https://lexten.cz/discordauth/json.php?adminjoin=true&since="
                + str(actual_time))
            if len(data) == 0:
                await message.channel.send("Žádný člen teamu se nepřipojil")
            else:
                admins = ''
                for i in range(0, len(data)):
                    admins += data[i]
                    if (i != len(data) - 1):
                        admins += ", "
                await message.channel.send(message.content + "Připojili se: " +
                                           admins)

    if "kde najdu ip" in messl or "kde bych našel ip" in messl or "jak se připojím" in messl or "jak si můžu zahrát" in messl:
        ip = db["ip"]
        await message.channel.send("{0.mention}".format(message.author) +
                                   ", IP serveru je: " + ip + ".")

    if "kde najdu dema" in messl or "kde bych našel demo" in messl or "kde najdu záznam" in messl or "kde bych našel záznam" in messl:
        await message.channel.send(
            "{0.mention} ".format(message.author) +
            ", dema najdeš na webu https://lexten.cz/dema")

    if (('může' in messl or 'mohl' in messl)
            and ('admin' in messl or 'mod' in messl) and 'server' in messl):
        await message.channel.send(
            "{0.mention} ".format(message.author) +
            ", admina můžeš zavolat ze serveru přes příkaz **calladmin <důvod>**"
        )

    await bot.process_commands(message)


keep_alive()
bot.run(TOKEN)
