from discord.ext import commands
from discord_slash import cog_ext, SlashContext
import discord
import json, requests

class Stats(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  def jsonurl(self, url):
    r = requests.get(url, headers={'Connection':'close'})
    if not r:
      return "1"
    rlist = json.dumps(r.json(), sort_keys=True, indent=4)
    return json.loads(rlist)

  @cog_ext.cog_slash(name="stats")
  async def _stats(self, ctx: SlashContext, servernick: str):
    if len(servernick) >= 3:
      data = self.jsonurl("https://lexten.cz/discordauth/json.php?stats="+servernick.replace("#","%23"))
      try:
        if data["code_err"] == 0:
          desc="**CT killů:** "+str(data["stats"]["ct_kills"])+"\n**T killů:** " + str(data["stats"]["t_kills"])+"\n**CT umrtí:** " + str(data["stats"]["ct_deaths"]) +"\n**T umrtí:** "+ str(data["stats"]["t_deaths"])+"\n**Nahraný čas:** "+str(data["stats"]["time"])+"\n**VIP:** "+str(data["stats"]["vip"])+"\n**První připojení:** "+str(data["stats"]["firstjoin"])+"\n**Naposledy připojen:** "+str(data["stats"]["lastjoin"])
          embed = discord.Embed(color=0x00cafc, title=data["message"], url="https://lexten.cz/stats/"+data["stats"]["steamid"]+"/", description=desc)
          embed.set_thumbnail(url=data["stats"]["avatar"])
          await ctx.send(embed=embed)
        elif data["code_err"] == 1:
          desc=''
          for i in range(0, len(data["players"])):
            desc+=data["players"][i]+", "
          embed = discord.Embed(color=0xffffff, title="Seznam podobných nicků:", description=desc)
          await ctx.send(content="Zadej prosím přesnější nick:", embed=embed)
        else:
          await ctx.send(data["message"])
   else:
     await ctx.send(":exclamation: Zadej alespoň 3 znaky")

  @cog_ext.cog_slash(name="topstats")
  async def _topstats(self, ctx: SlashContext, servernick: str, order: str = "score"):
    orders={"kills","deaths","kd","time","score","warden_count","lg_claims","pp_claims","fd_count"}
    if not order in orders:
      return await ctx.send(":exclamation: Neplatný typ statistik.")
    if len(servernick) >= 3:
      data = self.jsonurl("https://lexten.cz/discordauth/json.php?topstats="+servernick.replace("#","%23")+"&order="+order)
      if data["code_err"] == 0:
        e = discord.Embed(color=0x00cafc, description="Statistiky hráče **"+servernick+"** podle **"+order+"**:")
        e.set_image(url=data["message"])
        await ctx.send(embed=e)
      elif data["code_err"] == 1:
        desc=''
        for i in range(0, len(data["players"])):
          desc+=data["players"][i]+", "
        embed = discord.Embed(color=0xffffff, title="Seznam podobných nicků:", description=desc)
        await ctx.send(content="Zadej prosím přesnější nick:", embed=embed) 
      else:
        await ctx.send(data["message"])
    else:
      await ctx.send(":exclamation: Zadej alespoň 3 znaky")

def setup(bot):
  bot.add_cog(Stats(bot))