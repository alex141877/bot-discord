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
voted_users = {}  # Pour suivre les utilisateurs qui ont déjà voté

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
        
        self.add_item(Button(label="Groupes sanguins", style=discord.ButtonStyle.primary, custom_id="blood_groups"))
        self.add_item(Button(label="Constructions", style=discord.ButtonStyle.primary, custom_id="buildings"))
        self.add_item(Button(label="Autres Infos", style=discord.ButtonStyle.secondary, custom_id="other"))
        self.add_item(Button(label="Médic", style=discord.ButtonStyle.success, custom_id="medic"))
        self.add_item(Button(label="Checklist", style=discord.ButtonStyle.success, custom_id="checklist"))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id = interaction.data["custom_id"]
        if custom_id == "blood_groups":
            embed = discord.Embed(title="Groupes sanguins", description="Voici les groupes sanguins dans *DayZ*.")
            embed.set_image(url="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=1200,h=630,fit=crop,f=jpeg/YNqNaeQNEwSwGxov/donneur-receveur-YBgyQOJlnjivZzGr.png")
            await interaction.response.send_message(embed=embed)
        elif custom_id == "buildings":
            embed = discord.Embed(title="Plans de construction et raids", description="Voici les plans utiles en jeu.")
            embed.add_field(name="Construction", value="[Voir ici](https://i.redd.it/ni418ixshzu41.png)", inline=False)
            embed.add_field(name="Raids", value="[Voir ici](https://th.bing.com/th/id/R.72c751c14f5bbb5cc35d4e0ea3aa5446?rik=KfqbUkCjQeZJJQ&pid=ImgRaw&r=0)", inline=False)
            await interaction.response.send_message(embed=embed)
        elif custom_id == "other":
            embed = discord.Embed(title="Autres informations", description="Données utiles sur *DayZ*.")
            embed.set_image(url="https://steamuserimages-a.akamaihd.net/ugc/1681498780799219777/FE18654C476CB9FD970C9D75603C4D7BA721D2D1/")
            await interaction.response.send_message(embed=embed)
        elif custom_id == "medic":
            embed = discord.Embed(title="Guide médical", description="Informations sur les soins dans *DayZ*.")
            embed.add_field(name="Médicaments", value="[Voir ici](https://dayz.fandom.com/wiki/Medical_Supplies)", inline=False)
            embed.add_field(name="Traumatismes", value="[Voir ici](https://dayz.fandom.com/wiki/Injuries)", inline=False)
            await interaction.response.send_message(embed=embed)
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

bot.run(TOKEN)
