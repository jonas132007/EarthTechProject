# EarthTechProject

# EcoThrow : Ultimate Environment Defender
EcoThrow est un jeu 2D éducatif et amusant développé en Python avec Pygame, dans lequel le joueur doit trier des déchets en les lançant dans les bonnes poubelles, tout en tenant compte de facteurs physiques comme le vent et la gravité.

# Gameplay

Vous contrôlez un déchet et devez viser puis le lancer dans la bonne poubelle de recyclage.

 Objectif :
Trier correctement les déchets (Plastique, Papier, Verre)
Atteindre le score requis pour chaque niveau
Conserver vos vies jusqu’à la fin
⚠ Difficultés :
🌬 Le vent influence la trajectoire
 La gravité varie selon les niveaux
 Une mouette (obstacle mobile) apparaît
Mauvaise poubelle = perte de vie
 Commandes


# Fonctionnalités 
Système de physique réaliste (projectiles)
Différents environnements (Plage, Forêt, Océan)
Obstacle dynamique (mouette)
Animation de pluie
Messages de feedback (réussite / erreur)
Système de vies
Progression par niveaux 
Système physique

Le jeu repose sur des principes simples de physique :

Vitesse initiale calculée avec l’angle et la force
Gravité qui influence la vitesse verticale
Vent qui influence la vitesse horizontale

Une prévisualisation de la trajectoire est affichée avant le lancer (inspiré de Angry Birds).

# Niveaux
Niveau	Nom	Particularités
1	Plage 🌴	Aucun vent, niveau facile
2	Forêt 🌲	Introduction du vent
3	Océan 🌊	Vent fort + mouette + pluie
 Types de déchets
 Plastique
 Papier
 Verre

Chaque déchet doit être lancé dans la bonne poubelle !

# Structure du projet
project/
│
├── main.py       # Boucle principale du jeu
├── physique.py   # Calculs physiques et collisions
├── config.py     # Constantes et paramètres
⚙️ Installation
1. Installer Python (version 3 recommandée)
2. Installer les dépendances
pip install pygame
3. Lancer le jeu
python main.py
# Fonctionnement
 Module physique.py
Calcul des vitesses
Mise à jour des positions
Gestion des collisions
 Fichier main.py
Boucle de jeu
Gestion des entrées clavier
Affichage (graphismes, UI)
 Fichier config.py
Dimensions de l’écran
Couleurs
Paramètres du jeu

# Work Share
This work done equally by Jonas Tubiana, Jean Monier-Vinard Azoulay, and Nuri Ozyer.
