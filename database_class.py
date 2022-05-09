from discord.ext import commands
from replit import db

class Database(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def nopermission(self, ctx):
    return ":exclamation:"+ctx.author.mention + ", nemáš oprávnění k tomuto příkazu!"

  @commands.command(brief="Zobrazí proměnné uložené v DB [ADMIN]")
  async def showdb(self, ctx, prefix = ''):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(self.nopermission(ctx))
    matches = db.prefix(prefix)
    if len(matches) == 0:
      await ctx.send("0 dat nalezeno");
    else:
      database = ", " 
      database = database.join(matches)
      await ctx.send(database)
  @commands.command(brief="Zobrazí hodnotu zadané proměnné z DB [ADMIN]")
  async def selectdb(self, ctx, variable):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(self.nopermission(ctx))
    await ctx.send("Výsledek hledání "+variable+": "+str(db[variable]))
  
  @commands.command(brief="Smaže proměnnou z DB [ADMIN]")
  async def removedb(self, ctx, variable):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(self.nopermission(ctx))
    matches = db.prefix(variable)
    if len(matches) == 1:
      del db[matches[0]]
      await ctx.send(ctx.author.mention+", smazána proměnná "+matches[0])
    else:
      return ctx.send(ctx.author.mention+", upřesni prosím název proměnné. Nalezené proměnné: "+matches.partition(", "))
  @commands.command(brief="Změní proměnnou IP uloženou v databázi na zadaný parametr [ADMIN]")
  async def setip(self, ctx, ip):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(self.nopermission(ctx))

    db["ip"] = ip
    await ctx.send(ctx.author.mention + ", IP byla změněna na: "+db["ip"])

  @commands.command(brief="Změní VIP role ID  uloženou v databázi na zadaný parametr [ADMIN]")
  async def setviprole(self, ctx, roleid:int):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(self.nopermission(ctx))

    db["vip_role"] = roleid
    await ctx.send(ctx.author.mention + ", VIP role byla změněna na: <@&"+str(db["vip_role"])+">")

  @commands.command(brief="Nastavení doby kontroly calladmin [ADMIN]")
  async def calladmindelay(self, ctx, delay: int):
    if ctx.guild is None:
      return await ctx.send(":exclamation: Tenhle příkaz lze použít jen na serveru.") 
    if not ctx.author.guild_permissions.administrator:
      return await ctx.send(self.nopermission(ctx))
    if delay > 0 and delay <= 300:
      db["calladmin_check"] = delay
      await ctx.send("Delay calladmin kontroly nastaven na: " + str(delay)+ " sekund")
    else:
      await ctx.send(":exclamation: Lze nastavit pouze hodnotu v rozmezí 1-300 (včetně).")
    


def setup(bot):
 bot.add_cog(Database(bot))