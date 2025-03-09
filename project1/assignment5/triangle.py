class Triangle:
    def __init__(self, v0, v1, v2, color, specular, reflective):
        """
        v0, v1, v2: vertices (Vec objects)
        color: a Color object
        specular: specular exponent (for lighting calculations)
        reflective: reflection coefficient (float between 0 and 1)
        """
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.color = color
        self.specular = specular
        self.reflective = reflective
        self.edge1 = self.v1.sub(self.v0)
        self.edge2 = self.v2.sub(self.v0)
        self.normal = self.edge1.cross(self.edge2).normalize()