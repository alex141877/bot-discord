import os
import discord
from discord.ext import commands
from dotenv import load_dotenv  # Charge les variables d'environnement
import requests

# Charger les variables d'environnement depuis .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise ValueError("Le token Discord est introuvable ! Assurez-vous de l'ajouter aux variables d'environnement.")

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True  # Permet au bot de lire le contenu des messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionnaire pour suivre les votes des utilisateurs
votes = {}
voted_users = {}  # Pour suivre les utilisateurs qui ont déjà voté pour quelqu'un

# Dictionnaire des noms de serveurs
server_names = {
    "123.456.78.90:2302": "Serveur Alpha",
    "98.765.43.21:2500": "Serveur Bravo",
    "111.222.333.444:2400": "Serveur Charlie",
    "555.666.777.888:2600": "Serveur Delta",
    "92.38.222.126:2302": "Russian Deathmatch"
}

# Fonction pour récupérer les infos du serveur Steam
def get_steam_server_info(ip, port):
    url = f"http://api.steampowered.com/ISteamApps/GetServersAtAddress/v0001/?addr={ip}:{port}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("response"):
            # Analyser les données selon le format de réponse
            players = data["response"].get("players", 0)
            max_players = data["response"].get("maxplayers", 0)
            return players, max_players
    return None, None

# Commande pour afficher le nombre de joueurs sur plusieurs serveurs
@bot.command()
async def players(ctx, *servers):
    default_servers = list(server_names.keys())
    if not servers:
        servers = default_servers

    results = []
    for server in servers:
        try:
            ip, port = server.split(":")
            port = int(port)
            player_count, max_players = get_steam_server_info(ip, port)
            display_name = server_names.get(server, server)
            if player_count is None:
                results.append(f"❌ Impossible de récupérer les informations pour `{server}`.")
            else:
                results.append(f"🎮 **{display_name} ({server})** → {player_count}/{max_players} joueurs en ligne")
        except ValueError:
            results.append(f"❌ Format incorrect pour `{server}`. Utilisation: `ip:port`")

    await ctx.send("\n".join(results))

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

    votes[user.id] = votes.get(user.id, 0) + 1
    voted_users.setdefault(ctx.author.id, []).append(user.id)

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

    await ctx.send(f"{user.name} a {votes.get(user.id, 0)} votes.")

# Commande pour réinitialiser les votes (uniquement accessible par le fondateur)
@bot.command()
async def reset_votes(ctx):
    if ctx.author.id != ctx.guild.owner.id:
        await ctx.send("Désolé, vous devez être le fondateur du serveur pour réinitialiser les votes.")
        return

    votes.clear()
    voted_users.clear()
    await ctx.send("Les votes ont été réinitialisés. Les utilisateurs peuvent maintenant revoter.")

# Lancer le bot avec le token sécurisé
bot.run(TOKEN)
