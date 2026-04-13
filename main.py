import pygame
import random
import math
import config
import physique

#  CONFIG INITIALE
pygame.init()  # Démarre tous les modules de Pygame (vidéo, son, événements...)
ecran = pygame.display.set_mode((config.LARGEUR, config.HAUTEUR))  # creation fenetre de jeu
pygame.display.set_caption("EcoThrow: Ultimate Ocean Defender")  # Titre
horloge = pygame.time.Clock()  # Outil pour contrôler la vitesse du jeu (FPS)

# Création des polices d'écriture (Petite, Moyenne, Grande)
police_p = pygame.font.SysFont('Arial', 22, bold=True)
police_m = pygame.font.SysFont('Arial', 32, bold=True)
police_g = pygame.font.SysFont('Arial', 60, bold=True)


# Liste des poubelles avec leurs caractéristiques pour les collisions
poubelles = [
    {'type': 'Plastique', 'couleur': config.JAUNE, 'x': 450, 'y': 450, 'largeur': 70, 'hauteur': 100},
    {'type': 'Papier', 'couleur': config.BLEU, 'x': 575, 'y': 450, 'largeur': 70, 'hauteur': 100},
    {'type': 'Verre', 'couleur': config.VERT, 'x': 700, 'y': 450, 'largeur': 70, 'hauteur': 100}
]

# Définition des niveaux avec difficulter...
niveaux = [
    {'nom': 'Plage', 'ciel': config.CIEL_PLAGE, 'sol': config.SOL_PLAGE, 'vent': 0.0, 'gravite': 0.5, 'score_cible': 3,
     'obstacle': False},
    {'nom': 'Foret', 'ciel': config.CIEL_FORET, 'sol': config.SOL_FORET, 'vent': -0.1, 'gravite': 0.5, 'score_cible': 6,
     'obstacle': False},
    {'nom': 'Ocean', 'ciel': config.CIEL_OCEAN, 'sol': config.SOL_OCEAN, 'vent': 0.25, 'gravite': 0.6,
     'score_cible': 10, 'obstacle': True}
]

# Caractéristiques de l'obstacle mouette
oiseau = {'x': 400, 'y': 250, 'largeur': 80, 'hauteur': 40, 'vitesse': 4}

# Initialisation des variables de jeu: le score, les vies...
etat_jeu = 'MENU'
score = 0
vies = config.VIES_INITIALES
index_niveau = 0
angle_lancer = 45
force_lancer = 15
message_alerte = ""  # message d'affichage
timer_alerte = 0  # Durée d'affichage

# dechet aleatoire au debut
def creer_nouveau_dechet():

    t = random.choice(['Plastique', 'Papier', 'Verre'])
    c = config.JAUNE if t == 'Plastique' else config.BLEU if t == 'Papier' else config.VERT
    return {'x': 80, 'y': 500, 'vx': 0, 'vy': 0, 'rayon': 12, 'type': t, 'couleur': c, 'en_vol': False}


dechet = creer_nouveau_dechet()


running = True
while running:

   # gestion des evenements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # quitter
            running = False

        if event.type == pygame.KEYDOWN:  # Si on appuie sur une touche
            if etat_jeu == 'MENU':
                if event.key == pygame.K_RETURN:  # ENTREE pour lancer le jeu
                    etat_jeu = 'JEU'
                    score = 0
                    vies = config.VIES_INITIALES
                    index_niveau = 0

            elif etat_jeu == 'JEU':
                if event.key == pygame.K_SPACE and not dechet['en_vol']:
                    # Calcule la vitesse X et Y en fonction de la force et de l'angle
                    dechet['vx'], dechet['vy'] = physique.calculer_vitesse_initiale(force_lancer, angle_lancer)
                    dechet['en_vol'] = True

            elif etat_jeu in ['VICTOIRE', 'GAMEOVER']:
                if event.key == pygame.K_r:  # Touche R pour revenir au menu
                    etat_jeu = 'MENU'

    # MISE À JOUR DE LA LOGIQUE: Calculs de mouvement, collisions
    if etat_jeu == 'JEU':
        niveau = niveaux[index_niveau]

        # Déplacement de l'obstacle (mouette)
        if niveau['obstacle']:
            oiseau['x'] += oiseau['vitesse']
            if oiseau['x'] > 720 or oiseau['x'] < 300:  # Rebondit sur les bords invisibles
                oiseau['vitesse'] *= -1

        # Mouvement du déchet si im est lancé
        if dechet['en_vol']:
            dechet['x'], dechet['y'], dechet['vx'], dechet['vy'] = physique.mettre_a_jour_position(
                dechet['x'], dechet['y'], dechet['vx'], dechet['vy'], niveau['gravite'], niveau['vent']
            )

            # Collision avec la mouette
            if niveau['obstacle'] and physique.verifier_collision_obstacle(dechet['x'], dechet['y'], oiseau):
                dechet['vx'] *= -0.8  # Rebond vers l'arrière
                dechet['vy'] = random.uniform(-12, -7)  # Projection aléatoire vers le haut
                message_alerte = "AÏE ! LA MOUETTE !"
                timer_alerte = 40

            # si le dechet sort de l'ecran
            if dechet['y'] > 600 or dechet['x'] > 800 or dechet['x'] < 0:
                vies -= 1
                message_alerte = "RATÉ !"
                timer_alerte = 60
                dechet = creer_nouveau_dechet()
                if vies <= 0: etat_jeu = 'GAMEOVER'

            # Vérification des collisions avec les poubelles
            for p in poubelles:
                if physique.verifier_collision(dechet['x'], dechet['y'], dechet['rayon'], p):
                    if p['type'] == dechet['type']:  # Bonne poubelle !
                        score += 1
                        message_alerte = f"BIEN JOUÉ ! +1 {dechet['type']}"
                    else:  # Mauvaise poubelle !
                        vies -= 1
                        message_alerte = f"NON ! C'était du {dechet['type']}"

                    timer_alerte = 90
                    dechet = creer_nouveau_dechet()

                    if vies <= 0:
                        etat_jeu = 'GAMEOVER'
                    elif score >= niveau['score_cible']:  # Niveau terminé ?
                        if index_niveau < len(niveaux) - 1:
                            index_niveau += 1
                            message_alerte = "NIVEAU SUIVANT !"
                            timer_alerte = 100
                        else:
                            etat_jeu = 'VICTOIRE'
                    break
        else:
            # Commandes de visée (quand le déchet n'est pas encore lancé)
            touches = pygame.key.get_pressed()
            if touches[pygame.K_UP] and angle_lancer < 90: angle_lancer += 1
            if touches[pygame.K_DOWN] and angle_lancer > 0: angle_lancer -= 1
            if touches[pygame.K_RIGHT] and force_lancer < 25: force_lancer += 0.3
            if touches[pygame.K_LEFT] and force_lancer > 5: force_lancer -= 0.3

    #  AFFICHAGE (Dessin sur l'écran)
    if etat_jeu == 'MENU':
        ecran.fill(config.NOIR)
        t_titre = police_g.render("ECO THROW", True, config.VERT)
        ecran.blit(t_titre, (config.LARGEUR // 2 - t_titre.get_width() // 2, 150))
        ecran.blit(police_m.render("Appuyez sur ENTREE pour jouer", True, config.BLANC), (180, 300))

    elif etat_jeu == 'JEU':
        # Dessin de l'environnement (Ciel et Sol)
        ecran.fill(niveau['ciel'])
        pygame.draw.rect(ecran, niveau['sol'], (0, 520, 800, 80))

        # Dessin de la mouette (si présente)
        if niveau['obstacle']:
            # Corps de l'oiseau
            pygame.draw.ellipse(ecran, (240, 240, 240),
                                (oiseau['x'], oiseau['y'], oiseau['largeur'], oiseau['hauteur']))
            # Ailes (traits noirs)
            pygame.draw.line(ecran, config.NOIR, (oiseau['x'], oiseau['y'] + 15), (oiseau['x'] - 25, oiseau['y'] - 5),
                             3)
            pygame.draw.line(ecran, config.NOIR, (oiseau['x'] + oiseau['largeur'], oiseau['y'] + 15),
                             (oiseau['x'] + oiseau['largeur'] + 25, oiseau['y'] - 5), 3)
            ecran.blit(police_p.render("MOUETTE !", True, config.ROUGE), (oiseau['x'], oiseau['y'] - 30))

        # Dessin des 3 poubelles
        for p in poubelles:
            pygame.draw.rect(ecran, p['couleur'], (p['x'], p['y'], p['largeur'], p['hauteur']))
            pygame.draw.rect(ecran, config.NOIR, (p['x'], p['y'], p['largeur'], p['hauteur']), 2)
            txt = police_p.render(p['type'], True, config.NOIR)
            ecran.blit(txt, (p['x'] + p['largeur'] // 2 - txt.get_width() // 2, p['y'] + 40))

        # Dessin de la trajectoire de visée (avant le lancer)
        if not dechet['en_vol']:
            fx = dechet['x'] + (force_lancer * 5) * math.cos(math.radians(angle_lancer))
            fy = dechet['y'] - (force_lancer * 5) * math.sin(math.radians(angle_lancer))
            pygame.draw.line(ecran, config.BLANC, (dechet['x'], dechet['y']), (fx, fy), 2)

        # Dessin du déchet
        pygame.draw.circle(ecran, dechet['couleur'], (int(dechet['x']), int(dechet['y'])), dechet['rayon'])

        # Affichage du Panneau d'informations
        pygame.draw.rect(ecran, (255, 255, 255, 150), (10, 10, 250, 130))  # Fond blanc transparent
        ecran.blit(police_p.render(f"Lieu: {niveau['nom']}", True, config.NOIR), (20, 20))
        ecran.blit(police_p.render(f"Score: {score}/{niveau['score_cible']} | Vies: {vies}", True, config.NOIR),
                   (20, 50))
        ecran.blit(police_p.render(
            f"Vent: {'<-- ' if niveau['vent'] < 0 else '--> ' if niveau['vent'] > 0 else 'Nul'}{abs(niveau['vent'])}",
            True, config.BLEU), (20, 80))
        ecran.blit(police_m.render(f"OBJET: {dechet['type']}", True, dechet['couleur']), (20, 105))

        # Jauge de force: Barre orange en haut à droite
        pygame.draw.rect(ecran, config.NOIR, (600, 20, 150, 15), 2)
        pygame.draw.rect(ecran, (255, 140, 0), (600, 20, (force_lancer / 25) * 150, 15))
        ecran.blit(police_p.render("FORCE", True, config.NOIR), (650, 40))

        # Affichage des messages temporaires
        if timer_alerte > 0:
            color = config.VERT if "BIEN" in message_alerte or "NIVEAU" in message_alerte else config.ROUGE
            t_surface = police_m.render(message_alerte, True, color)
            ecran.blit(t_surface, (config.LARGEUR // 2 - t_surface.get_width() // 2, 280))
            timer_alerte -= 1  # Réduit le temps restant pour l'affichage

    # Écrans de fin: Victoire et Défaite
    elif etat_jeu == 'GAMEOVER':
        ecran.fill((40, 0, 0))
        t_msg = police_g.render("GAME OVER", True, config.ROUGE)
        ecran.blit(t_msg, (config.LARGEUR // 2 - t_msg.get_width() // 2, 200))
        ecran.blit(police_p.render("Appuyez sur 'R' pour recommencer", True, config.BLANC), (240, 350))

    elif etat_jeu == 'VICTOIRE':
        ecran.fill((0, 40, 0))
        t_msg = police_g.render("PLANÈTE SAUVÉE !", True, config.VERT)
        ecran.blit(t_msg, (config.LARGEUR // 2 - t_msg.get_width() // 2, 200))
        ecran.blit(police_p.render("Appuyez sur 'R' pour rejouer", True, config.BLANC), (270, 350))

    pygame.display.flip()  # Met à jour tout l'écran avec ce qu'on a dessiné
    horloge.tick(config.FPS)  # Attend le temps nécessaire pour rester à 60 FPS

pygame.quit()