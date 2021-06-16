import discord
import matplotlib
import aiohttp
import json
import os
import re

import traceback
import random
import sys
import jsonData as jbin
import requests
import datetime
import requests
import shutil
from discord import Color
from discord.ext import commands
from colorama import Fore
import colorama
colors = dict(matplotlib.colors.cnames)
colorama.init()

def getRepertoire():
    return jbin.read()['repertoire']


def pushRepertoire(data):
    datas = jbin.read()
    datas['repertoire'] = data
    jbin.update(datas)


class Repertoire(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.monster = {
                'stepCrea': (False, 0),
                'monsterMessage': "",
                'author': "",
                "monster": {

                }
            }

    @commands.command(name='bestiaire', description='Envoie le bestiaire', aliases=['btr', 'faune'], usage='bestiaire')
    async def bestiaire(self, ctx):
        bestiaire = getRepertoire()['bestiaire']
        embed = discord.Embed(
            title="Bestiaire", description="On trouve dans le bestiaire toutes les informations sur les monstres répértoriés", color=discord.Color.dark_green())
        for animal in bestiaire.values():
            stats = "\n".join(["__"+s+"__"+' : '+str(animal['stats'][s])
                               for s in animal['stats']])
            techniques = "\n".join(
                ["__"+s+"__"+' : '+animal['techniques'][s] for s in animal['techniques']])
            embed.add_field(
                name=animal['name'],
                value=animal['description']+'\n'+'**Loot :** '+" + ".join(
                    animal['loot'])+'\n**Stats :**\n'+stats+'\n**Techniques :**\n'+techniques,
                inline=True
            )
        await ctx.send(embed=embed)

    @commands.command(name='items', description='Envoie tous les items répertoriés', aliases=['itm', 'i', 'shop'], usage='items')
    async def items(self, ctx):

        items = getRepertoire()['item']
        if ctx.invoked_with == "shop":
            embed = discord.Embed(
                title="Magasin", description="Bienvenue dans le magasin, effectuez la commande buy suivie du nom de l'item à acheter pour acquérir un item !", color=discord.Color.gold())
        else:
            embed = discord.Embed(
                title="Items", description="Le catalogue des items comporte toutes les informations sur les items répertoriés", color=discord.Color.dark_green())
        for item in items.values():
            embed.add_field(
                name=item['name'],
                value=item['description']+'\n' +
                '**Prix :**\n'+str(item['price']),
                inline=True
            )
        await ctx.send(embed=embed)

    @commands.command(name='find', description='Envoie les informations sur l\'objet ou l\'animal demandé', aliases=['fnd', 'recherche', 'info'], usage='find <bestiaire/item> [nom]', details="Aliases des catégories :\n bestiaire : **b**, **btr**, **faune**, **animal** \nitem : **i**, **objet**")
    async def find(self, ctx, mod="", *request):
        request = " ".join(request)
        request = request.lower().replace("é", 'e').replace(
            "è", "e").replace("ê", 'e').replace("à", "a")
        bAliases = ["bestiaire", "b", "btr", "faune", "animal"]
        iAliases = ["item", "i", "objet"]
        bestiaire = getRepertoire()['bestiaire']
        item = getRepertoire()['item']
        if not mod:
            await ctx.send(":speech_balloon: **Veuillez préciser la catégorie de votre recherche.**\n> ``find <bestiaire/item> [nom]``")
            return

        if (not mod in bAliases+iAliases):
            await ctx.send(f":speech_balloon: **Veuillez préciser une catégorie valable.**\n> ``Bestiaire`` : {', '.join(bAliases)}\n> ``Item`` : {', '.join(iAliases)}")
            return

        if not request:
            await ctx.send(f":speech_balloon: **Veuillez préciser une recherche.**\n> ``find <bestiaire/item> [nom]``")
            return
        if (not request in bestiaire) and (not request in item):
            await ctx.send(embed=discord.Embed(title="Résultats : ", description=f"``{request}`` n'existe pas.\nEssayez les commandes ``bestiaire`` ou ``items`` pour obtenir la liste des créatures et objets existants.", color=discord.Color.red()))
            return
        if mod in bAliases:
            animal = bestiaire[request]
            nom = animal['name']
            description = animal['description']
            stats = animal['stats']
            techniques = animal['techniques']
            loot = animal['loot']
            image = animal['image']
            embed = discord.Embed(
                title=nom, description=description, color=discord.Color.dark_gold())
            embed.add_field(name="Stats", value="\n".join(
                ["__"+s+"__"+' : '+str(stats[s]) for s in stats]))
            embed.add_field(name="Techniques", value="\n".join(
                ["__"+s+"__"+' : '+techniques[s] for s in techniques]))
            embed.add_field(name="Loot", value="\n".join(loot))
            if image:
                embed.set_image(url=image)
            await ctx.send(embed=embed)
            return

        if mod in iAliases:
            objet = item[request]
            nom = objet['name']
            description = objet['description']
            prix = objet['price']
            image = objet["image"]
            embed = discord.Embed(
                title=nom, description=description, color=discord.Color.dark_gold())
            embed.add_field(name="Prix", value=str(prix))
            if image:
                embed.set_image(url=image)
            await ctx.send(embed=embed)
            return

    @commands.command(name='addItem', description='Ajoute un item à la liste', aliases=['ai', 'ajoutItem'], usage='addItem [nom] [prix] [description] (image)', details="Pour qu'un nom ou une description comporte des espaces il faut l'entourer de guilleumets (\"\")")
    async def addItem(self, ctx, name: str, price: str, description: str, image=""):

        if not ctx.message.author.guild_permissions.administrator:

            await ctx.send(embed=discord.Embed(title="Vous n'êtes pas administrateur", description="La permission administrateur est requise pour changer cette commande.", color=discord.Color.red()))
            return
        message = ctx.message
        safeName = name.lower().replace("é", 'e').replace("è", "e").replace("ê", 'e').replace("à", "a")
        newItem = {
            "name": name.replace("é", 'e').replace("è", "e").replace("ê", 'e').replace("à", "a"),
            "price": int(price),
            "description": description.replace("é", 'e').replace("è", "e").replace("ê", 'e').replace("à", "a"),
            "image": image
        }
        datas = getRepertoire()
        if safeName in [datas['item'][i]['name'] for i in datas['item']]:
            await ctx.send(embed=discord.Embed(title=f"{name} existe déja", description=f"Impossible de créer l'item ``{name}`` car il existe déja. Pour plus d'infomations, faites ``%find {name}``", color=discord.Color.red()))
            return

        datas['item'][safeName] = newItem
        pushRepertoire(datas)
        objet = newItem
        nom = objet['name']
        description = objet['description']
        prix = objet['price']
        image = objet["image"]
        embed = discord.Embed(
            title=nom, description=description, color=discord.Color.dark_gold())
        embed.add_field(name="Prix", value=str(prix))
        if image:
            embed.set_image(url=image)
        await ctx.send(":white_check_mark: **L'item a été créé avec succès !**", embed=embed)
        return

    @commands.command(name='removeItem', description='Enlève un item de la liste', aliases=['ri', 'enleveItem'], usage='removeItem [nom]')
    async def removeItem(self, ctx, *name):
        if not ctx.message.author.guild_permissions.administrator:

            await ctx.send(embed=discord.Embed(title="Vous n'êtes pas administrateur", description="La permission administrateur est requise pour changer cette commande.", color=discord.Color.red()))
            return
        message = ctx.message
        name = " ".join(name)
        safeName = name.lower().replace("é", 'e').replace(
            "è", "e").replace("ê", 'e').replace("à", "a")
        datas = getRepertoire()
        if not (safeName in [datas['item'][i]['name'] for i in datas['item']]):
            await ctx.send(embed=discord.Embed(title=f"{name} n'existe pas", description=f"Impossible de supprimer l'item ``{name}`` car il n'existe pas. Pour plus d'infomations, faites ``%items``", color=discord.Color.red()))
            return
        itemDeleted = datas['item'][name]
        del datas['item'][name]
        pushRepertoire(datas)
        objet = itemDeleted
        nom = objet['name']
        description = objet['description']
        prix = objet['price']
        image = objet["image"]
        embed = discord.Embed(
            title=nom, description=description, color=discord.Color.red())
        embed.add_field(name="Prix", value=str(prix))
        if image:
            embed.set_image(url=image)
        await ctx.send(":white_check_mark: **L'item a été supprimé avec succès !**", embed=embed)
        return

    @commands.command(name='removeMonster', description='Enlève une créature de la liste', aliases=['rmr', 'enleveMonstre'], usage='removeMonster [nom]')
    async def removeItem(self, ctx, *name):
        if not ctx.message.author.guild_permissions.administrator:

            await ctx.send(embed=discord.Embed(title="Vous n'êtes pas administrateur", description="La permission administrateur est requise pour effectuer cette commande.", color=discord.Color.red()))
            return
        message = ctx.message
        name = " ".join(name)
        safeName = name.lower().replace("é", 'e').replace(
            "è", "e").replace("ê", 'e').replace("à", "a")
        datas = getRepertoire()
        if not (safeName in [datas['bestiaire'][i]['name'] for i in datas['bestiaire']]):
            await ctx.send(embed=discord.Embed(title=f"{name} n'existe pas", description=f"Impossible de supprimer la créature ``{name}`` car elle n'existe pas. Pour plus d'infomations, faites ``%bestiaire``", color=discord.Color.red()))
            return
        monsterDeleted = datas['bestiaire'][name]
        del datas['bestiaire'][name]
        pushRepertoire(datas)
        monster = monsterDeleted
        nom = monster['name']
        description = monster['description']
        techniques = monster['techniques']
        loot = monster["loot"]
        stats = monster['stats']
        image = monster["image"]
        embed = discord.Embed(
            title=nom, description=description, color=discord.Color.dark_gold())
        embed.add_field(name="Stats", value="\n".join(
            ["__"+s+"__"+' : '+str(stats[s]) for s in stats]))
        embed.add_field(name="Techniques", value="\n".join(
            ["__"+s+"__"+' : '+techniques[s] for s in techniques]))
        embed.add_field(name="Loot", value="\n".join(loot))
        if image:
            embed.set_image(url=image)

        await ctx.send(":white_check_mark: **Monstre correctement supprimé**", embed=embed)
        return

    @commands.command(name='addMonster', description='Ajoute un monstre au bestiaire', aliases=['amr'], usage='addMonster')
    async def addMonster(self, ctx, ):
        if not ctx.message.author.guild_permissions.administrator:

            await ctx.send(embed=discord.Embed(title="Vous n'êtes pas administrateur", description="La permission administrateur est requise pour effectuer cette commande.", color=discord.Color.red()))
            return
        message = ctx.message
        listContent = message.content.split(' ')
        content = ' '.join(listContent[1:])
        args = content.strip().split(' ')
        if not self.monster['stepCrea'][0]:

            self.monster['monsterMessage'] = await ctx.send(embed=discord.Embed(title="Création d'un monstre", description="Bienvenue dans la création de monstre. Répondez aux demandes par * si  vous ne voulez rien répondre à cette demande et répondez par ! pour quitter.\n**Entrez le nom du monstre :**", color=discord.Color.gold()))
            self.monster['stepCrea'] = (True, 1)
            self.monster['author'] = ctx.message.author
            return

        else:

            await ctx.send(embed=discord.Embed(title="Création déja en cours", description="Une création de monstre est déja en cours, faites ! pour quitter cette création.", color=discord.Color.red()))
            return

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
        if msg.content.startswith("%"):
            return
        if self.monster['stepCrea'][0]:
            if msg.channel.id == self.monster['monsterMessage'].channel.id and msg.author.id == self.monster['author'].id:
                messageMonster = self.monster["monsterMessage"]
                author = self.monster['author']

                if self.monster['stepCrea'][1] == 7:
                    await msg.delete()
                    if msg.content == "!":
                        self.monster['stepCrea'] = (False, 0)
                        await messageMonster.edit(embed=discord.Embed(title="Création annulée", description="Vous avez annulé la création", color=discord.Color.orange()))
                        return

                    if msg.content == "oui":
                        datas = getRepertoire()
                        datas['bestiaire'][self.monster['monster']['name'].lower().replace("é", 'e').replace(
                            "è", "e").replace("ê", 'e').replace("à", "a")] = self.monster['monster']

                        pushRepertoire(datas)
                        animal = self.monster['monster']
                        nom = animal['name']
                        description = animal['description']
                        stats = animal['stats']
                        techniques = animal['techniques']
                        loot = animal['loot']
                        image = animal['image']
                        embed = discord.Embed(
                            title=nom, description=description, color=discord.Color.dark_gold())
                        embed.add_field(name="Stats", value="\n".join(
                            ["__"+s+"__"+' : '+str(stats[s]) for s in stats]))
                        embed.add_field(name="Techniques", value="\n".join(
                            ["__"+s+"__"+' : '+techniques[s] for s in techniques]))
                        embed.add_field(name="Loot", value="\n".join(loot))
                        if image:
                            embed.set_image(url=image)

                        await messageMonster.edit(embed=embed)
                        self.monster['stepCrea'] = (False, 0)
                        return
                    await messageMonster.edit(embed=discord.Embed(title="Erreur", description="Répondez par oui pour confirmer ou ! pour annuler", color=discord.Color.red()))
                    self.monster['stepCrea'] = (True, 7)
                elif self.monster['stepCrea'][1] == 6:
                    await msg.delete()
                    if msg.content == "!":
                        self.monster['stepCrea'] = (False, 0)
                        await messageMonster.edit(embed=discord.Embed(title="Création annulée", description="Vous avez annulé la création", color=discord.Color.orange()))
                        return

                    if msg.content == "*":
                        self.monster['monster']['image'] = ""
                        self.monster['stepCrea'] = (True, 7)
                        await messageMonster.edit(embed=discord.Embed(title="Validation", description="Entrez oui pour valider la création", color=discord.Color.gold()))
                        return

                    self.monster['monster']['image'] = msg.content
                    self.monster['stepCrea'] = (True, 7)
                    await messageMonster.edit(embed=discord.Embed(title="Validation", description="Entrez oui pour valider la création", color=discord.Color.gold()))

                elif self.monster['stepCrea'][1] == 5:
                    await msg.delete()
                    if msg.content == "!":
                        self.monster['stepCrea'] = (False, 0)
                        await messageMonster.edit(embed=discord.Embed(title="Création annulée", description="Vous avez annulé la création", color=discord.Color.orange()))
                        return

                    if msg.content == "*":
                        self.monster['monster']['loot'] = []
                        self.monster['stepCrea'] = (True, 6)
                        await messageMonster.edit(embed=discord.Embed(title="Création d'un animal", description="Entrez le lien de l'image de l'animal", color=discord.Color.gold()))
                        return
                    text = msg.content.lower().replace("é", 'e').replace(
                        "è", "e").replace("ê", 'e').replace("à", "a")
                    spt = text.split('"')
                    while '' in spt:
                        del spt[spt.index('')]
                    while ' ' in spt:
                        del spt[spt.index(' ')]
                    self.monster['monster']['loot'] = spt
                    self.monster['stepCrea'] = (True, 6)
                    await messageMonster.edit(embed=discord.Embed(title="Création d'un animal", description="Entrez le lien de l'image de l'animal", color=discord.Color.gold()))

                    self.monster['stepCrea'] = (True, 6)

                elif self.monster['stepCrea'][1] == 4:
                    await msg.delete()
                    if msg.content == "!":
                        self.monster['stepCrea'] = (False, 0)
                        await messageMonster.edit(embed=discord.Embed(title="Création annulée", description="Vous avez annulé la création", color=discord.Color.orange()))
                        return
                    if msg.content == "*":
                        await messageMonster.edit(embed=discord.Embed(title="Création d'un animal", description="Entrez le(s) loot(s) de l'animal entre guilleumets\n``Exemple :`` \"50 koinz\" \"1 super potion\"", color=discord.Color.gold()))
                        self.monster['monster']['techniques'] = {}
                        self.monster['stepCrea'] = (True, 5)
                        return
                    text = msg.content.lower().replace("é", 'e').replace(
                        "è", "e").replace("ê", 'e').replace("à", "a")
                    spt = text.split('"')
                    while '' in spt:
                        del spt[spt.index('')]
                    while ' ' in spt:
                        del spt[spt.index(' ')]
                    noms = [str(n) for n in spt[::2]]
                    descriptions = [str(n) for n in spt[1::2]]
                    self.monster['monster']['techniques'] = dict(
                        zip(noms, descriptions))

                    self.monster['stepCrea'] = (True, 5)
                    await messageMonster.edit(embed=discord.Embed(title="Création d'un animal", description="Entrez le(s) loot(s) de l'animal entre guilleumets\n``Exemple :`` \"50 koinz\" \"1 super potion\"", color=discord.Color.gold()))

                elif self.monster['stepCrea'][1] == 3:
                    await msg.delete()
                    if msg.content == "!":
                        self.monster['stepCrea'] = (False, 0)
                        await messageMonster.edit(embed=discord.Embed(title="Création annulée", description="Vous avez annulé la création", color=discord.Color.orange()))
                        return
                    if msg.content == "*":
                        await messageMonster.edit(embed=discord.Embed(title="Création d'un animal", description="Entrez les noms et descriptions des techniques entre guilleumets par pair.\n``Exemple : `` \"lame\" \"Inflige des degats tranchants\" \"Tsunami\" \"Inflige des degats de zone de type Eau\"", color=discord.Color.gold()))
                        self.monster['monster']['techniques'] = {}
                        self.monster['stepCrea'] = (True, 4)
                        return
                    text = msg.content.lower().replace("é", 'e').replace(
                        "è", "e").replace("ê", 'e').replace("à", "a")
                    spt = text.split(' ')
                    noms = [str(n) for n in spt[::2]]
                    try:
                        descriptions = [int(n) for n in spt[1::2]]
                    except ValueError:
                        await messageMonster.edit(embed=discord.Embed(title="Erreur", description="Les valeurs des paramètres doivent être des nombres\nRetapez les techniques dans leur intégralité", color=discord.Color.red()))
                        self.monster['stepCrea'] = (True, 3)
                        return

                    self.monster['monster']['stats'] = dict(
                        zip(noms, descriptions))

                    self.monster['stepCrea'] = (True, 4)
                    await messageMonster.edit(embed=discord.Embed(title="Création d'un animal", description="Entrez les noms et descriptions des techniques entre guilleumets par pair.\n``Exemple : `` \"lame\" \"Inflige des degats tranchants\" \"Tsunami\" \"Inflige des degats de zone de type Eau\"", color=discord.Color.gold()))

                elif self.monster['stepCrea'][1] == 2:
                    await msg.delete()
                    if msg.content == "!":
                        self.monster['stepCrea'] = (False, 0)
                        await messageMonster.edit(embed=discord.Embed(title="Création annulée", description="Vous avez annulé la création", color=discord.Color.orange()))
                        return

                    if msg.content == "*":
                        await messageMonster.edit(embed=discord.Embed(title="Erreur", description="La description est requise\nRetapez là", color=discord.Color.red()))
                        self.monster['stepCrea'] = (True, 2)
                        return

                    self.monster['monster']['description'] = msg.content.lower().replace(
                        "é", 'e').replace("è", "e").replace("ê", 'e').replace("à", "a")
                    self.monster['stepCrea'] = (True, 3)
                    await messageMonster.edit(embed=discord.Embed(title="Création d'un animal", description="Entrez les statistiques de l'animal sans ponctuation ni accents\n``Exemple :`` vie 50 vitese 40 spécial 20", color=discord.Color.gold()))

                elif self.monster['stepCrea'][1] == 1:
                    await msg.delete()
                    if msg.content == "!":
                        self.monster['stepCrea'] = (False, 0)
                        await messageMonster.edit(embed=discord.Embed(title="Création annulée", description="Vous avez annulé la création", color=discord.Color.orange()))
                        return
                    name = msg.content
                    if msg.content == "*":
                        await messageMonster.edit(embed=discord.Embed(title="Erreur", description="Le nom est requis\nVeuillez le retaper", color=discord.Color.red()))
                        self.monster['stepCrea'] = (True, 1)
                        return

                    self.monster['monster']['name'] = msg.content.lower().replace(
                        "é", 'e').replace("è", "e").replace("ê", 'e').replace("à", "a")
                    self.monster['stepCrea'] = (True, 2)
                    await messageMonster.edit(embed=discord.Embed(title="Création d'un animal", description="Entrez la description de l'animal", color=discord.Color.gold()))
                    
def setup(client):
    client.add_cog(Repertoire(client))