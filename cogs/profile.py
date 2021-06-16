import discord
import matplotlib
import aiohttp
import json
import os
import re
import time
import traceback
import random
import sys
import requests
import jsonData as jbin
import requests
import shutil
from discord import Color
from discord.ext import commands
from colorama import Fore
import colorama
colors = dict(matplotlib.colors.cnames)
colorama.init()


def getUsers():
    return jbin.read()['users']


def pushUsers(data):
    datas = jbin.read()
    datas['users'] = data
    jbin.update(datas)


def getRepertoire():
    return jbin.read()['repertoire']


def restDaily(last):
    pro = last+float(24*60*60)
    now = time.time()

    ellapsed = now-last
    rest = pro-last-ellapsed

    if rest <= 0:
        return None
    else:
        return rest


def prettyTime(s):
    hours = s//3600
    s -= hours*3600
    mins = s//60
    s -= mins*60
    secs = s
    chaine = ""
    if hours:
        chaine += f"{int(round(hours,0))}h "
    if mins:
        chaine += f"{int(round(mins,0))}mn "
    if secs:
        chaine += f"{int(round(secs,0))}s "
    return chaine


def profileEmb(user):
    nom = user['nom']
    trophees = user['trophees']
    koinz = str(user["koinz"])
    join = user['join']
    pfp = user['pfp']
    daily = user["daily"]
    invent = user['inventory']
    possess = user['possess']
    if invent:
        invent = [str(obj) for obj in invent]
        invent[0] = "- "+invent[0]
    if possess:
        possess = [str(obj) for obj in possess]
        possess[0] = "- "+possess[0]
    daily = "dans "+prettyTime(restDaily(daily)
                               ) if restDaily(daily) else "prêt !"
    embed = discord.Embed(
        title=nom, description=f"Sur le serveur depuis le {join['day']}/{join['month']}/{join['year']} à {join['hour']}:{join['minute']} ", colour=discord.Color.green())
    embed.add_field(name="Trophés", value=str(trophees), inline=True)
    embed.add_field(name="Koinz", value=koinz, inline=True)
    embed.add_field(name="Prochain daily",
                    value="Le prochain daily est "+daily, inline=False)
    embed.add_field(name="Inventaire", value="\n- ".join(invent)
                    or "Votre inventaire est vide", inline=False)
    embed.add_field(name="Items possédés", value="\n- ".join(possess)
                    or "Vous ne possédez rien", inline=False)
    embed.set_thumbnail(url=pfp)
    embed.set_footer(text="Fictiotopia - Profile")

    return embed


def daily(user, gain):
    nom = user['nom']
    pfp = user['pfp']
    daily = user["daily"]
    color = discord.Color.orange() if gain else discord.Color.green()
    daily = "dans " + \
        prettyTime(restDaily(daily)
                   ) if gain else f"Vous récupérez vos 50 koinz quotidiens !"
    embed = discord.Embed(title="Daily", description=f"{daily}", colour=color)
    embed.set_thumbnail(url=pfp)
    embed.set_footer(text="Fictiotopia - Daily")

    return embed


async def aventureError(ctx):
    await ctx.send(f":x: **L'utilisateur n'a pas commencé son aventure**")


async def adminError(ctx):
    await ctx.send(f":x: **La permission administrateur est requise pour cette commande**")


class Profile(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.roleSF = self.client.get_guild(
            778307254663249950).get_role(780773725519347723)
        self.device = "Koinz"

    @commands.command(name='start', description='Commence ton aventure RP', aliases=['commencer'], usage=f'start')
    async def start(self, ctx):
        message = ctx.message
        listContent = message.content.split(' ')
        content = ' '.join(listContent[1:])
        args = content.strip().split(' ')
        users = getUsers()
        if not str(message.author.id) in users:
            if not self.roleSF.id in [r.id for r in message.author.roles]:
                joined = ctx.guild.get_member(ctx.message.author.id).joined_at
                pfp = f'https://cdn.discordapp.com/avatars/{message.author.id}/{message.author.avatar}.png?size=4096'

                users[str(message.author.id)] = {
                    'nom': message.author.name,
                    'trophees': 0,
                    'koinz': 0,
                    'join': {
                        'minute': joined.minute,
                        'hour': joined.hour,
                        'day': joined.day,
                        "month": joined.month,
                        'year': joined.year
                    },
                    "inventory": [],
                    "possess": [],
                    "pfp": pfp,
                    "daily": time.time()-24*60*60
                }
                pushUsers(users)
                await ctx.send(":white_check_mark: **Votre profil a bien été créé**", embed=profileEmb(users[str(message.author.id)]))
            else:
                await ctx.send(f":x: **Vous ne pouvez pas commencer le RP si vous avez le role {self.roleSF.name}**")
        else:
            await ctx.send(":x: **Votre aventure est déja lancée, utilisez la commande ``profile`` pour voir votre profil**")

    @commands.command(name='update', description='Mets à jour tes informations de compte sur ton profil', aliases=['maj'], usage='update')
    async def update(self, ctx):
        message = ctx.message
        listContent = message.content.split(' ')
        content = ' '.join(listContent[1:])
        args = content.strip().split(' ')
        users = getUsers()

        joined = ctx.guild.get_member(ctx.message.author.id).joined_at
        pfp = f'https://cdn.discordapp.com/avatars/{message.author.id}/{message.author.avatar}.png?size=4096'

        users[str(message.author.id)] = {
            'nom': message.author.name,
            'trophees': users[str(message.author.id)]['trophees'],
            'koinz': users[str(message.author.id)]['koinz'],
            'join': users[str(message.author.id)]['join'],
            "inventory": users[str(message.author.id)]['inventory'],
            "possess": users[str(message.author.id)]['possess'],
            "pfp": pfp,
            "daily": users[str(message.author.id)]['daily']
        }
        pushUsers(users)
        await ctx.send(":white_check_mark: **Votre profil a bien été mit à jour**", embed=profileEmb(users[str(message.author.id)]))

    @commands.command(name='profile', description='Affiche votre profil ou celui d\'un membre', aliases=['p', 'profil'], usage='profile (membre)')
    async def profile(self, ctx):
        message = ctx.message
        listContent = message.content.split(' ')
        content = ' '.join(listContent[1:])
        args = content.strip().split(' ')
        user = message.mentions[0] if message.mentions else message.author
        users = getUsers()
        if str(user.id) in users:
            await ctx.send(embed=profileEmb(users[str(user.id)]))
        else:
            await aventureError(ctx)

    @commands.command(name='daily', description='Permet de récolter ses 50 koinz quotidiens', aliases=['quotidien', 'dl'], usage='daily')
    async def daily(self, ctx):
        message = ctx.message
        listContent = message.content.split(' ')
        content = ' '.join(listContent[1:])
        args = content.strip().split(' ')
        user = message.mentions[0] if message.mentions else message.author
        users = getUsers()
        if str(user.id) in users:
            users = getUsers()
            userProfile = users[str(message.author.id)]
            gain = True
            if not restDaily(userProfile['daily']):
                userProfile['koinz'] += 50
                userProfile['daily'] = time.time()
                gain = False
            pushUsers(users)
            await ctx.send(embed=daily(userProfile, gain))
        else:
            await aventureError(ctx)

    @commands.command(name='possess', description='Envoie les items possédés du joueur', aliases=['possession', 'pss'], usage='possess')
    async def possess(self, ctx):
        message = ctx.message
        users = getUsers()
        if str(message.author.id) in users:
            userPossess = users[str(message.author.id)]['possess']
            if userPossess:
                userPossess = ["**"+str(obj)+"**" for obj in userPossess]
                userPossess[0] = "- "+userPossess[0]
            await ctx.send(embed=discord.Embed(title=f"Objets possédés de {message.author.name}", description="\n- ".join(userPossess) or "Vous ne possédez rien", color=discord.Color.purple()))
        else:
            await aventureError(ctx)

    @commands.command(name='buy', description='Permet d\'acheter un objet', aliases=['pay', 'acheter'], usage='buy [objet]')
    async def buy(self, ctx, *objet):
        message = ctx.message
        users = getUsers()
        objet = " ".join(objet).lower().replace("é", 'e').replace("è", "e").replace(
            "ê", 'e').replace("à", "a")
        items = getRepertoire()['item']
        if not str(message.author.id) in users:
            await aventureError(ctx)
            return
        if not objet:
            await ctx.send(embed=discord.Embed(title="Précisez un objet", description="Veuillez préciser un objet du shop à acheter", color=discord.Color.red()))
            return

        if not objet in items:
            await ctx.send(embed=discord.Embed(title="Objet non existant", description=f"``{objet}`` n'existe pas\nPour connaitre les items à acheter utilisez la commande shop", color=discord.Color.red()))
            return

        user = users[str(message.author.id)]
        objPrice = items[objet]['price']
        if objet in user['possess']:
            await ctx.send(embed=discord.Embed(title="Objet déja possédé", description=f"Vous possédez déja ``{objet}``", color=discord.Color.red()))
            return

        if user['koinz'] < objPrice:
            await ctx.send(embed=discord.Embed(title=f"L'item est trop cher", description=f"{objet.capitalize()} coute {objPrice} koinz. \nVous en possèdez {user['koinz']}, il vous en manque {objPrice-user['koinz']}", color=discord.Color.red()))
            return
        users[str(message.author.id)]['koinz'] -= objPrice
        users[str(message.author.id)]['possess'].append(items[objet]['name'].lower(
        ).replace("é", 'e').replace("è", "e").replace("ê", 'e').replace("à", "a"))
        pushUsers(users)
        objet = items[objet]
        nom = objet['name']
        description = objet['description']
        prix = objet['price']
        image = objet["image"]
        embed = discord.Embed(
            title="Item acheté : "+nom, description=description, color=discord.Color.dark_gold())
        embed.add_field(name="Prix", value=str(prix))
        if image:
            embed.set_image(url=image)
        await ctx.send(":white_check_mark: **Objet acheté avec succès**", embed=embed)
        userMoney = users[str(message.author.id)]['koinz']
        embed = discord.Embed(
            title="Transaction", description=f"**-{objPrice} koinz**\nRestant : {userMoney} koinz", color=discord.Color.dark_gold())
        embed.set_thumbnail(url=user['pfp'])
        await ctx.send(embed=embed)

    @commands.command(name='sell', description='Permet de vendre un objet', aliases=['vendre', 'sl'], usage='sell [objet]')
    async def sell(self, ctx, *objet):
        message = ctx.message
        users = getUsers()
        objet = " ".join(objet).lower().replace("é", 'e').replace(
            "è", "e").replace("ê", 'e').replace("à", "a")
        items = getRepertoire()['item']
        if not str(message.author.id) in users:
            await aventureError(ctx)
            return
        if not objet:
            await ctx.send(embed=discord.Embed(title="Précisez un objet", description="Veuillez préciser un objet à vendre", color=discord.Color.red()))
            return

        if not objet in items:
            await ctx.send(embed=discord.Embed(title="Objet non existant", description=f"``{objet}`` n'existe pas\nPour connaitre les items existants utilisez la commande shop", color=discord.Color.red()))
            return

        user = users[str(message.author.id)]
        objPrice = items[objet]['price']
        if not objet in user['possess']:
            await ctx.send(embed=discord.Embed(title="Objet non possédé", description=f"Vous ne possédez pas ``{objet}``", color=discord.Color.red()))
            return

        if objet in user['inventory']:
            del users[str(message.author.id)]['inventory'][users[str(
                message.author.id)]['inventory'].index(objet)]
        users[str(message.author.id)]['koinz'] += objPrice
        del users[str(message.author.id)]['possess'][users[str(
            message.author.id)]['possess'].index(objet)]
        pushUsers(users)
        objet = items[objet]
        nom = objet['name']
        description = objet['description']
        prix = objet['price']
        image = objet["image"]
        embed = discord.Embed(
            title="Item vendu : "+nom, description=description, color=discord.Color.dark_blue())
        embed.add_field(name="Prix", value=str(prix))
        if image:
            embed.set_image(url=image)
        await ctx.send(":white_check_mark: **Objet vendu avec succès**", embed=embed)
        userMoney = users[str(message.author.id)]['koinz']
        embed = discord.Embed(
            title="Transaction", description=f"**+{objPrice} koinz**\nCompte : {userMoney} koinz", color=discord.Color.dark_green())
        embed.set_thumbnail(url=user['pfp'])
        await ctx.send(embed=embed)

    @commands.command(name='inventory', description='Envoie l\'inventaire du joueur', aliases=['inventaire', 'ivr'], usage='inventory')
    async def inventory(self, ctx):
        message = ctx.message
        users = getUsers()
        if str(message.author.id) in users:
            userInvent = users[str(message.author.id)]['inventory']
            if userInvent:
                userInvent = ["**"+str(obj)+"**" for obj in userInvent]
                userInvent[0] = "- "+userInvent[0]
            await ctx.send(embed=discord.Embed(title=f"Inventaire de {message.author.name}", description="\n- ".join(userInvent) or "Votre inventaire est vide", color=discord.Color.dark_magenta()))
        else:
            await aventureError(ctx)

    @commands.command(name='equip', description='Permet d\'équiper un objet', aliases=['eqp', 'equipe'], usage='equip [objet]')
    async def equip(self, ctx, *objet):
        message = ctx.message
        users = getUsers()
        objet = " ".join(objet).lower().replace("é", 'e').replace(
            "è", "e").replace("ê", 'e').replace("à", "a")
        items = getRepertoire()['item']
        if not str(message.author.id) in users:
            await aventureError(ctx)
            return
        if not objet:
            await ctx.send(embed=discord.Embed(title="Précisez un objet", description="Veuillez préciser un objet de la liste d'items à équiper", color=discord.Color.red()))
            return

        if not objet in items:
            await ctx.send(embed=discord.Embed(title="Objet non existant", description=f"``{objet}`` n'existe pas\nPour connaitre les items existants utilisez la commande items", color=discord.Color.red()))
            return

        user = users[str(message.author.id)]

        if objet in user['inventory']:
            await ctx.send(embed=discord.Embed(title="Objet déja équipé", description=f"Vous avez déja ``{objet}`` sur vous", color=discord.Color.red()))
            return

        if not objet in user['possess']:
            await ctx.send(embed=discord.Embed(title="Objet non possédé", description=f"Veillez à acheter ``{objet}`` avant de l'équiper", color=discord.Color.red()))
            return

        users[str(message.author.id)]['inventory'].append(items[objet]['name'].lower(
        ).replace("é", 'e').replace("è", "e").replace("ê", 'e').replace("à", "a"))
        pushUsers(users)
        objet = items[objet]
        nom = objet['name']
        description = objet['description']
        prix = objet['price']
        image = objet["image"]
        embed = discord.Embed(
            title="Objet équipé : "+nom, description=description, color=discord.Color.dark_gold())
        embed.add_field(name="Prix", value=str(prix))
        if image:
            embed.set_image(url=image)
        await ctx.send(":white_check_mark: **Objet correctement équipé**", embed=embed)

    @commands.command(name='unequip', description='Permet de déséquiper un objet', aliases=['uneqp', 'desequipe'], usage='unequip [objet]')
    async def unequip(self, ctx, *objet):
        message = ctx.message
        users = getUsers()
        objet = " ".join(objet).lower().replace("é", 'e').replace(
            "è", "e").replace("ê", 'e').replace("à", "a")
        items = getRepertoire()['item']
        if not str(message.author.id) in users:
            await aventureError(ctx)
            return
        if not objet:
            await ctx.send(embed=discord.Embed(title="Précisez un objet", description="Veuillez préciser un objet de la liste d'items à équiper", color=discord.Color.red()))
            return
        if not objet in items:
            await ctx.send(embed=discord.Embed(title="Objet non existant", description="Vous ne pouvez déséquiper un objet inexistant\nPour plus d'informations utilisez la commande items", color=discord.Color.red()))
            return

        user = users[str(message.author.id)]

        if not objet in user['inventory']:
            await ctx.send(embed=discord.Embed(title="Objet non équipé", description=f"Vous n'avez  pas ``{objet}`` sur vous", color=discord.Color.red()))
            return

        del users[str(message.author.id)]['inventory'][users[str(
            message.author.id)]['inventory'].index(objet)]
        pushUsers(users)
        objet = items[objet]
        nom = objet['name']
        description = objet['description']
        prix = objet['price']
        image = objet["image"]
        embed = discord.Embed(
            title="Objet déséquipé : "+nom, description=description, color=discord.Color.dark_gold())
        embed.add_field(name="Prix", value=str(prix))
        if image:
            embed.set_image(url=image)
        await ctx.send(":white_check_mark: **Objet correctement déséquipé**", embed=embed)

    @commands.command(name='addMoney', description=f'Ajoute de l\'argent à un joueur', aliases=['am'], usage='addMoney [membre] [somme]')
    async def addMoney(self, ctx, destUser: discord.User, somme: int):

        message = ctx.message
        users = getUsers()
        if not ctx.message.author.guild_permissions.administrator:
            await adminError(ctx)
            return

        if not str(destUser.id) in users:
            await aventureError(ctx)
            return

        user = users[str(destUser.id)]
        user['koinz'] += somme
        pushUsers(users)
        await ctx.send(embed=discord.Embed(title=f"{self.device} ajoutés", description=f"{somme} {self.device} ajoutés à {destUser.name}", color=discord.Color.green()).add_field(name=f"Compte de {destUser.name}", value=f"{user['koinz']-somme} ➜ {user['koinz']}"))

    @commands.command(name='addTrophes', description=f'Ajoute des trophés à un joueur', aliases=['at'], usage='addTrophes [membre] [nombre]')
    async def addTrophes(self, ctx, destUser: discord.User, somme: int):

        message = ctx.message
        users = getUsers()
        if not ctx.message.author.guild_permissions.administrator:
            await adminError(ctx)
            return

        if not str(destUser.id) in users:
            await aventureError(ctx)
            return

        user = users[str(destUser.id)]
        user['trophees'] += somme
        pushUsers(users)
        await ctx.send(embed=discord.Embed(title=f"Trophés ajoutés", description=f"{somme} :trophy: ajoutés à {destUser.name}", color=discord.Color.green()).add_field(name=f"Trophés de {destUser.name}", value=f"{user['trophees']-somme} ➜ {user['trophees']}"))

    @commands.command(name='test', description='', aliases=[], usage='')
    async def test(self, ctx):
        pass


def setup(client):
    client.add_cog(Profile(client))
