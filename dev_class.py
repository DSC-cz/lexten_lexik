from discord.ext import commands
import discord
import requests
import json
import time
import datetime
from discord_slash import cog_ext, SlashContext
import asyncio
import random
from replit import db

class Ostatni(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def jsonurl(self, url):
    r = requests.get(url)
    if not r:
      return "1"
    rlist = json.dumps(r.json(), sort_keys=True, indent=4)
    return json.loads(rlist)

  @commands.command(brief="Zobrazí aktuální UNIX TIMESTAMP")
  async def devtimestamp(self, ctx):
    await ctx.send("Timestamp: " + str(int(time.time())))
 
  @commands.command()
  async def request(self, ctx):
    await ctx.send(self.jsonurl("https://lexten.cz/discordauth/json.php?request"))
  
  @commands.command(brief="Vypíše zprávu, kterou má bot upravit [ADMIN]")
  async def readmessage(self, ctx, channel: discord.TextChannel, message: int):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(":exclamation: Na tenhle příkaz nemáš oprávnění.")
    
    msg = discord.utils.get(await channel.history(limit=1000).flatten(), id=message)
    if len(msg.embeds) > 0:
      for embed in msg.embeds:
        await ctx.send(embed.to_dict())
      return True
    else:
      return await ctx.send(msg.content)
    
    return await ctx.send(":exclamation: Nelze přečíst zprávu co není ode mě.")

  @commands.command(brief="Nastaví status serveru na kanál [ADMIN]")
  async def status(self, ctx):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(":exclamation: Na tenhle příkaz nemáš oprávnění.")

    getdata = self.jsonurl("https://lexten.cz/scripts/fh_status.php")

    players = []

    for i in range(1, len(getdata["players_list"])):
      if "stats" in getdata["players_list"][i]:
        if getdata["players_list"][i]["name"] != "":
          players.append("["+getdata["players_list"][i]["name"]+"]("+getdata["players_list"][i]["stats"]+") \t•\t **Čas:** "+str(round(getdata["players_list"][i]["time"]/60,1))+" minut")
      else:
        if getdata["players_list"][i]["name"] != "":
          players.append(getdata["players_list"][i]["name"]+" \t•\t** Čas:** "+str(round(getdata["players_list"][i]["time"]/60,1))+" minut")

    embed = discord.Embed(color=0xfc034e, title=getdata["hostname"], description=(getdata["is_running"] is True and ":green_circle:" or ":red_circle:")+"** | IP: [82.208.17.49:27479](https://tinyurl.com/join-lexten) • Web: https://lexten.cz**\n\n**Hráči ("+str(getdata["players"]-1)+"/26):**\n> "+'\n> '.join(players))
    embed.set_image(url="https://lexten.cz/scripts/actualmap_image.php?v="+str(random.getrandbits(128)))
    embed.set_footer(text="Aktualizováno " + str(getdata["last_query"]))
    
    message = await ctx.send(embed=embed)
    db["status"] = [message.id, message.channel.id, message.guild.id]
   
    
  @cog_ext.cog_slash(name="lastadminconnect")
  async def _lastadminconnect(self, ctx: SlashContext, minutes: int = 1):
    data= self.jsonurl("https://lexten.cz/discordauth/json.php?adminjoin=true&since="+str(int(time.time())-(minutes*60)))
    if len(data) == 0:
      if minutes == 1:
        await ctx.send("Před 1 minout nebyl žádný člen AT přítomný na serveru.")
      elif minutes > 1 and minutes <= 120:
        await ctx.send("Před "+str(minutes)+" minutami nebyl žádný člen AT přítomný na serveru.")
      else:
        await ctx.send(":exclamation: Lze zadat pouze minuty v rozmezí 1 - 120 (včetně)")
    else:
      admins = ''
      for i in range(0, len(data)):
        admins+=data[i]
        if(i != len(data)-1):
           admins+=", "
      if minutes == 1:
        await ctx.send("Před 1 minout byl na serveru: " + admins)
      elif minutes > 1 and minutes <= 120:
        await ctx.send("Před "+str(minutes)+" minutami byl na serveru: "+admins)
      else:
        await ctx.send(":exclamation: Lze zadat pouze minuty v rozmezí 1 - 120 (včetně)")

  @cog_ext.cog_slash(name="shortenurl")
  async def _shortenurl(self, ctx: SlashContext, url:str):
    if url.startswith("http"):
        message = await ctx.send("Zkracuji ... Tahle zpráva se za chvíli upraví.")
        url="https://api.shrtco.de/v2/shorten?url="+url
        r = requests.get(url=url)
        rlist = json.dumps(r.json(), sort_keys=True, indent=4)
        data = json.loads(rlist)
        if data["ok"] == True:
          await message.edit(content=":arrow_right: "+data['result']['full_short_link'])
        else:
          await message.edit(content=":octagonal_sign: Něco se pokazilo... Zkus jiný odkaz nebo kontaktuj administrátora.")
    else:
      await ctx.send(":exclamation: Pravděpodobně nezadáváš URL, zkopíruj jí prosím celou :slight_smile:")

  @cog_ext.cog_slash(name="covid")
  async def covid(self, ctx:SlashContext):
    data = self.jsonurl("https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/zakladni-prehled.json")["data"][0]
    embed = discord.Embed(color=0xfc034e, title="Aktuální informace o Covid-19", url="https://onemocneni-aktualne.mzcr.cz", description="**Včerejší počet testů:** "+str(data["provedene_testy_vcerejsi_den"])+"\n**Potvrzených nákaz:** "+str(data["potvrzene_pripady_vcerejsi_den"]) + "\n**Aktuálně nakažených:** "+str(data["aktivni_pripady"])+ " \n**Vykázáno očkování včera:** "+ str(data["vykazana_ockovani_vcerejsi_den"])+"\n**Naočkováno celkem:** "+str(data["ockovane_osoby_celkem"]))
    await ctx.send(embed=embed)
  


def setup(bot):
  bot.add_cog(Ostatni(bot))
