import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
import json, requests
from replit import db
import time
from datetime import timedelta, datetime

class VIP(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.start_time = bot.start_time

  def jsonurl(self, url):
    r = requests.get(url, headers={'Connection':'close'})
    if not r:
      return "1"
    rlist = json.dumps(r.json(), sort_keys=True, indent=4)
    return json.loads(rlist)

  @cog_ext.cog_slash(name="vip")
  async def _vip(self, ctx: SlashContext):
    data = self.jsonurl("https://lexten.cz/discordauth/json.php?viplist=true")
    desc = ""
    for i in range(0, len(data)):
      desc+="**["+data[i]['nick']+"](https://lexten.cz/stats/"+data[i]['cid']+"/)** - " + data[i]['vip']+"\n"
    embedv=discord.Embed(title=":date: Seznam VIP hráčů:",description=desc, color=0xffd03b)
    await ctx.send(embed=embedv)

  @cog_ext.cog_slash(name="setvip")
  async def _setvip(self, ctx: SlashContext, user: discord.Member = None, length: int = 30, unit: str = 'd'):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(":exclamation: Na tenhle příkaz nemáš oprávnění.")
    times = {"h":3600, "m": 60, "d": 86400}
    times_str = {"h":"hodin", "m": "minut", "d": "dnů"}
    if (unit != "h") and (unit != "m") and (unit != "d"):
      return await ctx.send(":exclamation: Parametr jednotky může být jen d, h nebo m (den, hodina, minuta)")
    if user:
      role = discord.utils.get(ctx.guild.roles, id=db["vip_role"])
      db["tg_"+str(user.id)+"_VIP"] = [role.id, int(time.time()+length*times[unit]), user.id]
      await user.add_roles(role)
      await ctx.send("Uživateli "+str(user.mention) +" přidána role VIP na "+str(length) + " " + times_str[unit])

  @cog_ext.cog_slash(name='delvip')
  async def _delvip(self, ctx: SlashContext, user: discord.Member = None):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(":exclamation: Na tenhle příkaz nemáš oprávnění.")
    if user:
      if "tg_"+str(user.id)+"_VIP" in db:
        del db["tg_"+str(user.id)+"_VIP"]
      else:
        return await ctx.send("Uživatel " + str(user.mention) + " není evidován, odeber skupinu ručně.")
      role = discord.utils.get(ctx.guild.roles, id=db["vip_role"])
      await user.remove_roles(role)
      await ctx.send("Uživateli "+str(user.mention)+" odebrána role VIP.")
  
  @cog_ext.cog_slash(name="refreshvip")
  async def _refreshvip(self, ctx: SlashContext):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    data = self.jsonurl("https://lexten.cz/discordauth/json.php?vipdiscordid=true")
    namelist = ""
    for guilds in self.bot.guilds:
      guild = self.bot.get_guild(guilds.id)
      for i in range(0, len(data)):    
        user = guild.get_member(int(data[i][0]))
        if user:
          if not "tg_"+data[i][0]+"_VIP" in db:
            role = discord.utils.get(ctx.guild.roles, id=db["vip_role"])
            await user.add_roles(role)
            db["tg_"+data[i][0]+"_VIP"] = [role.id,int(data[i][1]),user.id]
            namelist += user.mention+", " 
    if not namelist:
      await ctx.send("Během kontroly nebylo přidělena žádnému hráči VIP role.\n\n:information_source: Pro přidělní VIP role si musíš propojit Discord s webem, [tutoriál nalezneš kliknutím sem](https://lexten.cz/forum/topic/146)")
    else:
      await ctx.send("Uživatelům " + namelist + " přidána VIP role.")
  
  @cog_ext.cog_slash(name="createchannel")
  async def _createchannel(self, ctx):
    nitro = ctx.guild.get_role(852885887871877141)
    vip = ctx.guild.get_role(db["vip_role"])
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.")
    if not vip in ctx.author.roles and not nitro in ctx.author.roles:
      return await ctx.send(":exclamation: Na tenhle příkaz mají oprávnění pouze boosteři a VIP")
      
    if "tc_"+str(ctx.author.id) in db:
        return await ctx.send(":exclamation: Už máš jednu místnost vytvořenou!")

    category = discord.utils.get(ctx.guild.categories, id=db["temporary_rooms_category"])
    server = ctx.guild
    channel = await server.create_voice_channel(ctx.author.name, category=category, user_limit = 5)

    everyone = channel.overwrites_for(ctx.guild.default_role)
    everyone.connect = False
    author = channel.overwrites_for(ctx.author)
    author.connect = True
    author.move_members = True
    await channel.set_permissions(ctx.guild.default_role,overwrite=everyone)
    await channel.set_permissions(ctx.author,overwrite=author)

    end = self.start_time + timedelta(hours=1)

    if end < (self.start_time + timedelta(hours=2, minutes=10)):
      end = end + timedelta(hours=1)

    db["tc_"+str(ctx.author.id)] = [ctx.guild.id, channel.id, int(end.timestamp())]

    await ctx.send(":point_right: Tvůj kanál " + channel.mention + " byl vytvořen. Kanál v případě neaktivity bude smazán v " + end.strftime("%H:%M:%S")+".")
  
  @commands.command(name="temproomscat", brief="Nastavení kategorie pro soukromé kanály (category mention)")
  async def temproomscat(self, ctx, cat: discord.CategoryChannel):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.")
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(":exclamation: Na tenhle příkaz nemáš oprávnění.")
    
    db["temporary_rooms_category"] = cat.id
    await ctx.send(ctx.author.mention + ", kategorie pro soukromé kanály nastavena na " + cat.mention)

  @commands.command(name="deletechannel", brief="Smaže soukromý kanál uživatele ihned (channel mention)")
  async def deletechannel(self, ctx, channel: discord.VoiceChannel):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.")
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(":exclamation: Na tenhle příkaz nemáš oprávnění.")

    success = False
    matches = db.prefix("tc_")
    for i in range(0, len(matches)):
      if channel.id == db[matches[i]][1]:
        await ctx.send(ctx.author.mention + ", kanál **"+channel.name+"** smazán.")
        await channel.delete()
        del db[matches[i]]
        success = True
    
    if success == False:
      await ctx.send(":exclamation: Tenhle kanál není součástí soukromých kanálů.")

def setup(bot):
  bot.add_cog(VIP(bot))