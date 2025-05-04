import glm

class Camera:
    def __init__(self, position):
        self.position = glm.vec3(position)
        self.pitch = 0.0
        self.yaw = -90.0

    def get_view_matrix(self):
        direction = glm.vec3(
            glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch)),
            glm.sin(glm.radians(self.pitch)),
            glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        )
        target = self.position + glm.normalize(direction)
        up = glm.vec3(0.0, 1.0, 0.0)
        return glm.lookAt(self.position, target, up)
