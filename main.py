
import discord
from discord.ext import commands
import requests
import json
import os
import re
import pythonping
from pythonping import ping as pinger
import datetime
import tempfile
import chardet
import asyncio
import aiofiles
import pathlib
from discord.ext import tasks
import io
import colorama
from colorama import Style, Fore
colorama.init()

TOKEN = 'TOKEN'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

credit_system_user = {}
CREDITS_PER_USE = 2  # Set the number of credits required per use

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté!')
    bot.status = discord.Status.dnd
    activity = discord.Activity(type=discord.ActivityType.streaming,url = "https://twitch.tv/discord", name="by sex")
    await bot.change_presence(activity=activity)
    save_credits()

@bot.event
async def on_disconnect():
    save_credits()

def save_credits():
    try:
        with open('credit_system.json', 'r') as file:
            global credit_system
            credit_system = json.load(file)
    except FileNotFoundError:
        pass

def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 

def save_credits():
    with open('credit_system.json', 'w') as file:
        json.dump(credit_system, file, default=serialize_datetime)

credit_system = {}  # initialize the credit system as an empty dictionary
save_credits()      # call save_credits() after initializing credit_system
daily_users = {}  

import datetime

@bot.command()
async def claim(ctx):
    global credit_system
    now = datetime.datetime.now()
    # check if the user has already received their daily credits today
    datetime.datetime.now
    if ctx.author.id in credit_system and (now - credit_system[ctx.author.id]["last_daily"]) < datetime.timedelta(days=1):
        await ctx.send("Vous avez déjà reçu vos crédits quotidiens.")
    else:
    # if not, give them their daily credits and update the time
        if not ctx.author.id in credit_system:
            credit_system[ctx.author.id] = {"balance": 10, "last_daily": datetime.datetime.now()}
        else:
            credit_system[ctx.author.id]["balance"] = credit_system[ctx.author.id]["balance"] + 10
        embed = discord.Embed(title="Tu a eu tes 10 credits du jour.", description=f"", color=0x00ff00)
        embed.set_footer(text="searchdb")
        embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/N9_6kcP4wna8swPbcseyLaldZUKz9ZdISGxBcAeP_d0/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1242828852263387136/182acac7db921b0d479e952625bc3edb.webp?format=webp&width=300&height=300")
        embed.color = 0x1519F0
        await ctx.send(embed=embed)
        save_credits()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user in message.mentions:
        await message.reply('Mon prefix est !')
    await bot.process_commands(message)

@bot.command()
async def addcr(ctx, user: discord.Member, amount: int):
    authorized_ids = [1257325365022691411, 214, 421, 412]  # Met les id de tes owner

    if ctx.author.id not in authorized_ids:  
        await ctx.send("Désolé, vous n'êtes pas autorisé à ajouter des crédits.")
        return

    if user.id not in credit_system:
        credit_system[user.id] = {"balance":0, "last_daily": 0}
    credit_system[user.id]["balance"] += amount
    balance = credit_system[user.id]["balance"]
    await ctx.send(f"{user.mention} à maintenant {balance} credits.")
    save_credits()
   
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Commandes", description="", color=0x00ff00)
    embed.set_footer(text="sousdomain")
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/N9_6kcP4wna8swPbcseyLaldZUKz9ZdISGxBcAeP_d0/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1242828852263387136/182acac7db921b0d479e952625bc3edb.webp?format=webp&width=300&height=300")
    embed.add_field(name="", value="les paramètres mis entre `<> sont obligatoires. Si tu as besoin d'aide utilise: +help.", inline=False)
    embed.add_field(name="!search <mot-clé>", value="Rechercher une personnes dans les DB FiveM.", inline=False)
    embed.add_field(name="!restorecord <mot-clé>", value="Rechercher une personnes dans les DB restorecord.", inline=False)
    embed.add_field(name="!discordd <mot-clé>", value="Rechercher une personnes dans les DB discord.", inline=False)
    embed.add_field(name="!nazapi <mot-clé>", value="Rechercher une personnes dans les DB nazapi.", inline=False)
    embed.add_field(name="!geopip <mot-clé>", value="Rechercher une personnes avec son ip .", inline=False)
    embed.add_field(name="!balance", value="Voir son Solde de credits.", inline=False)                             
    embed.add_field(name="!addcr <id> <cr>", value="Ajouter des credits a un Utilisateurs. (Admin Only)", inline=False)
    embed.color = 0x1519F0
    await ctx.send(embed=embed)
    

@bot.command()
async def snusbase(ctx, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande. Merci de ping un fondateur pour en obtenir.")
        return

    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')

    snusbase_auth = 'sbuncd7b2bfcflweh3dkbeqsuzlzqk'
    snusbase_api = 'https://api-experimental.snusbase.com'
    url = f"{snusbase_api}/data/search"
    headers = {
        'auth': snusbase_auth,
        'Content-Type': 'application/json',
    }
    body = {
        'terms': [query],
        'types': ["email", "username", "lastip", "hash", "password", "name"],
        'wildcard': False,
    }

    response = requests.post(url, headers=headers, json=body)

    # Ajout de débogage pour afficher le statut et le contenu de la réponse
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")

    if response.status_code == 200:
        result = response.json()
        if result:
            formatted_response = json.dumps(result, indent=2)

            # Create a BytesIO object with the formatted JSON response
            output = io.BytesIO(formatted_response.encode())

            # Create a File object with the BytesIO object and a filename
            file = discord.File(output, filename=u"snsbase_response.txt")

            # Send the file as a message
            credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
            await ctx.author.send(file=file, content=f"")
            await ctx.send(f'Votre recherche a été envoyée à vos DM.')

            # Enregistrer le résultat de la recherche dans le fichier JSON
            search_results[query] = result
            save_results(search_results)
        else:
            await ctx.send(f'Aucun fichier trouvé avec le nom : {query}')
    else:
        await ctx.send(f'Erreur lors de la recherche : {response.status_code}')

    save_credits()

@bot.command()
async def search(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "database"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def mastercard(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "mastercard"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def shein(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "shein"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def onlyfan(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "onlyfan"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def restorecord(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "restorecord"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
               if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def tebex(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "nazapi"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def paypal(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "paypal"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()


@bot.command()
async def discordd(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "discordd"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def email(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "email"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def steam(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "steam"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def allo(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "allo"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def epicgames(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "epicgames"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()

@bot.command()
async def orange(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "orange"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()
        
@bot.command()
async def geoip(ctx, ip_address):
    ip_info_url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(ip_info_url)
    ip_info_data = response.json()
    embed = discord.Embed(title=f"Informations sur l'adresse IP : {ip_address}", color=0x1519F0)
    embed.add_field(name="Ip", value=ip_info_data.get('ip', 'N/A'), inline=False)
    embed.add_field(name="Pays", value=ip_info_data.get('country', 'N/A'), inline=True)
    embed.add_field(name="Région", value=ip_info_data.get('region', 'N/A'), inline=True)
    embed.add_field(name="Ville", value=ip_info_data.get('city', 'N/A'), inline=True)
    embed.add_field(name="Opérateurs", value=ip_info_data.get('org', 'N/A'), inline=False)
    loc = ip_info_data.get('loc', '').split(',')
    if len(loc) == 2:
        latitude, longitude = loc
        embed.add_field(name="Adresse Approximative", value=f"{latitude}, {longitude}", inline=True)
    vpn_status = "Oui" if ip_info_data.get('vpn') else "Non"
    embed.add_field(name="VPN", value=vpn_status, inline=True)

    await ctx.send(f'Regarde tes dm !')
    await ctx.author.send(embed=embed)

@bot.command()
async def fivem_vip(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "Fivemdb"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personne est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()     

@bot.command()
async def mc_vip(ctx, *, query):
    if ctx.author.id not in credit_system or credit_system[ctx.author.id]["balance"] < CREDITS_PER_USE:
        await ctx.send("Vous n'avez pas assez de crédits pour utiliser cette commande merci de ping un Fondateur pour en obtenir.")
        return
      
    await ctx.send(f'Veuillez patienter pendant que je rassemble les informations...')
    dump_directory = "Fivemdb"
    result = []

    for file in os.listdir(dump_directory):
        with open(os.path.join(dump_directory, file), "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if query in line:
                    result.append(line.strip())

    if result:
        async with aiofiles.open(f'results.txt', 'w', encoding='utf-8') as f:
            await f.write('\n'.join(result))

        with open(f'results.txt', 'rb') as f:
            await ctx.send(f'Les resultats a été envoyée à vos DM.')
            await ctx.author.send(file=discord.File(f))
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
    else:
        await ctx.send(f'Cette personnes est introuvable: {query}')
        credit_system[ctx.author.id]["balance"] -= CREDITS_PER_USE
        save_credits()             
       
@bot.command()
async def balance(ctx):
    if ctx.author.id not in credit_system:
        balance = 0
    else:
        balance = credit_system[ctx.author.id]["balance"]
    embed = discord.Embed(title="Vos Credits", description=f"Salut, {ctx.author.mention} \n **Tu as** {balance} **credits.**", color=0x00ff00)
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/N9_6kcP4wna8swPbcseyLaldZUKz9ZdISGxBcAeP_d0/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1242828852263387136/182acac7db921b0d479e952625bc3edb.webp?format=webp&width=676&height=676")
    embed.color = 0x1519F0
    await ctx.send(embed=embed)

        
save_credits()
bot.run(TOKEN)