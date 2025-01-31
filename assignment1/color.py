class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    
    def mul(self, num):
        return Color(self.r * num, self.g * num, self.b * num)