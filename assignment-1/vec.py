class Vec:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def dot(self, vec):
        return self.x * vec.x + self.y * vec.y + self.z * vec.z
    
    def sub(self, vec):
        return Vec(self.x - vec.x, self.y - vec.y, self.z - vec.z)