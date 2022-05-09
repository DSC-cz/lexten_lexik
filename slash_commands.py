import requests, json, asyncio

async def slash_commands(bot, AppID, TOKEN):
  for guilds in bot.guilds:
      #url = "https://discord.com/api/v9/applications/"+AppID+"/guilds/"+str(guilds.id)+"/commands"
      url = "https://discord.com/api/v9/applications/"+AppID+"/commands"

      commands = {
        0:{
          "name": "vip",
          "description": "Zobrazí seznam VIP hráčů"
        },
        1:{
          "name": "delvip",
          "description": "Odebere VIP roli hráči",
          "options": [
            {
              "name":"user",
              "description": "Uživatel, kterému VIP chci odebrat",
              "type":6,
              "required":True
            }
          ]
        },
        2:{
          "name": "setvip",
          "description": "Přidá VIP roli hráči", 
          "options": [
            {
              "name":"user",
              "description": "Uživatel, kterému VIP dám",
              "type":6,
              "required":True
            },
            {
              "name":"length",
              "description": "Číselná doba, po jakou bude VIP roli uživatel mít (def. 30)",
              "type": 4,
              "required":False
            },
            {
              "name":"unit","description":"Jednotka času k předešlé číselné délce (def. d)",
              "type": 3,
              "required":False,
              "choises": [
                {"name":"Dny","value":"d"},{"name":"Hodiny","value":"h"},{"name": "Minuty","value": "m"}
              ]
            }
          ]
        },
        3:{
          "name":"lastadminconnect",
          "description":"Zobrazí členy teamu, kteří se připojili před zadanými minutami.",
          "options":[
            {
              "name":"minutes",
              "description":"Počet minut (v rozmezí 1 - 120)",
              "type": 4,
              "required": False
            }
          ]
        },
        4:{
          "name":"refreshvip",
          "description": "Zkontroluje ihned všechny VIP hráče a přiřadí role"
        },
        5:{
          "name":"shortenurl",
          "description":"Zkrátí zadaný URL odkaz.",
          "options":[
            {
              "name":"url",
              "description":"Odkaz, který chci zkrátit",
              "type": 3,
              "required": True
            }
          ]
        },
        6:{
          "name":"covid",
          "description":"Základní informace k aktuálnímu dostupnému datu."
        },
        7:{
          "name":"stats",
          "description":"Vyhledá statistiky hráče na základě zadaného nicku.",
          "options":[
            {
              "name":"servernick",
              "description":"Uživatel, kterého statistiky chci vypsat",
              "type": 3,
              "required":True
            }
          ]
        },
        8:{
          "name":"topstats",
          "description":"Zobrazí na základě zadaného nicku pozici v TOP statistikách",
          "options":[
            {
              "name":"servernick",
              "description":"Uživatel, kterého statistiky chci vypsat",
              "type": 3,
              "required":True
            },
            {
              "name":"order",
              "description":"Řazení podle: score, kills, deaths, kd, time, warden_count, fd_count, pp_claims, lg_claims",
              "type":3,
              "required":False
            }
          ]
        },
        9:{
          "name":"getaccountid",
          "description":"Vypíše accountid zadaného hráče",
          "options":[
            {
              "name":"servernick",
              "description":"Uživatel, kterého accountid chci vypsat",
              "type":3,
              "required":True
            }
          ]
        },
        10:{
          "name":"boostkarma",
          "description":"Odměna za boost serveru, přidá karmu hráči (lze použít 1x denně)",
          "options":[
            {
              "name":"accountid",
              "description":"AccountID hráče, kterému chci karmu přičíst (/getaccountid)",
              "type":4,
              "required":True
            }
          ]
        },
        11:{
          "name":"createchannel",
          "description": "VIP/Nitro Booster - vytvoří soukromou voice místnost na serveru."
        }
      }


      headers = {
        "Authorization": "Bot "+TOKEN
      }
      
      for i in range(11, len(commands)):
        await asyncio.sleep(10)
        r = requests.post(url, json=commands[i], headers=headers)
        if r:
          print("[G: "+str(guilds.id)+"] "+commands[i]['name'] + ": success")
        else:
          print("[G: "+str(guilds.id)+"] "+commands[i]['name'] + ": error"+r.text)