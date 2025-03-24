import os
import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise ValueError("Le token Discord est introuvable ! Assurez-vous de l'ajouter aux variables d'environnement.")

# Crée une instance du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionnaire pour suivre les votes des utilisateurs
votes = {}
voted_users = {}  # Pour suivre les utilisateurs qui ont déjà voté pour quelqu'un

class ChecklistView(View):
    def __init__(self):
        super().__init__()
        self.items = {
            "Scie": False, "Clou": False, "Hache": False, "Pelle": False,
            "Corde": False, "Tenaille": False, "Cable": False,
            "Hachette ou Merlin+Marteau": False
        }
        
        for item in self.items.keys():
            self.add_item(Button(label=item, style=discord.ButtonStyle.secondary, custom_id=item))
        
        self.add_item(Button(label="✅ Valider", style=discord.ButtonStyle.success, custom_id="validate"))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id = interaction.data["custom_id"]
        if custom_id in self.items:
            self.items[custom_id] = not self.items[custom_id]
            await interaction.response.edit_message(content=f"{custom_id} {'ajouté' if self.items[custom_id] else 'retiré'} !", view=self)
        elif custom_id == "validate":
            checklist = "\n".join([f"✅ {item}" if checked else f"❌ {item}" for item, checked in self.items.items()])
            await interaction.response.send_message(f"État de votre checklist :\n{checklist}")
        return True

class MenuView(View):
    def __init__(self):
        super().__init__()
        
        # Ajout des boutons pour les catégories
        self.add_item(Button(label="Groupes sanguins", style=discord.ButtonStyle.primary, custom_id="blood_groups"))
        self.add_item(Button(label="Constructions", style=discord.ButtonStyle.primary, custom_id="buildings"))
        self.add_item(Button(label="Autres Infos", style=discord.ButtonStyle.secondary, custom_id="other"))
        self.add_item(Button(label="Checklist", style=discord.ButtonStyle.success, custom_id="checklist"))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id = interaction.data["custom_id"]
        if custom_id == "blood_groups":
            await interaction.response.send_message("Voici les groupes sanguins dans *DayZ* :\nhttps://example.com/blood_groups.png")
        elif custom_id == "buildings":
            await interaction.response.send_message("Voici les plans de construction :\nhttps://example.com/buildings.png")
        elif custom_id == "other":
            await interaction.response.send_message("Autres informations sur *DayZ* :\nhttps://example.com/other_info.png")
        elif custom_id == "checklist":
            view = ChecklistView()
            await interaction.response.send_message("Cliquez sur les outils pour les ajouter ou les retirer de votre liste :", view=view)
        return True

@bot.event
async def on_ready():
    print(f'{bot.user} est prêt et connecté à Discord !')

@bot.command()
async def menu(ctx):
    view = MenuView()
    await ctx.send("Choisissez une catégorie :", view=view)

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

# Connecte-toi à Discord avec le token sécurisé
bot.run(TOKEN)
