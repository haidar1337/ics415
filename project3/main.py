import pygame
from engine.renderer import Renderer
from game.world import World
from game.player import Player


pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()

renderer = Renderer()
world = World()
player = Player()

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    player.handle_input()          
    world.update(player, events)   
    renderer.render(world, player)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
