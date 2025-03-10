import discord
from discord.ext import commands
from datetime import datetime, timedelta

# Crée une instance du bot
intents = discord.Intents.default()
intents.message_content = True  # Permet au bot de lire le contenu des messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionnaire pour suivre les votes des utilisateurs
votes = {}
voted_users = {}  # Pour suivre les utilisateurs qui ont déjà voté pour quelqu'un

# Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f'{bot.user} est prêt et connecté à Discord !')

# Commande pour ajouter un vote à un utilisateur
@bot.command()
async def add_vote(ctx, user: discord.User):
    if ctx.author.id in voted_users and user.id in voted_users[ctx.author.id]:
        await ctx.send(f"{ctx.author.name}, vous avez déjà voté pour {user.name}. Vous ne pouvez pas revoter.")
        return

    if user.id in votes:
        votes[user.id] += 1
    else:
        votes[user.id] = 1

    # Ajoute l'utilisateur aux utilisateurs qui ont voté pour quelqu'un
    if ctx.author.id not in voted_users:
        voted_users[ctx.author.id] = []

    voted_users[ctx.author.id].append(user.id)

    # Si l'utilisateur a 6 votes ou plus, il sera banni pour 24h
    if votes[user.id] >= 6:
        await ctx.guild.ban(user, reason=f"Bannissement temporaire pour {votes[user.id]} votes", delete_message_days=1)
        await ctx.send(f"{user.name} a été banni pendant 24h pour avoir {votes[user.id]} votes.")
    else:
        await ctx.send(f"{user.name} a maintenant {votes[user.id]} votes.")

    # Notifie la personne qui a voté et lui montre le nombre de votes
    await ctx.send(f"{ctx.author.name} a voté pour {user.name}. {user.name} a maintenant {votes[user.id]} votes.")

# Commande pour voir le nombre de votes d'un utilisateur
@bot.command()
async def check_votes(ctx, user: discord.User = None):
    if user is None:
        await ctx.send("Veuillez mentionner un utilisateur pour vérifier ses votes.")
        return

    if user.id in votes:
        await ctx.send(f"{user.name} a {votes[user.id]} votes.")
    else:
        await ctx.send(f"{user.name} n'a pas encore reçu de votes.")

# Commande pour réinitialiser les votes (uniquement accessible par le fondateur)
@bot.command()
async def reset_votes(ctx):
    # Vérifie si l'utilisateur est le fondateur du serveur (propriétaire du serveur)
    if ctx.author.id != ctx.guild.owner.id:
        await ctx.send("Désolé, vous devez être le fondateur du serveur pour réinitialiser les votes.")
        return

    # Réinitialise les votes et les utilisateurs qui ont voté
    votes.clear()
    voted_users.clear()

    await ctx.send("Les votes ont été réinitialisés. Les utilisateurs peuvent maintenant revoter.")

# Connecte-toi à Discord avec ton token
bot.run('MTMyODE1ODA5NzMwNjU1MDM3Mg.GvNZWx.N79p-9qWD9FIxZaavfhfMgfONunVUaVEIf1S9g')  # Remplace par ton vrai token !
