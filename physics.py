import math

def calculate_initial_velocity(force, angle_degrees):
    angle_rad = math.radians(angle_degrees)
    vx = force * math.cos(angle_rad)
    vy = -force * math.sin(angle_rad)
    return vx, vy

def update_position(x, y, vx, vy, gravity, wind):
    vy += gravity
    vx += wind

    x += vx
    y += vy
    return x, y, vx, vy

def check_collision(waste_x, waste_y, waste_radius, bin_item):
    if bin_item['x'] < waste_x < bin_item['x'] + bin_item['width'] and bin_item['y'] < waste_y < bin_item['y'] + bin_item['height']:
        return True
    return False

def check_obstacle_collision(waste_x, waste_y, obstacle):
    if obstacle['x'] < waste_x < obstacle['x'] + obstacle['width'] and obstacle['y'] < waste_y < obstacle['y'] + obstacle['height']:
        return True
    return False