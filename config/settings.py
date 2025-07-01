import os
#=================================================================================
token = os.getenv("DISCORD_TOKEN")  # Token du bot Discord
#================================================================================
cycle = [
         "Mellieur serveur chill",
         "Un staff pas comme les autres !", 
         "Des emojis et autocollants à gogo !",
         "Des bots personnalisés !",
         "Un serveur à la cool !", 
         "Recrutement de staff !",
         "Un serveur pour tous !",
]
#==================================================================================
prefix= os.getenv("PREFIX", "!")  # Préfixe du bot, par défaut "!"
#==================================================================================
banned_words = [
    "Niquer","Va te faire foutre","Con","Conne","Connard",
    "Enculé","Salope","Pute","Bâtard","Pédé","Fdp","Bitch","Tg","Pd","Salo",
    "Gros fils de pute","Ferme ta gueule","Ta mère la pute","Nique ta mère","Grosse merde",
    "Sous-merde","Espèce d'enculé","Sale chien","Fils de chien","Gros enculé","Gros bâtard",
    "Pauvre con","Dégénéré","Tête de mort","Enculeur de mouches","Casse-toi","Bouffon",
    "Tocard","Tête de noeud","Fuck","Go fuck yourself","Asshole","Bitch","Bastard",
    "Motherfucker","Slut","Whore","Son of a bitch","Faggot","SOB","Bitch","STFU",
    "Gaylord","Skank","Big motherfucker","Shut the fuck up","Your mom's a whore","Fuck your mother",
    "Piece of shit","Low-life scum","Fucking prick","Dirty dog","Son of a dog","Big asshole",
    "Big bastard","Stupid fuck","Retard","Shithead","Fly fucker","Get lost",
    "Clown","Loser","Dickhead"
]
#==================================================================================
autoreaction_words = ["bonjour", 
                      "salut", 
                      "hey", 
                      "comment ça va ?", 
                      "ça va ?", 
                      "yo", 
                      "hello",
]
#==================================================================================
level_roles = {
    5: "E-rank Hunter",
    10: "D-rank Hunter",
    15: "C-rank Hunter",
    25: "B-rank Hunter",
    35: "A-rank Hunter",
    45: "S-rank Hunter",
    55: "National Hero",
    65: "Monarch",
    75: "Monarch",
    85: "Divine Majesty",
    95: "Divine Majesty",
    100: "Omni Lord",
}
#==================================================================================
thread_channels = [
        1317915578937118892,  # ID du salon presentation
        1335696194348908584,  # ID du salon selfie
        1320000482046902404,  # ID du salon citation
        1167369803170840606, # ID du salon cration
        1357749202754470148, # ID du salon shoocl annonces
        
] 
#==================================================================================
vocal_channel = None # ID du salon vocal principal
#==================================================================================
welcome_channel = 1167200604448366642 # ID du salon de bienvenue
#==================================================================================
icons = ["🎉", "⛩", "🎈", "🍣", "🔥", "🧩", "👨‍💻", "👩‍💻", "😎", "⚡"]
#==================================================================================
welcome_messages = [
    "🎉 Bienvenue sur le serveur, {member.mention} ! Nous sommes ravis de t'accueillir !",
    "✨ Salut {member.mention} ! Prépare-toi à vivre une expérience incroyable ici !",
    "🎈 Bienvenue, {member.mention} ! Fais comme chez toi et amuse-toi bien !",
    "🌟 Hey {member.mention} ! Toute la communauté est heureuse de te voir ici !",
    "🔥 Bienvenue à bord, {member.mention} ! Clique sur le bouton pour recevoir un accueil chaleureux !",
    "💫 Salut {member.mention} ! Clique sur le bouton ci-dessous pour recevoir des messages de bienvenue !",
    "✈ Bienvenue, {member.mention} ! Nous espérons que tu passeras un bon moment ici !",
    "🍀 Bienvenue sur le serveur, {member.mention} ! Clique sur le bouton pour te faire accueillir !",
    "🏳 Hey {member.mention} ! Nous sommes ravis de t'avoir parmi nous !",
    "⚡ Bienvenue, {member.mention} ! Clique sur le bouton pour recevoir un accueil chaleureux !"
]
#==================================================================================
log_channel = os.getenv("LOG_CHANNEL")  
#==================================================================================
level_up_channel = os.getenv("LEVEL_UP_CHANNEL")  # ID du salon pour les messages de niveau
#==================================================================================
level_up_messages = [
    "## <a:butterflieswhite:1283798557392109609> **{user}** a atteint le niveau **{level}** ! Continue comme ça ! 🚀",
    "## <a:blueflames:1283797575560069231> Bravo **{user}** ! Tu es maintenant au niveau **{level}** ! 💪",
    "## <a:heureux:1244287554321387550> Félicitations **{user}** pour avoir atteint le niveau **{level}** ! 🎊",
    "## ✨ **{user}**, tu viens de passer au niveau **{level}** ! Impressionnant ! 🎉",
    "## 🚀 **{user}** a monté au niveau **{level}** ! Garde le rythme ! <:icecream:1351817673457274920>"
]
#==================================================================================
confession_channel = 1288197998479802420  # Remplacez par l'ID du salon de confession
#==================================================================================
bump_channel_id = 1167201714957467760  # ID du salon où les bumps sont effectués
main_channel_id = 1167200604448366642  # ID du salon principal pour les messages de remerciement
bump_reminder_interval = 7200  # Intervalle de rappel en secondes (2 heures - 7200 secondes)
dell_last_bump = 1500  # 1500 secondes = 25 minutes Supprimer le message après 25 minutes
#==================================================================================
bump_bots = ["DISBOARD",
             "Bumpia", 
             "DL",
] # Liste des noms des bots
bump_messages = [
    "Bump effectué !",
    "Merci d'avoir bumpé le serveur !",
    "Le serveur a bien été bump !",
    "a Voté pour ᨍ 𝚕𝚊𝚗𝚍𝙷𝚊𝚟𝚎𝚗 達🍥",
] # Liste des messages possibles
#==================================================================================
birthday_channel = 123456789012345678  # Remplacez par l'ID du salon pour les messages d'anniversaire
#==================================================================================
# Twitch API Configuration
twitch_client_id = "VOTRE_CLIENT_ID"
twitch_client_secret = "VOTRE_CLIENT_SECRET"
twitch_channels = ["nom_de_la_chaine_twitch1", "nom_de_la_chaine_twitch2"]  # Liste des chaînes Twitch à surveiller
stream_announcement_channel_id = 123456789012345678  # ID du salon Discord pour les annonces de stream
#================================================================================== (AI CONFIG)
