class Sphere:
    def __init__(self, center, radius, color, specular=0, reflective=0, material=""):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular
        self.reflective = reflective
        self.material = material
