from engine.camera import Camera
import pygame
import glm

class Player:
    def __init__(self):
        self.camera = Camera((0, 1.5, 0))
        self.speed = 0.1
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        mouse_dx, mouse_dy = pygame.mouse.get_rel()

        self.camera.yaw += mouse_dx * 0.1
        self.camera.pitch -= mouse_dy * 0.1

        self.camera.pitch = max(-89, min(89, self.camera.pitch))

        forward = glm.vec3(
            glm.cos(glm.radians(self.camera.yaw)) * glm.cos(glm.radians(self.camera.pitch)),
            0,
            glm.sin(glm.radians(self.camera.yaw)) * glm.cos(glm.radians(self.camera.pitch)),
        )
        right = glm.cross(forward, glm.vec3(0, 1, 0))

        if keys[pygame.K_w]:
            self.camera.position += glm.normalize(forward) * self.speed
        if keys[pygame.K_s]:
            self.camera.position -= glm.normalize(forward) * self.speed
        if keys[pygame.K_a]:
            self.camera.position -= glm.normalize(right) * self.speed
        if keys[pygame.K_d]:
            self.camera.position += glm.normalize(right) * self.speed

    def get_direction(self):
        return glm.normalize(glm.vec3(
            glm.cos(glm.radians(self.camera.yaw)) * glm.cos(glm.radians(self.camera.pitch)),
            glm.sin(glm.radians(self.camera.pitch)),
            glm.sin(glm.radians(self.camera.yaw)) * glm.cos(glm.radians(self.camera.pitch))
        ))

