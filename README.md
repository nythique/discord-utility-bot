# 🤖 Discord Utility Bot

Ce projet est un bot Discord multifonction orienté modération, gestion de communauté et utilitaires, développé par **Nythique**. Il propose de nombreuses fonctionnalités pour animer, modérer et personnaliser votre serveur Discord.

> **Note :** Ce projet n'est plus activement maintenu, mais toutes les contributions sont les bienvenues !

## ✨ Fonctionnalités principales

- **Modération avancée** :
  - Verrouillage de salons ou fils (`/lock`)
  - Nettoyage rapide de messages (`/clear`)
  - Système de sanctions : ban, mute, avertissement (`/sanction`, `/unsanction`)
  - Filtrage automatique des messages contenant des mots interdits
- **Système de niveaux et d'XP** :
  - Gain d'XP par message ou activité vocale
  - Attribution automatique de rôles selon le niveau
  - Messages de level-up personnalisés
  - Commandes pour afficher, ajouter ou retirer de l'XP (`/level`, `/add_xp`, `/remove_xp`)
- **Commandes personnalisées** :
  - Ajout, suppression et gestion de commandes custom (`/custom`)
- **Confessions anonymes** :
  - Système de confessions anonymes dans un salon dédié (`$$.confess`)
- **Gestion des anniversaires** :
  - Enregistrement et rappel des anniversaires des membres (`/anniv`)
- **Suivi vocal** :
  - Calcul du temps passé en vocal et attribution d'XP
- **Bienvenue et intégration** :
  - Messages de bienvenue interactifs et personnalisés
- **Création automatique de fils** :
  - Organisation automatique des discussions dans certains salons
- **Rappels de bump** :
  - Rappels automatiques pour bumper le serveur et attribution d'XP
- **Annonces Twitch** :
  - Notification automatique lors du lancement d'un stream sur une chaîne Twitch configurée
- **Panneau de configuration** :
  - Interface interactive pour modifier les paramètres du bot (`/pannel`)

## 🛠️ Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/nythique/discord-utility-bot.git
   cd discord-utility-bot
   ```
2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configurer le bot**
   - Renommez/modifiez le fichier `config/settings.py` avec votre token Discord, vos IDs de salons, et vos préférences.
   - (Optionnel) Configurez les identifiants Twitch si vous souhaitez les notifications de stream.

4. **Lancer le bot**
   ```bash
   python main.py
   ```

## 📁 Structure des données

Les données (niveaux, sanctions, confessions, commandes custom, anniversaires, etc.) sont stockées dans le dossier `cluster/` sous forme de fichiers JSON.

## 🤝 Contribuer

Les contributions sont **ouvertes à tous** ! N'hésitez pas à proposer des améliorations, corriger des bugs ou ajouter de nouvelles fonctionnalités via des pull requests.

## 🛑 Maintenance

Ce projet n'est plus activement maintenu par son auteur. Il peut donc contenir des bugs ou ne pas être à jour avec les dernières versions de Discord.py.

## 👤 Auteur

Développé par **Nythique**.

---

Merci d'utiliser ce bot ! Pour toute question ou suggestion, ouvrez une issue ou une pull request.
