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
    
    def cross(self, vec):
        """
        Computes the cross product of self with another vector.
        The cross product is defined as:
            self x vec = (self.y * vec.z - self.z * vec.y,
                          self.z * vec.x - self.x * vec.z,
                          self.x * vec.y - self.y * vec.x)
        """
        x = self.y * vec.z - self.z * vec.y
        y = self.z * vec.x - self.x * vec.z
        z = self.x * vec.y - self.y * vec.x
        return Vec(x, y, z)
    
    def normalize(self):
        """
        Returns a normalized (unit length) vector in the same direction.
        Raises a ValueError if the vector has zero length.
        """
        l = self.length()
        if l == 0:
            raise ValueError("Cannot normalize a zero-length vector")
        return self.div(l)
