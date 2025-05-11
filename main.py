#{DEBUT : Importation des modules 
from itertools import cycle
from discord.ui import View, Button, Modal, TextInput, Select
from discord.ext import commands, tasks
from motors import config, memory
from io import BytesIO
from groq import Groq
import discord, json, os, asyncio, time, random, sys

#FIN}

#{DEBUT : Creation de la fonction du cycle satus
status = cycle(config.cycle) 
@tasks.loop(seconds=5)
async def status_swap(): 
    await bot.change_presence(activity=discord.CustomActivity(next(status)))
#FIN}

#{DEBUT : Configuration des clients
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Active l'intention pour les membres
bot = commands.Bot(command_prefix=config.prefix, intents=intents)
client = Groq(api_key=config.api_key) # Client pour l'API Groq
#FIN}

#{DEBUT : Creation de la fonction de verification des fichiers de niveaux
data_folder = "datacenter" #Définir le chemin du dossier et du fichier
levels_file = os.path.join(data_folder, "levels.json")
# Vérifier si le dossier existe, sinon le créer
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Vérifier si le fichier levels.json existe, sinon le créer
if not os.path.exists(levels_file):
    with open(levels_file, "w") as f:
        json.dump({}, f)
#FIN}

#{DEBUT : Creation de la fonction de verification des fichiers Json des fils
thread_counters_file = os.path.join(data_folder, "thread_counters.json") # Définir le chemin du fichier de compteurs de fils

# Vérifier si le fichier thread_counters.json existe, sinon le créer
if not os.path.exists(thread_counters_file):
    with open(thread_counters_file, "w") as f:
        json.dump({}, f)
#FIN}

#{DEBUT : Creation de la fonction de verification des fichiers Json de sanction
sanctions_file = os.path.join(data_folder, "sanctions.json") # Définir le chemin du fichier de suivi des sanctions

# Vérifier si le fichier sanctions.json existe, sinon le créer
if not os.path.exists(sanctions_file):
    with open(sanctions_file, "w") as f:
        json.dump({}, f)
#FIN}

#{DEBUT : Creation de la fonction de verification des fichiers Json pour le voc
# Définir le chemin du fichier de suivi des vocaux
voice_activity_file = os.path.join(data_folder, "voice_activity.json")

# Vérifier si le fichier voice_activity.json existe, sinon le créer
if not os.path.exists(voice_activity_file):
    with open(voice_activity_file, "w") as f:
        json.dump({}, f)
#FIN}

#{DEBUT : Creation de la fonction de verification des fichiers Json pour les cmd no code !
custom_commands_file = os.path.join(data_folder, "custom_commands.json") # Définir le chemin du fichier de commandes personnalisées

# Vérifier si le fichier custom_commands.json existe, sinon le créer
if not os.path.exists(custom_commands_file):
    with open(custom_commands_file, "w") as f:
        json.dump({}, f)
#FIN}

#{DEBUT : Creation de la fonction de verification des fichiers Json pour les confessions
confession_counter_file = os.path.join(data_folder, "confession_counter.json") # Définir le chemin du fichier de compteur de confessions

# Vérifier si le fichier confession_counter.json existe, sinon le créer
if not os.path.exists(confession_counter_file):
    with open(confession_counter_file, "w") as f:
        json.dump({"last_confession_number": 0}, f)
#FIN}

#{DEBUT : Creation de la fonct de verification des fichiers d'anniversaire
birthdays_file = os.path.join(data_folder, "birthdays.json") # Définir le chemin du fichier pour stocker les anniversaires

# Vérifier si le fichier birthdays.json existe, sinon le créer
if not os.path.exists(birthdays_file):
    with open(birthdays_file, "w") as f:
        json.dump({}, f)
#FIN}

#{DEBUT : Ajoutez une tâche asynchrone pour envoyer des rappels dans le salon de bump à intervalles réguliers
class BumpReminderView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Bumper le serveur", style=discord.ButtonStyle.grey, emoji="<a:sadgers:1243293297363910827>")
    async def bump_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Merci de vouloir bumper le serveur ! Utilisez la commande `/bump` dans ce salon [Clique Ici!](https://ptb.discord.com/channels/1166812114648838184/1167201714957467760).",
            ephemeral=True
        )

@tasks.loop(seconds=config.bump_reminder_interval)
async def bump_reminder():
    """
    Envoie un rappel pour bump le serveur à intervalles réguliers.
    """
    main_channel = bot.get_channel(config.main_channel_id)
    if main_channel:
        # Créer un embed pour le rappel
        embed = discord.Embed(
            title="<:chibiusawelcome:1310852415150620703> Rappel de Bump",
            description="```Aidez le serveur à grandir en utilisant la commande `/bump` !\n"
                        "Cliquez sur le bouton ci-dessous pour plus de détails.```",
            color=discord.Color.from_rgb(255, 255, 255)  # Couleur blanche
        )
        embed.set_footer(text="Merci pour votre soutien ❤️")
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
        embed.set_image(url="https://media.discordapp.net/attachments/1328845912646356994/1360262128543596845/WhiteLine.png")  # Remplacez par l'URL de votre image

        # Créer une vue avec le bouton
        view = BumpReminderView()

        # Envoyer le message avec l'embed et le bouton
        reminder_message = await main_channel.send(embed=embed, view=view)

        # Supprimer le message après x minutes
        await asyncio.sleep(config.dell_last_bump)  
        await reminder_message.delete()
#FIN}

''''
#{DEBUT : Implémenter la vérification des streams (âche asynchrone)
async def get_twitch_access_token(): # Fonction pour obtenir un token d'accès Twitch
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": config.twitch_client_id,
        "client_secret": config.twitch_client_secret,
        "grant_type": "client_credentials"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            data = await response.json()
            return data["access_token"]

# Fonction pour vérifier si une chaîne Twitch est en direct
async def is_twitch_channel_live(access_token, channel_name):
    url = f"https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": config.twitch_client_id,
        "Authorization": f"Bearer {access_token}"
    }
    params = {"user_login": channel_name}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            return data["data"]  # Retourne les données si la chaîne est en direct

# Tâche pour vérifier régulièrement l'état des chaînes Twitch
@tasks.loop(minutes=1)  # Vérifie toutes les 1 minutes
async def check_twitch_streams():
    try:
        access_token = await get_twitch_access_token()
        announcement_channel = bot.get_channel(config.stream_announcement_channel_id)

        for channel_name in config.twitch_channels:
            stream_data = await is_twitch_channel_live(access_token, channel_name)
            if stream_data:
                # La chaîne est en direct
                stream_info = stream_data[0]
                stream_title = stream_info["title"]
                stream_url = f"https://www.twitch.tv/{channel_name}"

                # Envoyer une notification dans le salon Discord
                if announcement_channel:
                    await announcement_channel.send(
                        f"🎮 **{channel_name}** est maintenant en direct sur Twitch !\n"
                        f"**Titre du stream :** {stream_title}\n"
                        f"🔗 Regardez le stream ici : {stream_url}"
                    )
    except Exception as e:
        print(f"Erreur lors de la vérification des streams Twitch : {e}")
#FIN}'''


#{DEBUT : Event de demarrage de l'application
print("Démarrage de la connexion avec le client discord")
@bot.event
async def on_ready(): #fonction de lancement.
    print(f'\033[92m{bot.user.name} est en ligne ✔ \033[0m')
    status_swap.start() #lancement des status.
    bump_reminder.start()  # Lancement des rappels de bump
    #check_twitch_streams.start()  # Lancement de la vérification des streams Twitch
    try:
        synced = await bot.tree.sync()
        print(f"\033[92mCommandes synchronisées : {len(synced)} commandes ✔\033[0m")
    except Exception as e:
        print(f"\033[91mErreur lors de la synchronisation des commandes slash et préfixes : {e}\033[0m")
#FIN}

#{DEBUT : Event de detection des messages
async def log_moderation_action(guild, message, reason):
    """
    :param guild: Le serveur (guild) où l'action a eu lieu.
    :param message: Le message qui a été modéré.
    :param reason: La raison de la modération.
    """
    log_channel_id = config.log_channel  # ID du salon de journalisation (à définir dans config.py)
    log_channel = guild.get_channel(log_channel_id)

    if log_channel:
        embed = discord.Embed(
            title="Action de modération automatique",
            description=f"Un message a été supprimé pour la raison suivante : {reason}",
            color=discord.Color.red(),
            timestamp=message.created_at
        )
        embed.add_field(name="Auteur", value=f"{message.author.mention} ({message.author.id})", inline=False)
        embed.add_field(name="Message", value=message.content, inline=False)
        embed.add_field(name="Salon", value=message.channel.mention, inline=False)
        embed.set_footer(text=f"ID du message : {message.id}")
        await log_channel.send(embed=embed)

#{DEBUT : Event de detection des messages
#--------------------------------------
# EVENEMENT IA DE L'APPLICATION
conversation_manager = memory.memory(max_history=config.max_history) # management de l'historie des conversations.
memory_instance = memory.memory() # instance de la classe memory
memory_instance.clear_inactive_conversations(config.del_history) # nettoyer les conversations inactives après 1 heure (par défaut).
def split_message(message, max_length=2000): #fonction pour la gestion du nombre de caractère max des reponses.
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]
#FIN}

# Fonctionnalité de confession
class ConfessionModal(discord.ui.Modal, title="Confession"):
    def __init__(self, confession_number: int, previous_message=None):
        super().__init__()
        self.confession_number = confession_number
        self.previous_message = previous_message  # Message précédent contenant l'embed

        # Champ pour saisir la confession
        self.confession_input = discord.ui.TextInput(
            label="Votre confession",
            style=discord.TextStyle.long,
            placeholder="Écrivez votre confession ici...",
            required=True
        )
        # Ajout du champ de texte à la vue
        self.add_item(self.confession_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Crée une vue avec le bouton de confession
            view = ConfessionButtonView(previous_message=None)  # Pas de message précédent pour la première confession

            # Différer la réponse pour éviter le délai de 3 secondes
            await interaction.response.defer(ephemeral=True)

            # Récupérer le texte de la confession
            confession_text = self.confession_input.value

            # Créer un embed pour la confession
            embed = discord.Embed(
                title=f"Confession #{self.confession_number}",
                description=f"```{confession_text}```",
                color=discord.Color.from_rgb(255, 255, 255)  # Couleur blanche
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1328845912646356994/1360262128543596845/WhiteLine.png")  # Remplacez par l'URL de votre image

            # Récupérer le salon de confession depuis le fichier de configuration
            confession_channel_id = config.confession_channel
            confession_channel = interaction.guild.get_channel(confession_channel_id)

            # Vérifiez si le salon est valide
            if not confession_channel:
                raise ValueError("Le salon de confession configuré est introuvable ou invalide.")

            # Créer une vue avec le bouton "Se confesser"
            view = ConfessionButtonView()

            # Supprimer le bouton de l'embed précédent (si applicable)
            if self.previous_message:
                try:
                    await self.previous_message.edit(view=None)  # Supprime la vue du message précédent
                except discord.NotFound:
                    print("Le message précédent est introuvable ou a été supprimé.")
                except discord.HTTPException as e:
                    print(f"Erreur HTTP lors de la modification du message précédent : {e}")

            # Envoyer l'embed dans le salon de confession avec le bouton
            new_message = await confession_channel.send(embed=embed, view=view)

             # Créer un fil pour la confession
            thread = await confession_channel.create_thread(
                name=f"Confession #{self.confession_number}",
                message=new_message,
                auto_archive_duration=1440  # Durée d'archivage automatique en minutes (1 jour)
            )

            # Envoyer un message dans le fil pour accueillir les participants
            await thread.send(f"Bienvenue dans le fil de discussion pour la **Confession #{self.confession_number}**.")

            # Passez le message à la vue pour qu'il puisse être modifié plus tard
            view.previous_message = new_message

            # Répondre à l'utilisateur pour confirmer la soumission
            await interaction.followup.send(
                "✅ Votre confession a été soumise anonymement.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Une erreur s'est produite : {e}",
                ephemeral=True
            )

class ConfessionButtonView(discord.ui.View):
    def __init__(self, previous_message=None):
        super().__init__(timeout=None)
        self.previous_message = previous_message

    @discord.ui.button(label="Se confesser", style=discord.ButtonStyle.gray, emoji="<:Crayon:1360619525380374719>")
    async def confess_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Charger le numéro de la dernière confession
        with open(confession_counter_file, "r") as f:
            counter_data = json.load(f)

        # Incrémenter le numéro de confession
        confession_number = counter_data["last_confession_number"] + 1
        counter_data["last_confession_number"] = confession_number

        # Sauvegarder le nouveau numéro de confession
        with open(confession_counter_file, "w") as f:
            json.dump(counter_data, f, indent=4)

        # Ouvrir le modal pour saisir la confession
        modal = ConfessionModal(confession_number, previous_message=self.previous_message)
        await interaction.response.send_modal(modal)
        
@bot.event
async def on_message(message):
    """
    Fonction pour gérer les messages envoyés dans les salons.
    """
    # Ignore les messages envoyés par le bot lui-même ou par d'autres bots
    if message.author.bot:
        return
    
    #{ IA ==========================================================================================
    try:
        keyWord = config.keyWord # Liste des mots-clés pour déclencher la réponse du bot.
        if isinstance(message.channel, discord.DMChannel):#(2)
            userId = message.author.id
            UserMsg = message.content
            #prompt = conversation_manager.manage_chatting(userId, UserMsg)
            prompt = conversation_manager.manage_chatting(userId, UserMsg)

            try: 
                response_parts = split_message(prompt) #séparation de la réponse en parties pour éviter les dépassements de caractères.
                for part in response_parts: #envoi de chaque partie de la réponse.
                    await message.reply(part)
                    return

            except Exception as e: #gestion des erreurs
                return f"Une erreur s'est produite: {e}"
            
        if bot.user.mention in message.content or any(keyword in message.content for keyword in keyWord) or message.reference and message.reference.resolved and message.reference.resolved.author == bot.user:
            userId = message.author.id
            UserMsg = message.content
            prompt = conversation_manager.manage_chatting(userId, UserMsg)

            try:
                response_parts = split_message(prompt) #séparation de la réponse en parties pour éviter les dépassements de caractères.
                for part in response_parts: #envoi de chaque partie de la réponse.
                    await message.reply(part)

            except Exception as e: #gestion des erreurs.
                return await f"Une erreur c'est produite: {e}"

    except Exception as e:
        pass
    #===============================================================================================}

    # Fonctionnalité 1 : Réponse automatique à une commande personnalisée
    # Charger les commandes personnalisées
    with open(custom_commands_file, "r") as f:
        custom_commands = json.load(f)

    # Vérifie si le message correspond à une commande personnalisée
    if message.content in custom_commands:
        await message.channel.send(custom_commands[message.content])
        return

    # Fonctionnalité 2 : Système de modération (suppression de mots interdits)
    banned_words = config.banned_words  # Liste des mots interdits
    if any(banned_word in message.content.lower() for banned_word in banned_words):
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, votre message a été supprimé car il contient des mots interdits.",
                delete_after=5  # Supprime le message d'avertissement après 5 secondes
            )
            # Journalisation de l'action
            await log_moderation_action(message.guild, message, "Contenu interdit")
        except discord.Forbidden:
            print(f"Impossible de supprimer le message de {message.author} dans {message.channel}.")
        except discord.HTTPException as e:
            print(f"Erreur HTTP lors de la suppression du message : {e}")

    # Fonctionnalité 3 : Réaction automatique à un message spécifique
    autoreaction_words = config.autoreaction_words  # Liste des mots déclencheurs de réaction
    if any(word in message.content.lower() for word in autoreaction_words):
        await message.add_reaction("👋")
     
    # Fonctionnalité 4 : Détection de bump de Disboard
    """
    Détecte les messages de Disboard pour attribuer des XP après un bump réussi.
    """
    # Ignore les messages envoyés par le bot lui-même
    if message.author.bot:
        # Vérifie si le message provient de Disboard
        if message.author.name in config.bump_bots and any(bump_message in message.content for bump_message in config.bump_messages):
            # Extraire l'utilisateur qui a bumpé
            bump_user = message.mentions[0] if message.mentions else None

            if bump_user:
                # Charger les données de niveaux
                with open(levels_file, "r") as f:
                    levels = json.load(f)

                user_id = str(bump_user.id)
                if user_id not in levels:
                    levels[user_id] = {"xp": 0, "level": 1}

                # Ajouter 30 XP à l'utilisateur
                levels[user_id]["xp"] += 30

                # Sauvegarder les données de niveaux
                with open(levels_file, "w") as f:
                    json.dump(levels, f, indent=4)

                # Envoyer un message dans le salon principal
                main_channel = bot.get_channel(config.main_channel_id)
                if main_channel:
                    await main_channel.send(
                        f"<:froggyheart:1283815216844505091> Merci {bump_user.mention} d'avoir bumpé le serveur ! Vous avez gagné **30 XP** !"
                    )

    # Fonctionnalité 5 : Vérifie si le message est "$$.confess" dans le salon de confession
    if message.content.strip() == "$$.confess":
        # Vérifie si l'utilisateur a la permission de gérer les messages (par exemple, administrateur)
        if not message.author.guild_permissions.manage_messages:
            await message.channel.send(
                embed=discord.Embed(
                    title="❌ Permission refusée",
                    description="Vous n'avez pas la permission de configurer les confessions.",
                    color=discord.Color.red()
                )
            )
            return
        
        # Récupérer le salon de confession depuis le fichier de configuration
        confession_channel_id = config.confession_channel
        confession_channel = message.guild.get_channel(confession_channel_id)
        # Vérifiez si le salon est valide
        if not confession_channel:
            await message.channel.send(
                embed=discord.Embed(
                    title="❌ Erreur",
                    description="Le salon de confession configuré est introuvable. Veuillez vérifier l'ID dans le fichier de configuration.",
                    color=discord.Color.red()
                )
            )
            return
        
        # Crée une vue avec le bouton de confession
        view = ConfessionButtonView()

        # Crée un embed pour le message de configuration
        embed = discord.Embed(
            title="<:super:1243293274622525510> Confessions anonymes",
            description="```Cliquez sur le bouton ci-dessous pour faire une confession anonyme.```",
            color=discord.Color.from_rgb(255, 255, 255)  # Couleur blanche
        )
        embed.set_footer(text="Les confessions sont anonymes et confidentielles.")
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
        embed.set_image(url="https://media.discordapp.net/attachments/1328845912646356994/1360262128543596845/WhiteLine.png?ex=67fa7a53&is=67f928d3&hm=ef4a72dd72a96b476c388f481ff117933cbdeedcd2bf5025cd45e6d05cb6744d&=&width=1638&height=21")  # Remplacez par l'URL de votre image

        # Envoie le message avec l'embed et le bouton
        embed_message = await message.channel.send(embed=embed, view=view)

        # Passez le message à la vue pour qu'il puisse être modifié plus tard
        view.previous_message = embed_message

        # Supprime le message de commande pour garder le salon propre
        await message.delete()
    
    # Fonctionnalité 5 : Création automatique de fils de discussion
    # Liste des salons où les fils doivent être créés automatiquement
    thread_channels = config.thread_channels  # Liste des IDs des salons (à définir dans votre fichier de configuration)

    # Vérifie si le message est envoyé dans un salon spécifique
    if message.channel.id in thread_channels:
        # Charger les compteurs de fils
        with open(thread_counters_file, "r") as f:
            thread_counters = json.load(f)

        # Obtenir le compteur pour le salon actuel
        channel_id_str = str(message.channel.id)
        if channel_id_str not in thread_counters:
            thread_counters[channel_id_str] = 1  # Initialiser le compteur pour ce salon

        # Crée un fil pour le message avec un numéro
        thread_number = thread_counters[channel_id_str]

        # Déterminer le titre du fil
        if message.content.strip():  # Si le message contient du texte
            thread_name = message.content.split("\n")[0][:50]  # Prend la première ligne (max 50 caractères)
        else:
            thread_name = f"fil #{thread_number}"  # Titre par défaut si le message est vide

        # Créer le fil
        thread = await message.channel.create_thread(
        name=thread_name,
        message=message,
        auto_archive_duration=1440  # Durée d'archivage automatique en minutes (1 jour)
        )
        await thread.send(f"Bienvenue dans le fil de discussion #{thread_number} pour le message de {message.author.mention} !")

        # Incrémenter le compteur et sauvegarder
        thread_counters[channel_id_str] += 1
        with open(thread_counters_file, "w") as f:
            json.dump(thread_counters, f, indent=4)
       
    # Fonctionnalité 6 :Système de niveaux
    # Charger les données de niveaux
    with open(levels_file, "r") as f:
        levels = json.load(f)

    user_id = str(message.author.id)  # ID de l'utilisateur sous forme de chaîne
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}

    # Empêcher les membres "En Prison" de gagner de l'XP
    prison_role = discord.utils.get(message.guild.roles, name="En Prison")
    if prison_role and prison_role in getattr(message.author, "roles", []):
        # On ne donne pas d'XP, ni de level up, ni de rôle de niveau
        # Mais on continue à traiter les commandes si besoin
        if message.content.startswith(config.prefix):
            await bot.process_commands(message)
        return

    # Ajouter de l'XP pour chaque message
    levels[user_id]["xp"] += 10  # Vous pouvez ajuster la valeur d'XP par message
    current_xp = levels[user_id]["xp"]
    current_level = levels[user_id]["level"]

    # Calculer le seuil pour monter de niveau
    next_level_xp = current_level * 100  # Exemple : 100 XP pour le niveau 1, 200 pour le niveau 2, etc.
    new_level = None  # Initialise la variable new_level
    if current_xp >= next_level_xp:
        levels[user_id]["level"] += 1
        levels[user_id]["xp"] = 0  # Réinitialiser l'XP après la montée de niveau
        new_level = levels[user_id]["level"]
        await message.channel.send(f"🎉 {message.author.mention} a atteint le niveau {new_level} !")
    
    # Liste des niveaux et des rôles correspondants
    level_roles = config.level_roles  # Dictionnaire des rôles par niveau
    level_up_messages = config.level_up_messages  # Liste des messages de montée de niveau
    # Vérifie si le membre a atteint un niveau avec un rôle
    if new_level in level_roles:
        role_name = level_roles[new_level]
        guild = message.guild  # Récupère le serveur (guild)
        role = discord.utils.get(guild.roles, name=role_name)  # Récupère le rôle par son nom

        if role:
            # Supprime les anciens rôles de niveau
            for level, old_role_name in level_roles.items():
                if level < new_level:  # Supprime uniquement les rôles des niveaux inférieurs
                    old_role = discord.utils.get(guild.roles, name=old_role_name)
                    if old_role in message.author.roles:
                        await message.author.remove_roles(old_role)
            # Ajoute le nouveau rôle
            await message.author.add_roles(role)

        # Envoie le message de montée en niveau dans un salon spécifique
        level_up_channel_id = config.level_up_channel  # ID du salon de montée en niveau
        level_up_channel = guild.get_channel(level_up_channel_id)

        if level_up_channel:
            random_message = random.choice(level_up_messages).format(user=message.author.mention, level=new_level)
            await level_up_channel.send(random_message)
        else:
            print(f"[ALERTE] Le salon de montée en niveau (ID: {level_up_channel_id}) n'existe pas dans le serveur {guild.name}.")

    # Sauvegarder les données de niveaux
    with open(levels_file, "w") as f:
        json.dump(levels, f, indent=4)

    # Vérifie si le message commence par le préfixe avant de traiter les commandes
    if message.content.startswith(config.prefix):
        await bot.process_commands(message)
#FIN} 
 
 #{DEBUT : Event pour les salon vocaux !
@bot.event
async def on_voice_state_update(member, before, after):
    """
    Suivi du temps passé en vocal, du nombre de fois où un membre est allé en vocal,
    et attribution d'XP en fonction du temps passé.
    """

   # Ignorer les bots
    if member.bot:
        return
    
    # Charger les données de suivi des vocaux
    with open(voice_activity_file, "r") as f:
        voice_activity = json.load(f)

    # Charger les données de niveaux
    with open(levels_file, "r") as f:
        levels = json.load(f)

    user_id = str(member.id)  # ID de l'utilisateur sous forme de chaîne

    # Initialiser les données pour l'utilisateur s'il n'existe pas encore
    if user_id not in voice_activity:
        voice_activity[user_id] = {
            "total_time": 0,  # Temps total passé en vocal (en secondes)
            "join_count": 0,  # Nombre de fois où l'utilisateur est allé en vocal
            "last_join": None  # Dernière heure de connexion
        }

    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}

    # Empêcher les membres "En Prison" de gagner de l'XP vocal
    prison_role = discord.utils.get(member.guild.roles, name="En Prison")
    if prison_role and prison_role in getattr(member, "roles", []):
        # On ne donne pas d'XP vocal, mais on continue à enregistrer les entrées/sorties si besoin
        # On sauvegarde quand même le temps total et le compteur de join, mais pas d'XP
        if after.channel and (not before.channel or before.channel.id != after.channel.id):
            voice_activity[user_id]["join_count"] += 1
            voice_activity[user_id]["last_join"] = int(time.time())
        if before.channel and (not after.channel or before.channel.id != after.channel.id):
            last_join = voice_activity[user_id]["last_join"]
            if last_join:
                time_spent = int(time.time()) - last_join
                voice_activity[user_id]["total_time"] += time_spent
                voice_activity[user_id]["last_join"] = None
        # Sauvegarder les données de suivi des vocaux
        with open(voice_activity_file, "w") as f:
            json.dump(voice_activity, f, indent=4)
        # Sauvegarder les données de niveaux (inchangées)
        with open(levels_file, "w") as f:
            json.dump(levels, f, indent=4)
        return

    # Si l'utilisateur rejoint un salon vocal
    if after.channel and (not before.channel or before.channel.id != after.channel.id):
        voice_activity[user_id]["join_count"] += 1  # Incrémenter le compteur de connexions
        voice_activity[user_id]["last_join"] = int(time.time())  # Enregistrer l'heure de connexion

    # Si l'utilisateur quitte un salon vocal
    if before.channel and (not after.channel or before.channel.id != after.channel.id):
        last_join = voice_activity[user_id]["last_join"]
        if last_join:
            time_spent = int(time.time()) - last_join  # Calculer le temps passé
            voice_activity[user_id]["total_time"] += time_spent  # Ajouter au temps total
            voice_activity[user_id]["last_join"] = None  # Réinitialiser l'heure de connexion

            # Ajouter des XP en fonction du temps passé (20 XP par minute)
            xp_earned = (time_spent // 60) * 20  # 20 XP par minute
            levels[user_id]["xp"] += xp_earned

            # Vérifier si l'utilisateur monte de niveau
            current_xp = levels[user_id]["xp"]
            current_level = levels[user_id]["level"]
            next_level_xp = current_level * 100  # Exemple : 100 XP pour le niveau 1, 200 pour le niveau 2, etc.
            new_level = None

            if current_xp >= next_level_xp:
                levels[user_id]["level"] += 1
                levels[user_id]["xp"] = 0  # Réinitialiser l'XP après la montée de niveau
                new_level = levels[user_id]["level"]

                # Envoyer un message de montée de niveau
                level_up_channel_id = config.level_up_channel  # ID du salon de montée en niveau
                level_up_channel = member.guild.get_channel(level_up_channel_id)
                if level_up_channel:
                    await level_up_channel.send(
                        f"🎉 {member.mention} a atteint le niveau {new_level} grâce à son activité vocale !"
                    )

    # Sauvegarder les données de suivi des vocaux
    with open(voice_activity_file, "w") as f:
        json.dump(voice_activity, f, indent=4)

    # Sauvegarder les données de niveaux
    with open(levels_file, "w") as f:
        json.dump(levels, f, indent=4)
 #FIN}


 #{DEBUT : Event de bienvenue 
class WelcomeButtonView(View):
    def __init__(self, member):
        super().__init__(timeout=None)  # Pas de timeout pour garder le bouton actif
        self.member = member
        self.welcome_count = 0  # Compteur de clics sur le bouton
        self.clicked_users = set()  # Ensemble pour stocker les utilisateurs ayant cliqué

        # Liste d'icônes aléatoires
        self.icons = config.icons  # Liste d'icônes à définir dans votre fichier de configuration
        self.current_icon = random.choice(self.icons)  # Choisir une icône aléatoire

    @discord.ui.button(label="Souhaiter la bienvenue", style=discord.ButtonStyle.green, emoji="🎉")
    async def welcome_button(self, interaction: discord.Interaction, button: Button):
        """
        Action déclenchée lorsqu'un utilisateur clique sur le bouton.
        """
        # Vérifier si l'utilisateur a déjà cliqué
        if interaction.user.id in self.clicked_users:
            await interaction.response.send_message(
                "❌ Vous avez déjà souhaité la bienvenue à cet utilisateur !",
                ephemeral=True
            )
            return

        # Ajouter l'utilisateur à la liste des utilisateurs ayant cliqué
        self.clicked_users.add(interaction.user.id)

        # Charger les données de niveaux
        with open(levels_file, "r") as f:
            levels = json.load(f)

        # Ajouter 10 XP à l'utilisateur qui clique
        user_id = str(interaction.user.id)
        if user_id not in levels:
            levels[user_id] = {"xp": 0, "level": 1}
        levels[user_id]["xp"] += 10

        # Sauvegarder les données de niveaux
        with open(levels_file, "w") as f:
            json.dump(levels, f, indent=4)

        # Mettre à jour le compteur de clics
        self.welcome_count += 1
        self.current_icon = random.choice(self.icons)  # Changer l'icône aléatoire
        button.label = f"{self.welcome_count} membre(s) vous souhaitent la bienvenue !"
        button.emoji = self.current_icon  # Mettre à jour l'icône du bouton
        await interaction.response.edit_message(view=self)

        # Envoyer un message éphémère pour informer l'utilisateur
        await interaction.followup.send(
            f"🎉 Vous avez gagné **10 XP** pour avoir souhaité la bienvenue à {self.member.mention} !",
            ephemeral=True
        )


@bot.event
async def on_member_join(member):
    """
    Événement déclenché lorsqu'un utilisateur rejoint le serveur.
    Envoie un message de bienvenue avec un bouton interactif.
    Le message est automatiquement supprimé après 20 minutes.
    """
    # Récupérer le salon de bienvenue
    welcome_channel_id = config.welcome_channel  # ID du salon de bienvenue
    welcome_channel = bot.get_channel(welcome_channel_id)

    if welcome_channel:
        # Choisir un message de bienvenue aléatoire
        welcome_message = random.choice(config.welcome_messages).format(member=member)

        # Créer une vue avec le bouton
        view = WelcomeButtonView(member)

        # Envoyer le message de bienvenue avec le bouton
        message = await welcome_channel.send(
            welcome_message,
            view=view
        )

        # Supprimer le message après 20 minutes
        await asyncio.sleep(1200)  # 1200 secondes = 20 minutes
        await message.delete()
 #FIN}

#{DEBUT : CMD de Verrouilliage !
@bot.tree.command(name="lock", description="Verrouiller le salon ou le fil actuel.")
async def lock(interaction: discord.Interaction):
    """
    Commande pour verrouiller le salon ou le fil où la commande est exécutée.
    Seuls les administrateurs ou le créateur du fil peuvent exécuter cette commande.
    """
    channel = interaction.channel  # Récupère le salon ou le fil actuel
    user = interaction.user  # Récupère l'utilisateur qui exécute la commande

    # Vérifie si l'utilisateur est administrateur
    if not user.guild_permissions.administrator:
        # Si le canal est un fil, vérifie si l'utilisateur est le créateur du fil
        if isinstance(channel, discord.Thread) and channel.owner_id != user.id:
            await interaction.response.send_message(
                "Vous devez être administrateur ou le créateur de ce fil pour exécuter cette commande.",
                ephemeral=True
            )
            return
        # Si ce n'est pas un fil, l'utilisateur doit être administrateur
        elif not isinstance(channel, discord.Thread):
            await interaction.response.send_message(
                "Vous devez être administrateur pour exécuter cette commande.",
                ephemeral=True
            )
            return

    # Vérifie le type de canal
    if isinstance(channel, discord.TextChannel):
        # Verrouille un salon textuel
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message(f"Le salon textuel {channel.name} a été verrouillé.", ephemeral=True)

    elif isinstance(channel, discord.Thread):
        # Verrouille un fil
        await channel.edit(locked=True)
        await interaction.response.send_message(f"Le fil {channel.name} a été verrouillé.", ephemeral=True)

    else:
        # Si le type de salon n'est pas pris en charge
        await interaction.response.send_message("Ce type de salon ne peut pas être verrouillé.", ephemeral=True)
#FIN}

#{DEBUT : CMD Supprimer un ou plusieurs messages dans le salon actuel.
@bot.tree.command(name="clear", description="Supprimer un ou plusieurs messages dans le salon actuel.")
async def clear(interaction: discord.Interaction, user: discord.User = None, limit: int = 10):
    """
    :param user: L'utilisateur dont les messages doivent être supprimés.
    :param limit: Le nombre maximum de messages à vérifier.
    """
    channel = interaction.channel  # Récupère le salon actuel

    # Vérifie si le canal est un salon textuel
    if not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message("Cette commande ne peut être utilisée que dans un salon textuel.", ephemeral=True)
        return

    # Vérifie si l'utilisateur a la permission de gérer les messages
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Vous n'avez pas la permission de gérer les messages.", ephemeral=True)
        return
    
    # Envoie une réponse différée pour éviter l'expiration de l'interaction
    await interaction.response.defer(ephemeral=True)

    # Supprime les messages
    def check_message(message):
        return user is None or message.author == user

    deleted = await channel.purge(limit=limit, check=check_message)
    await interaction.followup.send(f"{len(deleted)} message(s) supprimé(s).", ephemeral=True)
#FIN}

#{DEBUT : CMD afficher le niveau d'un utilisateur ou votre propre niveau.
@bot.tree.command(name="level", description="Afficher le niveau d'un utilisateur ou votre propre niveau.")
async def level(interaction: discord.Interaction, user: discord.User = None):
    """
    :param interaction: L'interaction Discord.
    :param user: L'utilisateur dont le niveau doit être affiché (facultatif).
    """
    # Si aucun utilisateur n'est mentionné, utiliser l'utilisateur qui exécute la commande
    if user is None:
        user = interaction.user

    # Charger les données de niveaux
    with open(levels_file, "r") as f:
        levels = json.load(f)

    user_id = str(user.id)  # ID de l'utilisateur sous forme de chaîne

    # Vérifie si l'utilisateur a des données de niveau
    if user_id not in levels:
        await interaction.response.send_message(f"{user.mention} n'a pas encore de niveau.", ephemeral=True)
        return

    # Récupère le niveau et l'XP de l'utilisateur
    user_level = levels[user_id]["level"]
    user_xp = levels[user_id]["xp"]
    next_level_xp = user_level * 100  # Calcul du seuil pour le prochain niveau

    # Envoie une réponse avec les informations de niveau
    await interaction.response.send_message(
        f"📊 {user.mention} est au niveau **{user_level}** avec **{user_xp}/{next_level_xp} XP**.",
        ephemeral=True
    )
#FIN}

#{DEBUT : CMD Ajouter de XP manuellement à un utilisateur.
@bot.tree.command(name="add_xp", description="Ajouter des XP à un utilisateur.")
async def add_xp(interaction: discord.Interaction, user: discord.User, xp: int):
    """
    :param interaction: L'interaction Discord.
    :param user: L'utilisateur à qui ajouter des XP.
    :param xp: Le nombre d'XP à ajouter.
    """
    # Vérifie si l'utilisateur qui exécute la commande est administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    # Charger les données de niveaux
    with open(levels_file, "r") as f:
        levels = json.load(f)

    user_id = str(user.id)  # ID de l'utilisateur sous forme de chaîne

    # Vérifie si l'utilisateur a des données de niveau, sinon les initialise
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}

    # Ajouter les XP à l'utilisateur
    levels[user_id]["xp"] += xp
    current_xp = levels[user_id]["xp"]
    current_level = levels[user_id]["level"]

    # Calculer le seuil pour monter de niveau
    next_level_xp = current_level * 100
    new_level = None

    # Vérifie si l'utilisateur monte de niveau
    while current_xp >= next_level_xp:
        levels[user_id]["level"] += 1
        current_xp -= next_level_xp
        next_level_xp = levels[user_id]["level"] * 100
        new_level = levels[user_id]["level"]

    # Met à jour les XP restants
    levels[user_id]["xp"] = current_xp

    # Sauvegarder les données de niveaux
    with open(levels_file, "w") as f:
        json.dump(levels, f, indent=4)

    # Réponse à l'utilisateur
    if new_level:
        await interaction.response.send_message(
            f"🎉 {user.mention} a reçu **{xp} XP** et est maintenant au niveau **{new_level}** avec **{current_xp}/{next_level_xp} XP**.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"🎉 {user.mention} a reçu **{xp} XP** et est maintenant à **{current_xp}/{next_level_xp} XP** pour le niveau **{current_level}**.",
            ephemeral=True
        )
#FIN}

#{DEBUT : CMD Retirer des xp à un utilisateur.
@bot.tree.command(name="remove_xp", description="Retirer des XP à un utilisateur.")
async def remove_xp(interaction: discord.Interaction, user: discord.User, xp: int):
    """
    Commande pour retirer des XP à un utilisateur.
    :param interaction: L'interaction Discord.
    :param user: L'utilisateur à qui retirer des XP.
    :param xp: Le nombre d'XP à retirer.
    """
    # Vérifie si l'utilisateur qui exécute la commande est administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    # Charger les données de niveaux
    with open(levels_file, "r") as f:
        levels = json.load(f)

    user_id = str(user.id)  # ID de l'utilisateur sous forme de chaîne

    # Vérifie si l'utilisateur a des données de niveau, sinon les initialise
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}

    # Retirer les XP à l'utilisateur
    levels[user_id]["xp"] -= xp
    if levels[user_id]["xp"] < 0:  # Si les XP deviennent négatifs, ajustez-les
        levels[user_id]["xp"] = 0

    current_xp = levels[user_id]["xp"]
    current_level = levels[user_id]["level"]

    # Vérifie si l'utilisateur descend de niveau
    while current_xp < 0 and current_level > 1:
        levels[user_id]["level"] -= 1
        current_level = levels[user_id]["level"]
        current_xp += current_level * 100  # Ajoute le seuil du niveau précédent

    # Met à jour les XP restants
    levels[user_id]["xp"] = current_xp

    # Sauvegarder les données de niveaux
    with open(levels_file, "w") as f:
        json.dump(levels, f, indent=4)

    # Réponse à l'utilisateur
    await interaction.response.send_message(
        f"📉 {user.mention} a perdu **{xp} XP** et est maintenant au niveau **{current_level}** avec **{current_xp}/{current_level * 100} XP**.",
        ephemeral=True
    )
#FIN}

#{DEBUT : CMD Envoie de message
@bot.tree.command(name="message", description="Envoyer un message dans un salon spécifique.")
async def message(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    """
    :param interaction: L'interaction Discord.
    :param channel: Le salon où envoyer le message.
    :param message: Le contenu du message à envoyer.
    """
    # Vérifie si l'utilisateur qui exécute la commande est administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    # Envoie le message dans le salon spécifié
    try:
        await channel.send(message)
        await interaction.response.send_message(f"Message envoyé dans {channel.mention} :\n{message}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Une erreur s'est produite lors de l'envoi du message : {e}", ephemeral=True)
#FIN}

#{DEBUT : CMD Info utilisateur
@bot.tree.command(name="user_info", description="Obtenir des informations détaillées sur un utilisateur.")
async def user_info(interaction: discord.Interaction, user: discord.User = None):
    """
    Commande pour afficher des informations détaillées sur un utilisateur sous forme d'embed.
    :param interaction: L'interaction Discord.
    :param user: L'utilisateur dont les informations doivent être affichées (facultatif).
    """
    # Si aucun utilisateur n'est mentionné, utiliser l'utilisateur qui exécute la commande
    if user is None:
        user = interaction.user

    # Récupérer les informations du membre si possible
    member = interaction.guild.get_member(user.id)

    # Charger les données de sanctions
    with open(sanctions_file, "r") as f:
        sanctions = json.load(f)

    # Charger les données de suivi des vocaux
    with open(voice_activity_file, "r") as f:
        voice_activity = json.load(f)

    user_id = str(user.id)  # ID de l'utilisateur sous forme de chaîne

    # Récupérer les sanctions de l'utilisateur
    user_sanctions = sanctions.get(user_id, {"ban": 0, "mute": 0, "warn": 0})
    ban_count = user_sanctions["ban"]
    mute_count = user_sanctions["mute"]
    warn_count = user_sanctions["warn"]

    # Récupérer les données de suivi des vocaux
    user_voice_data = voice_activity.get(user_id, {"total_time": 0, "join_count": 0})
    total_time = user_voice_data["total_time"]
    join_count = user_voice_data["join_count"]

    # Convertir le temps total en heures, minutes et secondes
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Créer un embed pour afficher les informations
    embed = discord.Embed(
        title=f"Informations sur {user.name}",
        color=discord.Color.blue(),
        timestamp=interaction.created_at
    )
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

    # Ajouter les informations de base
    embed.add_field(name="Nom d'utilisateur", value=f"{user.name}#{user.discriminator}", inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Bot ?", value="Oui" if user.bot else "Non", inline=True)

    # Ajouter les informations sur le compte
    embed.add_field(name="Compte créé le", value=user.created_at.strftime("%d/%m/%Y à %H:%M:%S"), inline=True)

    # Ajouter les informations spécifiques au serveur si le membre est dans le serveur
    if member:
        embed.add_field(name="A rejoint le serveur le", value=member.joined_at.strftime("%d/%m/%Y à %H:%M:%S"), inline=True)
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        embed.add_field(name="Rôles", value=", ".join(roles) if roles else "Aucun rôle", inline=False)
        embed.add_field(name="Statut", value=str(member.status).capitalize(), inline=True)
        embed.add_field(name="Activité", value=member.activity.name if member.activity else "Aucune", inline=True)

    # Ajouter les informations sur les sanctions
    embed.add_field(name="Sanctions", value=(
        f"🚫 **Bannissements** : {ban_count}\n"
        f"🔇 **Mutes** : {mute_count}\n"
        f"⚠️ **Avertissements** : {warn_count}"
    ), inline=False)

    # Ajouter les informations sur le suivi des vocaux
    embed.add_field(name="Activité vocale", value=(
        f"⏳ **Temps total passé en vocal** : {hours}h {minutes}m {seconds}s\n"
        f"🔄 **Nombre de connexions en vocal** : {join_count}"
    ), inline=False)

    # Ajouter un footer
    embed.set_footer(text=f"Demandé par {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)

    # Envoyer l'embed
    await interaction.response.send_message(embed=embed)
#FIN}

#{DEBUT : CMD Sanctionner un utilisateur
@bot.tree.command(name="sanction", description="Sanctionner un utilisateur (bannir, mute, avertir).")
async def sanction(interaction: discord.Interaction, user: discord.Member, action: str, reason: str = "Aucune raison spécifiée"):
    """
    Commande pour sanctionner un utilisateur.
    :param interaction: L'interaction Discord.
    :param user: L'utilisateur à sanctionner.
    :param action: L'action à effectuer (ban, mute, warn).
    :param reason: La raison de la sanction.
    """
    # Vérifie si l'utilisateur qui exécute la commande est administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    # Envoie une réponse différée pour éviter l'expiration de l'interaction
    await interaction.response.defer(ephemeral=True)

    # Vérifie l'action demandée
    action = action.lower()
    if action not in ["ban", "mute", "warn"]:
        await interaction.followup.send("Action invalide. Utilisez `ban`, `mute` ou `warn`.", ephemeral=True)
        return

    # Charger les données de sanctions
    with open(sanctions_file, "r") as f:
        sanctions = json.load(f)

    user_id = str(user.id)  # ID de l'utilisateur sous forme de chaîne

    # Initialiser les sanctions pour l'utilisateur s'il n'existe pas encore
    if user_id not in sanctions:
        sanctions[user_id] = {"ban": 0, "mute": 0, "warn": 0}

    # Préparer le message de notification pour le membre
    try:
        if action == "ban":
            await user.send(f"🚫 Vous avez été **banni** du serveur **{interaction.guild.name}** pour la raison : {reason}.")
            await user.ban(reason=reason)
            sanctions[user_id]["ban"] += 1  # Incrémenter le compteur de bannissements
            await interaction.followup.send(f"🚫 {user.mention} a été **banni** pour la raison : {reason}.", ephemeral=True)

        elif action == "mute":
            mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
            if not mute_role:
                # Crée le rôle "Muted" s'il n'existe pas
                mute_role = await interaction.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
                for channel in interaction.guild.channels:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)
            await user.add_roles(mute_role, reason=reason)
            await user.send(f"🔇 Vous avez été **muté** sur le serveur **{interaction.guild.name}** pour la raison : {reason}.")
            sanctions[user_id]["mute"] += 1  # Incrémenter le compteur de mutes
            await interaction.followup.send(f"🔇 {user.mention} a été **muté** pour la raison : {reason}.", ephemeral=True)

        elif action == "warn":
            await user.send(f"⚠️ Vous avez reçu un **avertissement** sur le serveur **{interaction.guild.name}** pour la raison : {reason}.")
            sanctions[user_id]["warn"] += 1  # Incrémenter le compteur d'avertissements
            await interaction.followup.send(f"⚠️ {user.mention} a reçu un **avertissement** pour la raison : {reason}.", ephemeral=True)

    except discord.Forbidden:
        await interaction.followup.send(f"❌ Impossible d'envoyer un message privé à {user.mention}.", ephemeral=True)

    # Sauvegarder les données de sanctions
    with open(sanctions_file, "w") as f:
        json.dump(sanctions, f, indent=4)
#FIN}

#{DEBUT : CMD Lever une sanction d'un utilisateur.
@bot.tree.command(name="unsanction", description="Lever une sanction sur un utilisateur (débannir ou retirer le mute).")
async def unsanction(interaction: discord.Interaction, user: discord.Member, action: str):
    """
    :param interaction: L'interaction Discord.
    :param user: L'utilisateur à libérer de la sanction.
    :param action: L'action à effectuer (unban, unmute).
    """
    # Vérifie si l'utilisateur qui exécute la commande est administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    # Vérifie l'action demandée
    action = action.lower()
    if action not in ["unban", "unmute"]:
        await interaction.response.send_message("Action invalide. Utilisez `unban` ou `unmute`.", ephemeral=True)
        return

    # Effectuer l'action
    if action == "unban":
        bans = await interaction.guild.bans()
        for ban_entry in bans:
            if ban_entry.user.id == user.id:
                await interaction.guild.unban(user)
                await interaction.response.send_message(f"✅ {user.mention} a été **débanni**.", ephemeral=True)
                return
        await interaction.response.send_message(f"❌ {user.mention} n'est pas banni.", ephemeral=True)

    elif action == "unmute":
        # Vérifie si le rôle "Muted" existe
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            await interaction.response.send_message("Le rôle `Muted` n'existe pas dans ce serveur.", ephemeral=True)
            return

        # Vérifie si l'utilisateur a le rôle "Muted"
        if mute_role in user.roles:
            await user.remove_roles(mute_role)
            try:
                # Envoie un message privé à l'utilisateur
                await user.send(f"✅ Vous n'êtes plus **muté** sur le serveur **{interaction.guild.name}**.")
            except discord.Forbidden:
                await interaction.followup.send(f"❌ Impossible d'envoyer un message privé à {user.mention}.", ephemeral=True)
            await interaction.response.send_message(f"✅ {user.mention} n'est plus **muté**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {user.mention} n'est pas muté.", ephemeral=True)
#FIN}

#{DEBUT : CMD Commandes personnalisées
@bot.tree.command(name="custom", description="Gérer les commandes personnalisées.")
async def custom(interaction: discord.Interaction, action: str, command_name: str = None, message: str = None):
    """
    :param interaction: L'interaction Discord.
    :param action: L'action à effectuer (add, remove, list).
    :param command_name: Le nom de la commande personnalisée.
    :param message: Le message associé à la commande (pour l'action 'add').
    """
    # Vérifie si l'utilisateur est administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    # Charger les commandes personnalisées
    with open(custom_commands_file, "r") as f:
        custom_commands = json.load(f)

    action = action.lower()

    if action == "add":
        if not command_name or not message:
            await interaction.response.send_message("Veuillez fournir un nom de commande et un message.", ephemeral=True)
            return
        custom_commands[command_name] = message
        with open(custom_commands_file, "w") as f:
            json.dump(custom_commands, f, indent=4)
        await interaction.response.send_message(f"✅ La commande personnalisée `{command_name}` a été ajoutée avec le message : `{message}`.", ephemeral=True)

    elif action == "remove":
        if not command_name:
            await interaction.response.send_message("Veuillez fournir le nom de la commande à supprimer.", ephemeral=True)
            return
        if command_name in custom_commands:
            del custom_commands[command_name]
            with open(custom_commands_file, "w") as f:
                json.dump(custom_commands, f, indent=4)
            await interaction.response.send_message(f"❌ La commande personnalisée `{command_name}` a été supprimée.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ La commande `{command_name}` n'existe pas.", ephemeral=True)

    elif action == "list":
        if not custom_commands:
            await interaction.response.send_message("Aucune commande personnalisée n'a été définie.", ephemeral=True)
        else:
            commands_list = "\n".join([f"- `{cmd}` : {msg}" for cmd, msg in custom_commands.items()])
            await interaction.response.send_message(f"📜 Liste des commandes personnalisées :\n{commands_list}", ephemeral=True)

    else:
        await interaction.response.send_message("Action invalide. Utilisez `add`, `remove` ou `list`.", ephemeral=True)
#FIN}


#{DEBUT : CMD Anniversaire define
from discord.ui import View, Button, Modal, TextInput

class BirthdayModal(Modal):
    def __init__(self, user_id):
        super().__init__(title="Enregistrer votre anniversaire")
        self.user_id = user_id

        # Champ pour saisir la date d'anniversaire
        self.birthday_input = TextInput(
            label="Date d'anniversaire (JJ/MM)",
            placeholder="Exemple : 25/12",
            required=True
        )
        self.add_item(self.birthday_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Charger les données des anniversaires
        with open(birthdays_file, "r") as f:
            birthdays = json.load(f)

        # Enregistrer la date d'anniversaire
        birthdays[str(self.user_id)] = self.birthday_input.value

        # Sauvegarder les données
        with open(birthdays_file, "w") as f:
            json.dump(birthdays, f, indent=4)

        await interaction.response.send_message(
            f"🎉 Votre date d'anniversaire a été enregistrée : **{self.birthday_input.value}** !",
            ephemeral=True
        )

class BirthdayPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ajouter/Modifier ma date", style=discord.ButtonStyle.green, emoji="🎂")
    async def add_birthday(self, interaction: discord.Interaction, button: Button):
        modal = BirthdayModal(user_id=interaction.user.id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Supprimer ma date", style=discord.ButtonStyle.red, emoji="🗑️")
    async def remove_birthday(self, interaction: discord.Interaction, button: Button):
        # Charger les données des anniversaires
        with open(birthdays_file, "r") as f:
            birthdays = json.load(f)

        # Supprimer la date d'anniversaire si elle existe
        if str(interaction.user.id) in birthdays:
            del birthdays[str(interaction.user.id)]
            with open(birthdays_file, "w") as f:
                json.dump(birthdays, f, indent=4)
            await interaction.response.send_message("🗑️ Votre date d'anniversaire a été supprimée.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Vous n'avez pas encore enregistré de date d'anniversaire.", ephemeral=True)

    @discord.ui.button(label="Voir la liste", style=discord.ButtonStyle.blurple, emoji="📜")
    async def view_birthdays(self, interaction: discord.Interaction, button: Button):
        # Charger les données des anniversaires
        with open(birthdays_file, "r") as f:
            birthdays = json.load(f)

        if not birthdays:
            await interaction.response.send_message("📜 Aucune date d'anniversaire n'a été enregistrée.", ephemeral=True)
            return

        # Construire la liste des anniversaires
        birthday_list = "\n".join(
            [f"<@{user_id}> : **{date}**" for user_id, date in birthdays.items()]
        )
        await interaction.response.send_message(f"📜 **Liste des anniversaires enregistrés :**\n{birthday_list}", ephemeral=True)

@bot.tree.command(name="anniv", description="Gérer les anniversaires des membres.")
async def anniv(interaction: discord.Interaction):
    """
    Commande pour afficher le panneau de gestion des anniversaires.
    """
    view = BirthdayPanelView()
    await interaction.response.send_message(
        "🎂 **Panneau de gestion des anniversaires**\n- Ajoutez ou modifiez votre date d'anniversaire.\n- Supprimez votre date.\n- Consultez la liste des anniversaires enregistrés.",
        view=view,
        ephemeral=True
    )
#FIN}

#{DEBUT : CMD Wivia
@bot.tree.command(name="wyvia", description="Commandes de sanction de la princesse Wyvia.")
async def wyvia(interaction: discord.Interaction, user: discord.Member, action: str):
    """
    :param user: Le sujet concerné.
    :param action: L'action à effectuer (emprisonner, liberer).
    """ 
    try:
        await interaction.response.defer(ephemeral=True)
        # Vérifie si l'utilisateur qui exécute la commande est la princesse Wyvia
        if interaction.user.id != 1024341153216204830:  # ID de la princesse Wyvia
            # Si l'utilisateur n'est pas la princesse Wyvia, envoie un message d'erreur
            await interaction.followup.send("<:hien:1243293271783112745> Hum tu essayes d'usurper l'identité de la princesse Wyvia ...\nTu iras en prison toi!", ephemeral=True)
            return
    
        # Vérifie l'action demandée
        action = action.lower()
        if action not in ["emprisonner", "liberer"]:
            await interaction.followup.send("<a:popcat:1307808741353066497> Princesse, vous pouvez `emprisonner` ou `liberer`.\n-# L'orthographe doit-être correcte telle que precisée.", ephemeral=True)
            return

        # Effectuer l'action
        if action == "emprisonner":
            prison = discord.utils.get(interaction.guild.roles, name="En Prison")
            if not prison:
                    # Crée le rôle "En Prison" s'il n'existe pas
                    prison = await interaction.guild.create_role(name="En Prison", permissions=discord.Permissions(send_messages=False, speak=False))
                    for channel in interaction.guild.channels:
                        await channel.set_permissions(prison, send_messages=False, speak=False)
            await user.add_roles(prison)
            try:
                await user.send(f" Vous avez été mis **en Prison** sur le serveur **{interaction.guild.name}**.")
                await interaction.followup.send(f" {user.mention} est désormais en prison ! Il ne pourra pas gagner des xp, tant qu'il ne sera pas libre.", ephemeral=True)
            except discord.Forbidden:
                await interaction.followup.send(f" {user.mention} est désormais en prison ! Mais impossible de l'envoyer un message privé.", ephemeral=True)

        elif action == "liberer":
            # Vérifie si le rôle "En Prison" existe
            prison = discord.utils.get(interaction.guild.roles, name="En Prison")
            
            if not prison:
                await interaction.followup.send("Le rôle `En Prison` n'existe pas dans ce serveur.", ephemeral=True)
                return

            # Vérifie si l'utilisateur a le rôle "En Prison"
            if prison in user.roles:
                await user.remove_roles(prison)
                try:
                    # Envoie un message privé à l'utilisateur
                    await user.send(f"✅ Vous n'êtes plus **En Prison** sur le serveur **{interaction.guild.name}**.")
                    await interaction.followup.send(f"✅ {user.mention} n'est plus **En Prison**.", ephemeral=True)
                    return
                except Exception as e:
                    # Si l'envoi du message échoue, envoie un message d'erreur
                    print(f"Erreur lors de l'envoi du message privé à {user.name}: {e}")
                    await interaction.followup.send(f"✅ {user.mention} n'est plus **En Prison** mais, Impossible d'envoyer un message privé à {user.mention}.", ephemeral=True)
                    return
            else:
                await interaction.followup.send(f"❌ {user.mention} n'est pas En Prison.", ephemeral=True)
                return

    except Exception as e:
        print(f"Erreur dans la commande wyvia : {e}")
#FIN}

#{DEBUT: CMD d'aide !
@bot.tree.command(name="help", description="Afficher toutes les fonctionnalités du bot.")
async def help_command(interaction: discord.Interaction):
    """
    Commande pour afficher toutes les fonctionnalités du bot dans un joli embed.
    """
    # Créer un embed
    embed = discord.Embed(
        title="📚 Liste des fonctionnalités du bot",
        description="Découvrez toutes les fonctionnalités incroyables que ce bot peut offrir !",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)

    # Ajouter les fonctionnalités
    embed.add_field(
        name="🔒 **Verrouillage**",
        value="`/lock` : Verrouillez un salon ou un fil pour empêcher les utilisateurs d'envoyer des messages.",
        inline=False
    )
    embed.add_field(
        name="🧹 **Nettoyage**",
        value="`/clear` : Supprimez rapidement un ou plusieurs messages dans un salon pour garder les discussions propres.",
        inline=False
    )
    embed.add_field(
        name="📊 **Niveau**",
        value="`/level` : Consultez votre niveau ou celui d'un autre utilisateur pour voir votre progression.",
        inline=False
    )
    embed.add_field(
        name="🎉 **Ajouter des XP**",
        value="`/add_xp` : Récompensez un utilisateur en lui ajoutant des points d'expérience.",
        inline=False
    )
    embed.add_field(
        name="📉 **Retirer des XP**",
        value="`/remove_xp` : Retirez des points d'expérience à un utilisateur en cas de besoin.",
        inline=False
    )
    embed.add_field(
        name="📨 **Envoyer un message**",
        value="`/send_message` : Envoyez un message dans un salon spécifique pour partager des informations importantes.",
        inline=False
    )
    embed.add_field(
        name="👤 **Info utilisateur**",
        value="`/user_info` : Obtenez des informations détaillées sur un utilisateur, y compris ses rôles et son activité.",
        inline=False
    )
    embed.add_field(
        name="⚠️ **Sanction**",
        value="`/sanction` : Sanctionnez un utilisateur en le bannissant, en le mutant ou en lui donnant un avertissement.",
        inline=False
    )
    embed.add_field(
        name="✅ **Lever une sanction**",
        value="`/unsanction` : Annulez une sanction appliquée à un utilisateur, comme un bannissement ou un mute.",
        inline=False
    )
    embed.add_field(
        name="⚙️ **Commandes personnalisées**",
        value="`/custom_command` : Créez, modifiez ou supprimez des commandes personnalisées pour enrichir votre serveur.",
        inline=False
    )
    embed.add_field(
        name="📝 **Confessions anonymes**",
        value="Permettez aux utilisateurs de partager des confessions anonymes dans un salon dédié avec `$$.confess`.",
        inline=False
    )
    embed.add_field(
        name="🎙️ **Suivi vocal**",
        value="Suivez le temps passé en vocal par les membres et attribuez des XP en fonction de leur activité.",
        inline=False
    )
    embed.add_field(
        name="🎉 **Bienvenue**",
        value="Souhaitez la bienvenue aux nouveaux membres avec un message interactif et des récompenses en XP.",
        inline=False
    )
    embed.add_field(
        name="📜 **Création automatique de fils**",
        value="Créez automatiquement des fils de discussion pour organiser les conversations dans certains salons.",
        inline=False
    )
    embed.add_field(
        name="🔔 **Rappel de bump**",
        value="Recevez des rappels automatiques pour bumper le serveur et attribuez des XP aux membres qui le font.",
        inline=False
    )
    embed.add_field(
        name="🎂 **Anniversaires**",
        value="Permettez aux membres d'enregistrer leur date d'anniversaire et recevez un message le jour J avec `/anniv`.",
        inline=False
    )
    embed.add_field(
        name="📢 **Annonces Twitch**",
        value="Recevez des notifications automatiques lorsqu'une chaîne Twitch configurée commence un stream.",
        inline=False
    )
    embed.add_field(
        name="⚙️ **Configuration**",
        value="Gérez les paramètres du bot via un panneau interactif avec `/config`.",
        inline=False
    )

    # Ajouter un footer
    embed.set_footer(
        text=f"Demandé par {interaction.user.name}",
        icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
    )

    # Envoyer l'embed
    await interaction.response.send_message(embed=embed)
#FIN}

#{DEBUT: Config du bot !
class ConfigSelectorView(View):
    def __init__(self):
        super().__init__(timeout=None)

        # Ajouter un menu déroulant (select menu)
        self.add_item(ConfigSelector())

class ConfigSelector(Select):
    def __init__(self):
        # Définir les options du sélecteur
        options = [
            discord.SelectOption(label="Salon de bienvenue", description="Modifier le salon de bienvenue", emoji="🔔"),
            discord.SelectOption(label="Salon de log", description="Modifier le salon de log", emoji="📜"),
            discord.SelectOption(label="Salon de niveau up", description="Modifier le salon de niveau up", emoji="🎉"),
            discord.SelectOption(label="Salon de confession", description="Modifier le salon de confession", emoji="📝"),
            discord.SelectOption(label="Salon de bump", description="Modifier le salon de bump", emoji="🔔"),
            discord.SelectOption(label="Salon d'annonces de stream", description="Modifier le salon d'annonces de stream", emoji="📢"),
            discord.SelectOption(label="Salon d'anniversaires", description="Modifier le salon d'anniversaires", emoji="🎂"),
            discord.SelectOption(label="Chaînes Twitch surveillées", description="Modifier les chaînes Twitch surveillées", emoji="🎮"),
            discord.SelectOption(label="Bots de bump", description="Modifier les bots de bump", emoji="🤖"),
            discord.SelectOption(label="Messages de bump", description="Modifier les messages de bump", emoji="📜"),
        ]

        # Initialiser le sélecteur
        super().__init__(
            placeholder="Sélectionnez une configuration à modifier...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        # Récupérer l'option sélectionnée
        selected_option = self.values[0]

        # Gérer chaque option
        if selected_option == "Salon de bienvenue":
            await interaction.response.send_message("Veuillez mentionner le nouveau salon de bienvenue.", ephemeral=True)
        elif selected_option == "Salon de log":
            await interaction.response.send_message("Veuillez mentionner le nouveau salon de log.", ephemeral=True)
        elif selected_option == "Salon de niveau up":
            await interaction.response.send_message("Veuillez mentionner le nouveau salon de niveau up.", ephemeral=True)
        elif selected_option == "Salon de confession":
            await interaction.response.send_message("Veuillez mentionner le nouveau salon de confession.", ephemeral=True)
        elif selected_option == "Salon de bump":
            await interaction.response.send_message("Veuillez mentionner le nouveau salon de bump.", ephemeral=True)
        elif selected_option == "Salon d'annonces de stream":
            await interaction.response.send_message("Veuillez mentionner le nouveau salon d'annonces de stream.", ephemeral=True)
        elif selected_option == "Salon d'anniversaires":
            await interaction.response.send_message("Veuillez mentionner le nouveau salon d'anniversaires.", ephemeral=True)
        elif selected_option == "Chaînes Twitch surveillées":
            await interaction.response.send_message("Veuillez entrer les nouvelles chaînes Twitch (séparées par des virgules).", ephemeral=True)
        elif selected_option == "Bots de bump":
            await interaction.response.send_message("Veuillez entrer les nouveaux bots de bump (séparées par des virgules).", ephemeral=True)
        elif selected_option == "Messages de bump":
            await interaction.response.send_message("Veuillez entrer les nouveaux messages de bump (séparées par des virgules).", ephemeral=True)

@bot.tree.command(name="pannel", description="Gérer la configuration actuelle du bot.")
async def pannel(interaction: discord.Interaction):
    """
    Commande pour afficher le panneau de gestion des configurations.
    """
    # Vérifie si l'utilisateur est administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    # Créer une vue avec le sélecteur
    view = ConfigSelectorView()

    # Envoyer le message avec le sélecteur
    await interaction.response.send_message(
        "⚙️ **Panneau de gestion des configurations**\nSélectionnez une option dans le menu déroulant pour modifier une configuration.",
        view=view,
        ephemeral=True
    )
#FIN}

#{DEBUT : CMD Restart
@bot.tree.command(name="restart", description="Redémarrer le bot.")
async def restart(interaction: discord.Interaction):
    """
    Commande pour redémarrer le bot.
    """
    # Vérifie si l'utilisateur qui exécute la commande est administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return
    try:
        await interaction.response.send_message("🔄 landhaven va redémarrer...", ephemeral=True)
        await bot.close()
        os.execv(sys.executable, ['python'] + sys.argv) # Relance le bot
    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur s'est produite lors du redémarrage : {e}", ephemeral=True)
        print(f"Erreur lors du redémarrage : {e}")
        return
#FIN}

#{DEBUT : Lancement de l'application
bot.run(config.token)
#FIN}