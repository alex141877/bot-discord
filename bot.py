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
        if interaction.data["custom_id"] in self.items:
            self.items[interaction.data["custom_id"]] = not self.items[interaction.data["custom_id"]]
            await interaction.response.edit_message(content=f"{interaction.data["custom_id"]} {'ajouté' if self.items[interaction.data["custom_id"]] else 'retiré'} !", view=self)
        elif interaction.data["custom_id"] == "validate":
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
        if interaction.data["custom_id"] == "blood_groups":
            await interaction.response.send_message("Voici les groupes sanguins dans *DayZ* :\nhttps://example.com/blood_groups.png")
        elif interaction.data["custom_id"] == "buildings":
            await interaction.response.send_message("Voici les plans de construction :\nhttps://example.com/buildings.png")
        elif interaction.data["custom_id"] == "other":
            await interaction.response.send_message("Autres informations sur *DayZ* :\nhttps://example.com/other_info.png")
        elif interaction.data["custom_id"] == "checklist":
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

# Connecte-toi à Discord avec le token sécurisé
bot.run(TOKEN)
