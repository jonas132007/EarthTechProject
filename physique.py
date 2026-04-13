import math

def calculer_vitesse_initiale(force, angle_degres):
    angle_rad = math.radians(angle_degres)
    vx = force * math.cos(angle_rad)
    vy = -force * math.sin(angle_rad)
    return vx, vy

def mettre_a_jour_position(x, y, vx, vy, gravite, vent):
    vy += gravite
    vx += vent

    x += vx
    y += vy
    return x, y, vx, vy

def verifier_collision(dechet_x, dechet_y, dechet_rayon, poubelle):
    if poubelle['x'] < dechet_x < poubelle['x'] + poubelle['largeur'] and poubelle['y'] < dechet_y < poubelle['y'] + poubelle['hauteur']:
        return True
    return False

def verifier_collision_obstacle(dechet_x, dechet_y, obstacle):
    if obstacle['x'] < dechet_x < obstacle['x'] + obstacle['largeur'] and obstacle['y'] < dechet_y < obstacle['y'] + obstacle['hauteur']:
        return True
    return False