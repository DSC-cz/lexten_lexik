from discord.ext import commands
import discord
from replit import db
from discord_slash import cog_ext, SlashContext
import requests, json
import datetime

class Boost(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  def jsonurl(self, url):
    r = requests.get(url, headers={'Connection':'close'})
    if not r:
      return "1"
    rlist = json.dumps(r.json(), sort_keys=True, indent=4)
    return json.loads(rlist)

  @cog_ext.cog_slash(name="getaccountid")
  async def _getaccountid(self, ctx: SlashContext, servernick:str):
    if len(servernick) < 3:
      return await ctx.send("Zadej alespoň 3 znaky")

    data = self.jsonurl("https://lexten.cz/discordauth/json.php?getaccountid="+servernick)

    if data["code_err"] == 0:
      await ctx.send("AccountID uživatele "+servernick+": **" + data["message"] + "**\n:exclamation: Pozor: pokud chceš použít /boostkarma, ujisti se, že "+servernick+" není připojený na serveru")
    elif data["code_err"] == 1:
      desc = ", "
      desc = desc.join(data["players"])

      embed = discord.Embed(color=0xffffff, title="Seznam podobných nicků:", description=desc)
      await ctx.send(content="Zadej prosím přesnější nick:", embed=embed) 
    else:
      await ctx.send(data["message"])

  @cog_ext.cog_slash(name="boostkarma")
  async def _boostkarma(self, ctx: SlashContext, accountid:int):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    role = ctx.guild.get_role(852885887871877141)
    if not role in ctx.author.roles:
      return await ctx.send(":exclamation: Tento příkaz můžeš použít pouze pokud boostuješ server.")
    now = datetime.datetime.now()
    if db["boost"]["day"] == now.strftime("%d"):
      if ctx.author.id in db["boost"]["players"]:
        return await ctx.send(":exclamation: Tento příkaz jsi dnes již použil, znovu půjde použít až od 02:00")
    else:
      db["boost"]["day"] = now.strftime("%d")
      db["boost"]["players"] = []

    data = self.jsonurl("https://lexten.cz/discordauth/json.php?boostkarma=true&accountid="+str(accountid))
    if data["code_err"] == 0:
      await ctx.send("Hráči **" + data["name"] + "** bylo přidáno +100 karmy (aktuálně: **"+data["karma"]+"**)")
      db["boost"]["players"].append(ctx.author.id)
    else:
      await ctx.send(data["message"])

def setup(bot):
  bot.add_cog(Boost(bot))