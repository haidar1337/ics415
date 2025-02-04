class BVHNode:
    def __init__(self, bbox_min, bbox_max, triangles=None, left=None, right=None):
        self.bbox_min = bbox_min
        self.bbox_max = bbox_max
        self.triangles = triangles  # Only for leaf nodes.
        self.left = left
        self.right = right
        self.is_leaf = (triangles is not None)