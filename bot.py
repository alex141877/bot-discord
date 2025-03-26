import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Charger les variables d'environnement depuis .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise ValueError("Le token Discord est introuvable ! Assurez-vous de l'ajouter aux variables d'environnement.")

# Activer les intents nécessaires
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Assurez-vous que cette ligne est présente
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionnaire pour suivre le temps passé en vocal
voice_times = {}
user_join_times = {}

@bot.event
async def on_ready():
    print(f'{bot.user} est prêt et connecté à Discord !')

@bot.event
async def on_voice_state_update(member, before, after):
    """ Suivi du temps vocal """
    if before.channel is None and after.channel is not None:
        # L'utilisateur rejoint un salon vocal
        user_join_times[member.id] = datetime.now()
        print(f"{member.name} est entré en vocal à {user_join_times[member.id]}")
    
    elif before.channel is not None and after.channel is None:
        # L'utilisateur quitte un salon vocal
        if member.id in user_join_times:
            join_time = user_join_times.pop(member.id)
            duration = datetime.now() - join_time
            voice_times[member.id] = voice_times.get(member.id, timedelta()) + duration
            print(f"{member.name} a quitté le vocal après {duration}")

@bot.command()
async def check_time(ctx, user: discord.User = None):
    """ Vérifie le temps passé en vocal """
    if user is None:
        user = ctx.author
    total_time = voice_times.get(user.id, timedelta())
    
    hours, remainder = divmod(total_time.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    
    await ctx.send(f"{user.name} a passé {int(hours)}h {int(minutes)}m en vocal.")
    print(f"Vérification du temps vocal pour {user.name}: {int(hours)}h {int(minutes)}m")

@bot.command()
async def reset_time(ctx):
    """ Réinitialise le temps de vocal pour tous les utilisateurs """
    if ctx.author.guild_permissions.administrator:
        voice_times.clear()
        await ctx.send("Le temps de vocal a été réinitialisé.")
    else:
        await ctx.send("Vous devez être administrateur pour utiliser cette commande.")

bot.run(TOKEN)
