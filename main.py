import asyncio
import pygame
import random 

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
gravity = 1
sim_speed = 1
particle_r = 10
drag_power = 0.05
sense_dist = 25
point_inr = -1
points = []

class point:

    def __init__(self, x, y, fric, color, mass, elast):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 10
        self.fric = fric
        self.color = color
        self.mass = mass
        self.elasticity = elast

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
        self.vx *= (1 - self.fric) ** sim_speed
        self.vy *= (1 - self.fric) ** sim_speed
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

def test_setup(count):
    for i in range(count):
        points.append(point(random.randint(round(-game_width / 2), round(game_width / 2)), 0, 0.02, (155, 155, 155), 1, 0.7))

def points_av():
    for i in points:
        i.apply_velocity()

def draw_all():
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
    mindist = min(dists)
    if mindist <= sense_dist:
        point_inr = dists.index(mindist)
    
test_setup(50)

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