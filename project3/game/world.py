import pygame
import glm
from engine.block import Block
from game.explosion import Explosion

class World:
    def __init__(self):
        self.blocks = {
            (0, 0, -5): Block((0, 0, -5))
        }
        self.explosions = []

    def update(self, player, events):
        direction = player.get_direction()
        hit, last_empty = self.raycast(player.camera.position, direction)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - destroy
                    if hit and hit in self.blocks:
                        del self.blocks[hit]
                        self.explosions.append(Explosion(hit))

                elif event.button == 3:  # Right click - place
                    if hit and last_empty and last_empty not in self.blocks:
                        self.blocks[last_empty] = Block(last_empty)

        # Update explosions
        self.explosions = [e for e in self.explosions if not e.is_done()]
        for explosion in self.explosions:
            explosion.update()


    def raycast(self, origin, direction, max_distance=6):
        pos = glm.vec3(origin)
        last_empty = None
        for _ in range(int(max_distance * 10)):
            block_pos = tuple(int(glm.floor(pos[i])) for i in range(3))
            if block_pos in self.blocks:
                return block_pos, last_empty
            last_empty = block_pos
            pos += direction * 0.1
        return None, None
