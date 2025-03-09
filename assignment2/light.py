class Light:
    def __init__(self, intensity):
        self.intensity = intensity

class PointLight(Light):
    def __init__(self, intensity, position):
        super().__init__(intensity=intensity)
        self.position = position  

class AmbientLight(Light):
    def __init__(self, intensity):
        super().__init__(intensity=intensity)

class DirectionalLight(Light):
    def __init__(self, intensity, direction):
        super().__init__(intensity=intensity)
        self.direction = direction