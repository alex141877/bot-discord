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

class MenuView(View):
    def __init__(self):
        super().__init__()
        
        # Bouton Groupes sanguins
        self.add_item(Button(label="Groupes sanguins", style=discord.ButtonStyle.primary, custom_id="blood_groups"))
        # Bouton Constructions
        self.add_item(Button(label="Constructions", style=discord.ButtonStyle.primary, custom_id="buildings"))
        # Bouton Autres Infos
        self.add_item(Button(label="Autres Infos", style=discord.ButtonStyle.secondary, custom_id="other"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "blood_groups":
            await interaction.response.send_message("Voici les groupes sanguins dans *DayZ* :https://serveur-dayz.fr/wp-content/uploads/2022/11/donneur-receveur.jpeg")
        elif interaction.data["custom_id"] == "buildings":
            await interaction.response.send_message("Voici les plans de construction :\nhttps://example.com/buildings.png")
        elif interaction.data["custom_id"] == "other":
            await interaction.response.send_message("Autres informations sur *DayZ* :\nhttps://example.com/other_info.png")
        return True

@bot.event
async def on_ready():
    print(f'{bot.user} est prêt et connecté à Discord !')

@bot.command()
async def menu(ctx):
    view = MenuView()
    await ctx.send("Choisissez une catégorie :", view=view)

# Connecte-toi à Discord avec le token sécurisé
bot.run(TOKEN)
