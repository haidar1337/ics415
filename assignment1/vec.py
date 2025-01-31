class Vec:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def dot(self, vec):
        return self.x * vec.x + self.y * vec.y + self.z * vec.z
    
    def sub(self, vec):
        return Vec(self.x - vec.x, self.y - vec.y, self.z - vec.z)
    
    def add(self, vec):
        return Vec(self.x + vec.x, self.y + vec.y, self.z + vec.z)
    
    def mul(self, num):
        return Vec(self.x * num, self.y * num, self.z * num)
    
    def div(self, num):
        return Vec(self.x / num, self.y / num, self.z / num)
    
    def length(self):
        from math import sqrt
        return sqrt(self.x**2 + self.y**2 + self.z**2)