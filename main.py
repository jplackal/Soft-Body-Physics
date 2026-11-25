import asyncio
import pygame
import random 
import math

pygame.init()

WIDTH = 1300
HEIGHT = 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Soft Body Physics")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 50)
running = True

alpha = 255
text = font.render("", True, (255, 255, 255)).convert_alpha()
text.set_alpha(alpha)
#screen.blit(text, (100, 550))

cam_x = 0
cam_y = 0
game_width = WIDTH
game_height = HEIGHT
gravity = 0.2
sim_speed = 1
particle_r = 10
drag_power = 0.05
sense_dist = 25
point_inr = -1
speed_cap = 500
points = []
lines = []

class point:

    def __init__(self, x, y, fric, color, mass, elast, locked):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.fric = fric
        self.color = color
        self.mass = mass
        self.elasticity = elast
        self.locked = locked

    def draw(self, id):
        global cam_x, cam_y, point_inr
        if id == point_inr:
            pygame.draw.circle(screen, (255,255,255), (round(self.x + cam_x + (WIDTH / 2)),round((- self.y) + cam_y + (HEIGHT / 2))), particle_r+2)
        pygame.draw.circle(screen, self.color, (round(self.x + cam_x + (WIDTH / 2)),round((- self.y) + cam_y + (HEIGHT / 2))), particle_r)

    def bounce(self):
        if not - (game_width / 2 - particle_r) < self.x < (game_width / 2 - particle_r):
            self.x = (abs(self.x) / self.x) * (game_width / 2 - particle_r)
            self.vx *= -1 * self.elasticity
        if not - (game_height / 2 - particle_r) < self.y < (game_height / 2 - particle_r):
            self.y = (abs(self.y) / self.y) * (game_height / 2 - particle_r)
            self.vy *= -1 * self.elasticity

    def apply_velocity(self):
        if not self.locked == 1:
            self.vx *= (1 - self.fric) ** sim_speed
            self.vy *= (1 - self.fric) ** sim_speed
            cspeed = ((self.vx ** 2) + (self.vy ** 2))
            if cspeed > speed_cap ** 2:
                self.vx *= (speed_cap ** 2) / cspeed
                self.vy *= (speed_cap ** 2) / cspeed
            self.x += self.vx * sim_speed
            self.y += self.vy * sim_speed
            self.bounce()
            self.vy -= 1 * gravity * sim_speed

    def drag_point(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x = mouse_x - cam_x - WIDTH/2
        world_y = - (mouse_y - cam_y - HEIGHT/2)
        dx = world_x - self.x
        dy = world_y - self.y
        self.vx += dx * drag_power
        self.vy += dy * drag_power

    def in_range(self, id):
        global point_inr, sense_dist
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x = mouse_x - cam_x - WIDTH/2
        world_y = - (mouse_y - cam_y - HEIGHT/2)
        dist = ((world_x - self.x) ** 2 + (world_y - self.y) ** 2)
        return dist**0.5

class spring:
    def __init__(self, start, end, stiffness, dampening, target_lenght):
        self.start = start
        self.end = end
        self.stiff = stiffness
        self.damp = dampening
        self.tlenght = target_lenght

    def draw(self):
        pygame.draw.line(screen, (255, 255, 255), (self.start.x+cam_x+(WIDTH/2), -self.start.y+cam_y+(HEIGHT/2)), (self.end.x+cam_x+(WIDTH/2), -self.end.y+cam_y+(HEIGHT/2)), 3)

    def calculate(self):
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        dist = ((dx ** 2) + (dy ** 2))**0.5
        if dist == 0:
            nx = 0
            ny = 0
        else:
            nx = dx/dist
            ny = dy/dist
        extension = dist - self.tlenght
        f = self.stiff * extension
        rvx = self.end.vx - self.start.vx
        rvy = self.end.vy - self.start.vy
        rspeed = ((rvx * nx) + (rvy * ny))
        df = self.damp * rspeed
        ft = df + f
        ftx = ft * nx
        fty = ft * ny
        if not self.start.locked == 1:
            self.start.vx += ftx / self.start.mass
            self.start.vy += fty / self.start.mass
        if not self.end.locked == 1:
            self.end.vx -= (ftx / self.end.mass)
            self.end.vy -= (fty / self.end.mass)

def draw_polygon(points):
    points = list(points)
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    points.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    #pygame.draw.polygon(screen, (200, 200, 200), points)

def test_setup1(count):
    for i in range(count):
        points.append(point(random.randint(round(-game_width / 2), round(game_width / 2)), 0, 0.02, (155, 155, 155), 1, 0.7, 0))
        for i2 in range(len(points)):
            if i != i2:
                lines.append(spring(points[i], points[i2], 0.4, 0.05, 100))

def test_setup2(x, y):
    for i in range(x):
        for i2 in range(y):
            if i == 0 or i == x - 1:
                points.append(point((i * 50) - ((x-1) * 25), i2 * 50 - ((y-1) * 25), 0, (155, 155, 155), 1, 1, 1))
            else:
                points.append(point((i * 50) - ((x-1) * 25), i2 * 50 - ((y-1) * 25), 0, (155, 155, 155), 1, 1, 0))
    for i in points:
        for i2 in points:
            if i != i2:
                dist = ((i.x - i2.x) ** 2 + (i.y - i2.y) ** 2)
                if dist <= 99**2:
                    lines.append(spring(i, i2, 0.2, 0.1, (dist ** 0.5)))

def points_av():
    for i in lines:
        i.calculate()
    for i in points:
        i.apply_velocity()

def draw_all():
    draw_polygon([i.x + cam_x + WIDTH/2, - i.y + cam_y + HEIGHT/2] for i in points)
    for i in lines:
        i.draw()
    for id, i in enumerate(points):
        i.draw(id)
    if point_inr != -1:
        points[point_inr].draw(point_inr)

def ir_all():
    global point_inr
    point_inr = -1
    dists = []
    for id, i in enumerate(points):
        dists.append(i.in_range(id))
    if points == []:
        return
    mindist = min(dists)
    if mindist <= sense_dist:
        point_inr = dists.index(mindist)
    
test_setup2(20, 2)

async def main():

    global running, dt

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            #elif event.type == pygame.KEYDOWN:

                #if event.key == pygame.K_SPACE:
                    #pass

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    ir_all()

        screen.fill((0,0,0))
        points_av()
        if  not (pygame.mouse.get_pressed()[0] and point_inr != -1):
            ir_all()
        else:
            points[point_inr].drag_point()
        draw_all()
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())