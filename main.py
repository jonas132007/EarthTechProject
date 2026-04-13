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
    {'nom': 'Plage', 'ciel_haut': config.CIEL_PLAGE_HAUT, 'ciel_bas': config.CIEL_PLAGE_BAS, 'sol': config.SOL_PLAGE, 'vent': 0.0, 'gravite': 0.5, 'score_cible': 3,
     'obstacle': False, 'decor_type': 'nuages'},
    {'nom': 'Foret', 'ciel_haut': config.CIEL_FORET_HAUT, 'ciel_bas': config.CIEL_FORET_BAS, 'sol': config.SOL_FORET, 'vent': -0.1, 'gravite': 0.5, 'score_cible': 6,
     'obstacle': False, 'decor_type': 'nuages'},
    {'nom': 'Ocean', 'ciel_haut': config.CIEL_OCEAN_HAUT, 'ciel_bas': config.CIEL_OCEAN_BAS, 'sol': config.SOL_OCEAN, 'vent': 0.25, 'gravite': 0.6,
     'score_cible': 10, 'obstacle': True, 'decor_type': 'bulles'}
]

def dessiner_degrade(surface, haut, bas):
    """Dessine un dégradé vertical sur toute la surface"""
    for y in range(config.HAUTEUR):
        facteur = y / config.HAUTEUR
        r = int(haut[0] * (1 - facteur) + bas[0] * facteur)
        g = int(haut[1] * (1 - facteur) + bas[1] * facteur)
        b = int(haut[2] * (1 - facteur) + bas[2] * facteur)
        pygame.draw.line(surface, (r, g, b), (0, y), (config.LARGEUR, y))

particules = []
decor_bg = []

def init_decor(type_decor):
    decor_bg.clear()
    for _ in range(15):
        if type_decor == 'nuages':
            decor_bg.append({'x': random.randint(0, config.LARGEUR), 'y': random.randint(50, 300), 'vitesse': random.uniform(0.1, 0.4), 'taille': random.randint(40, 90)})
        elif type_decor == 'bulles':
            decor_bg.append({'x': random.randint(0, config.LARGEUR), 'y': random.randint(0, config.HAUTEUR), 'vitesse': random.uniform(-1.5, -0.5), 'taille': random.randint(5, 12)})

def creer_particules(x, y, couleur, mode='trainee'):
    if mode == 'trainee':
        particules.append({'x': x, 'y': y, 'vx': random.uniform(-0.5, 0.5), 'vy': random.uniform(-0.5, 0.5), 'vie': 20, 'couleur': couleur, 'taille': 4})
    elif mode == 'explosion':
        for _ in range(25):
            particules.append({'x': x, 'y': y, 'vx': random.uniform(-5, 5), 'vy': random.uniform(-10, 2), 'vie': random.randint(30, 60), 'couleur': random.choice([couleur, config.BLANC, config.ORANGE, config.JAUNE]), 'taille': random.randint(3, 8)})
    elif mode == 'mega_explosion':
        # giga feu d'artifice de victoire !! 😎
        for _ in range(120):
            couleur_rand = random.choice([config.VERT, config.BLEU, config.JAUNE, config.BLANC, config.ORANGE, (255, 100, 200)])
            particules.append({'x': x, 'y': y, 'vx': random.uniform(-15, 15), 'vy': random.uniform(-15, 15), 'vie': random.randint(40, 80), 'couleur': couleur_rand, 'taille': random.randint(5, 15)})

def dessiner_texte_ombre(surface, texte, police, couleur, x, y, ombre_couleur=(0,0,0), decalage=2):
    t_ombre = police.render(texte, True, ombre_couleur)
    surface.blit(t_ombre, (x + decalage, y + decalage))
    t_clair = police.render(texte, True, couleur)
    surface.blit(t_clair, (x, y))

def dessiner_dechet(surface, t_dechet, x, y):
    # # petite fonction de dessin pour modéliser nos déchets avec style ! (surface Alpha pr pouvoir superposer)
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    if t_dechet == 'Plastique':
        # notre best bouteille d'eau: corps + goulot fin + etiquette bleue + bouchon orange par dessus
        pygame.draw.rect(surf, config.JAUNE, (6, 12, 18, 18), border_radius=4)
        pygame.draw.rect(surf, config.JAUNE, (11, 6, 8, 6))
        pygame.draw.rect(surf, config.ORANGE, (10, 3, 10, 4), border_radius=1) # le pti bouchon lol
        pygame.draw.rect(surf, config.BLEU, (6, 16, 18, 6))
    elif t_dechet == 'Papier':
        # boule de papier froissé (je ruse grave en empilant des ptis cercles randoms)
        pygame.draw.circle(surf, config.BLEU, (15, 15), 11)
        pygame.draw.circle(surf, (200, 220, 255), (12, 12), 7)
        pygame.draw.circle(surf, (150, 180, 220), (18, 17), 5)
        # fausses traces de stylo gribouillées
        pygame.draw.line(surf, config.NOIR, (10, 10), (18, 20), 2)
        pygame.draw.line(surf, config.NOIR, (12, 20), (16, 12), 2)
    elif t_dechet == 'Verre':
        # pitite teille de verre verte bien stylée style soda
        pygame.draw.rect(surf, config.VERT, (5, 13, 20, 17), border_radius=3)
        pygame.draw.rect(surf, config.VERT, (11, 2, 8, 11))
        # un pti trait d'ellipse oklm pr faire effet brillance 
        pygame.draw.ellipse(surf, (150, 255, 150), (7, 15, 4, 10))
        # l'etiquette vièrge en plein centre
        pygame.draw.rect(surf, (200, 200, 200), (5, 18, 20, 8))
        
    # on pop notre dessin giga lourd au beau milieu des coords
    surface.blit(surf, (int(x - 15), int(y - 15)))

# On initialise le décor de base
init_decor(niveaux[0]['decor_type'])

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
                    init_decor(niveaux[index_niveau]['decor_type'])
                    particules.clear()

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

            # Traînée de particules
            creer_particules(dechet['x'], dechet['y'], config.BLANC, 'trainee')

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
                        creer_particules(p['x'] + p['largeur']//2, p['y'], p['couleur'], 'explosion')
                    else:  # Mauvaise poubelle !
                        vies -= 1
                        message_alerte = f"NON ! C'était du {dechet['type']}"

                    timer_alerte = 90
                    dechet = creer_nouveau_dechet()

                    if vies <= 0:
                        etat_jeu = 'GAMEOVER'
                    elif score >= niveau['score_cible']:  # Niveau terminé ?
                        if index_niveau < len(niveaux) - 1:
                            # on lance la phase d'animation avant le prochain niveau
                            etat_jeu = 'TRANSITION'
                            timer_alerte = 120 # anim d'environ 2 sec pr kiffer l'explo
                            # ptite explosion épique de réussite au milieu de l'écran !!
                            creer_particules(config.LARGEUR//2, config.HAUTEUR//2, config.BLANC, 'mega_explosion')
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

    # ptite gestion pour faire passer le temps de l'anim sans que le mec joue
    elif etat_jeu == 'TRANSITION':
        timer_alerte -= 1
        # l'anim est finie du coup hop on switch la data
        if timer_alerte <= 0:
            index_niveau += 1
            score = 0
            etat_jeu = 'JEU'
            dechet = creer_nouveau_dechet()
            init_decor(niveaux[index_niveau]['decor_type'])

    #  AFFICHAGE (Dessin sur l'écran)
    if etat_jeu == 'MENU':
        ecran.fill(config.NOIR)
        t_titre = police_g.render("ECO THROW", True, config.VERT)
        ecran.blit(t_titre, (config.LARGEUR // 2 - t_titre.get_width() // 2, 150))
        ecran.blit(police_m.render("Appuyez sur ENTREE pour jouer", True, config.BLANC), (180, 300))

    # on continue de recréer l'image chaque ms pour faire bouger l'explo même en pause
    elif etat_jeu in ['JEU', 'TRANSITION']:
        # Animation et affichage des particules de fond (nuages/bulles)
        for d in decor_bg:
            if niveau['decor_type'] == 'nuages':
                d['x'] += d['vitesse']
                if d['x'] > config.LARGEUR + 100: d['x'] = -100
            elif niveau['decor_type'] == 'bulles':
                d['y'] += d['vitesse']
                if d['y'] < -20: d['y'] = config.HAUTEUR + 20

        # Maj Particules
        for p in particules[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vie'] -= 1
            if p['vie'] <= 0:
                particules.remove(p)

        # Dessin de l'environnement (Ciel et Sol) avec Dégradé
        dessiner_degrade(ecran, niveau['ciel_haut'], niveau['ciel_bas'])
        
        # design visuel propre selon mon niveau
        
        if niveau['nom'] == 'Plage':
            # mon gros soleil jaune pr la plage !!
            pygame.draw.circle(ecran, (255, 204, 0), (650, 150), 60)
            # faux rayon de lumière avec un bord large (le fameux 4 de la fin)
            pygame.draw.circle(ecran, (255, 140, 0), (650, 150), 75, 4)
            # la bande d'eau basique derriere
            pygame.draw.rect(ecran, (0, 119, 190), (0, 480, 800, 40))

        elif niveau['nom'] == 'Foret':
            # j'ai mis 4 arbres de base avec un petit decallage entre
            for x_arbre in [80, 250, 580, 750]:
                # un vrai tronc rectangulaire mdrrr
                pygame.draw.rect(ecran, (139, 69, 19), (x_arbre, 450, 20, 70))
                # bas du sapin avec un polyg (3 coins)
                pygame.draw.polygon(ecran, (34, 100, 34), [(x_arbre - 40, 460), (x_arbre + 60, 460), (x_arbre + 10, 350)])
                # et le dessus du sapin un poil plus clair 
                pygame.draw.polygon(ecran, (50, 120, 50), [(x_arbre - 30, 410), (x_arbre + 50, 410), (x_arbre + 10, 320)])

        # on affiche les ptis nuages decoratif fixe bg
        for d in decor_bg:
            if niveau['decor_type'] == 'nuages':
                # des ronds etirés = nuage du gouv... lol
                pygame.draw.ellipse(ecran, (255, 255, 255), (int(d['x']), int(d['y']), int(d['taille']*2), int(d['taille'])))
            elif niveau['decor_type'] == 'bulles':
                # ptite ellipse vide = ptite bulle sous l'eau
                pygame.draw.circle(ecran, (255, 255, 255), (int(d['x']), int(d['y'])), d['taille'], 1)

        # block solide du bas (terre etc..)
        pygame.draw.rect(ecran, niveau['sol'], (0, 520, 800, 80))
        # je force la limite pr detacher visuellement... ca donne bien
        pygame.draw.line(ecran, (0,0,0), (0, 520), (800, 520), 4)

        # boucle d'anim pr les particules qui volent pdt les lancés
        for p in particules:
            # on triche sur le radius en testant son age (vie / 30 * taille ini)
            t = max(1, int(p['taille'] * (p['vie'] / 30)))
            pygame.draw.circle(ecran, p['couleur'], (int(p['x']), int(p['y'])), t)

        # Dessin de la mouette animée (si présente)
        if niveau['obstacle']:
            battement = math.sin(pygame.time.get_ticks() / 100) * 15
            # Ombre au sol (faké pour l'effet de hauteur)
            pygame.draw.ellipse(ecran, (0, 0, 0, 50), (oiseau['x'] + 10, oiseau['y'] + 50, oiseau['largeur'], oiseau['hauteur'] // 2))
            # Corps
            pygame.draw.ellipse(ecran, (240, 240, 240), (oiseau['x'], oiseau['y'], oiseau['largeur'], oiseau['hauteur']))
            # Ailes animées
            pygame.draw.line(ecran, config.NOIR, (oiseau['x'] + 10, oiseau['y'] + 15), (oiseau['x'] - 20, oiseau['y'] + battement), 4)
            pygame.draw.line(ecran, config.NOIR, (oiseau['x'] + oiseau['largeur'] - 10, oiseau['y'] + 15), (oiseau['x'] + oiseau['largeur'] + 20, oiseau['y'] + battement), 4)
            dessiner_texte_ombre(ecran, "MOUETTE !", police_p, config.ROUGE, oiseau['x'], oiseau['y'] - 30)

        # ---- Dessin de nos superbes poubelles urbaines -----
        # un gros calque unique pr pouvoir utiliser le transp/SRCALPHA pépère (pr les ombres !)
        calque_poubelles = pygame.Surface((config.LARGEUR, config.HAUTEUR), pygame.SRCALPHA)
        for p in poubelles:
            # 1. Grosse ombre derrière pour l'effet volume incrrr
            pygame.draw.rect(calque_poubelles, (0, 0, 0, 100), (p['x'] + 10, p['y'] + 10, p['largeur'], p['hauteur']), border_radius=8)
            # 2. Le Bidon massif en block avec ses vraies couleurs
            pygame.draw.rect(calque_poubelles, p['couleur'], (p['x'], p['y'], p['largeur'], p['hauteur']), border_radius=8)
            # 3. Traits noircis pour les rayures du bidon (ça fait vraiment poubelle de parc commça)
            for x_ray in [20, 35, 50]:
                pygame.draw.line(calque_poubelles, (0, 0, 0, 60), (p['x'] + x_ray, p['y'] + 25), (p['x'] + x_ray, p['y'] + p['hauteur'] - 15), 4)
            # 4. Le gros couvercle gris du haut de la teille, qui depasse
            pygame.draw.rect(calque_poubelles, (70, 70, 70), (p['x'] - 5, p['y'] - 10, p['largeur'] + 10, 20), border_radius=6)
            pygame.draw.rect(calque_poubelles, (200, 200, 200), (p['x'] - 5, p['y'] - 10, p['largeur'] + 10, 5), border_radius=6) # petit effet sun glare en plus
            # 5. Bordure de protection en noir stylisé
            pygame.draw.rect(calque_poubelles, config.NOIR, (p['x'], p['y'], p['largeur'], p['hauteur']), 3, border_radius=8)
            pygame.draw.rect(calque_poubelles, config.NOIR, (p['x'] - 5, p['y'] - 10, p['largeur'] + 10, 20), 2, border_radius=6)
            
        # blit de notre master piece sur le canvas
        ecran.blit(calque_poubelles, (0,0))
        
        # Et un pti ajout textuel sympa pr chaque back pour qu'on sache quoi y jeter ^^
        for p in poubelles:
            txt_surface = police_p.render(p['type'], True, config.BLANC)
            txt_w = txt_surface.get_width()
            dessiner_texte_ombre(ecran, p['type'], police_p, config.BLANC, p['x'] + p['largeur'] // 2 - txt_w // 2, p['y'] + 45)

        # Dessin de la trajectoire de visée (avant le lancer jte dis pas pk)
        if not dechet['en_vol']:
            sim_x, sim_y = dechet['x'], dechet['y']
            sim_vx, sim_vy = physique.calculer_vitesse_initiale(force_lancer, angle_lancer)
            # jui balance 150 frames de calcul de physics pr prevoir sa trajec !!!
            for i in range(150): 
                sim_x, sim_y, sim_vx, sim_vy = physique.mettre_a_jour_position(sim_x, sim_y, sim_vx, sim_vy, niveau['gravite'], niveau['vent'])
                if i % 4 == 0:
                    pygame.draw.circle(ecran, (255, 255, 255, 180), (int(sim_x), int(sim_y)), 3)
                # ptite securité si la boule hit le bord pr eviter de la crash loins mdddr
                if sim_y > 600 or sim_x > 800 or sim_x < 0:
                    break

        # Dessin full custom de nos dechet HD au lieu des vielles boules
        dessiner_dechet(ecran, dechet['type'], dechet['x'], dechet['y'])

        # UI Glassmorphism (Panneau d'informations)
        panneau = pygame.Surface((260, 140), pygame.SRCALPHA)
        pygame.draw.rect(panneau, (0, 0, 0, 140), (0, 0, 260, 140), border_radius=15)
        pygame.draw.rect(panneau, (255, 255, 255, 50), (0, 0, 260, 140), 2, border_radius=15)
        ecran.blit(panneau, (10, 10))
        
        dessiner_texte_ombre(ecran, f"Lieu: {niveau['nom']}", police_p, config.BLANC, 20, 20)
        dessiner_texte_ombre(ecran, f"Score: {score}/{niveau['score_cible']} | Vies: {vies}", police_p, config.BLANC, 20, 50)
        
        vent_color = (150, 200, 255) if niveau['vent'] != 0 else (200, 200, 200)
        dessiner_texte_ombre(ecran, f"Vent: {'<-- ' if niveau['vent'] < 0 else '--> ' if niveau['vent'] > 0 else 'Nul '}{abs(niveau['vent']):.2f}", police_p, vent_color, 20, 80)
        dessiner_texte_ombre(ecran, f"OBJET: {dechet['type']}", police_m, dechet['couleur'], 20, 105)

        # Jauge de force dynamique
        jauge_couleur = config.VERT if force_lancer <= 10 else config.ORANGE if force_lancer <= 20 else config.ROUGE
        pygame.draw.rect(ecran, (50, 50, 50), (590, 15, 170, 25), border_radius=12)
        # La barre intérieure est la couleur de jauge
        largeur_barre = max(5, (force_lancer / 25) * 150)
        pygame.draw.rect(ecran, jauge_couleur, (600, 20, largeur_barre, 15), border_radius=8)
        dessiner_texte_ombre(ecran, "FORCE", police_p, config.BLANC, 645, 45)

        # Affichage des messages temporaires Pop-Up
        if timer_alerte > 0 and etat_jeu == 'JEU':
            color = config.VERT if "BIEN" in message_alerte or "NIVEAU" in message_alerte else config.ROUGE
            t_surface = police_g.render(message_alerte, True, color)
            txt_w = t_surface.get_width()
            
            # Encadré derrière le popup
            bg_rect = pygame.Surface((txt_w + 40, 80), pygame.SRCALPHA)
            pygame.draw.rect(bg_rect, (0, 0, 0, 180), (0, 0, txt_w + 40, 80), border_radius=20)
            ecran.blit(bg_rect, (config.LARGEUR // 2 - txt_w // 2 - 20, 260))
            
            dessiner_texte_ombre(ecran, message_alerte, police_g, color, config.LARGEUR // 2 - txt_w // 2, 270)
            timer_alerte -= 1

        # affichage final animé qd le prchain niveau pop !
        if etat_jeu == 'TRANSITION':
            # fondu sympa pr assombrir le background = beau contraste !!
            voile = pygame.Surface((config.LARGEUR, config.HAUTEUR), pygame.SRCALPHA)
            pygame.draw.rect(voile, (0, 0, 0, 150), (0,0,config.LARGEUR,config.HAUTEUR))
            ecran.blit(voile, (0,0))
            
            txt = "NIVEAU RÉSOLU !"
            t_surface = police_g.render(txt, True, config.JAUNE)
            x_txt = config.LARGEUR // 2 - t_surface.get_width() // 2
            # fait monter doucement le texte grace à mon timer hehe 
            y_txt = 250 - (120 - timer_alerte)
            dessiner_texte_ombre(ecran, txt, police_g, config.JAUNE, x_txt, y_txt, decalage=4)

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