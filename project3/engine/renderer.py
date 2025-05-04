from OpenGL.GL import *
from OpenGL.GLU import *
import glm

class Renderer:
    def __init__(self):
        glClearColor(0.5, 0.7, 1.0, 1.0)  # Light blue sky
        glEnable(GL_DEPTH_TEST)
        self.set_projection(800, 600)

    def set_projection(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70.0, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def render(self, world, player):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Set up camera view
        view_matrix = player.camera.get_view_matrix()
        glLoadMatrixf(sum(view_matrix.to_list(), []))

        # Draw all blocks
        for block in world.blocks.values():
            for explosion in world.explosions:
                for p in explosion.particles:
                    self.draw_particle(p[0])
            self.draw_block(block.position)

    def draw_particle(self, pos):
        x, y, z = pos
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.5, 0.0)  # Orange fire
        self.draw_particle_cube()
        glPopMatrix()


    def draw_block(self, pos):
        x, y, z = pos
        glPushMatrix()
        glTranslatef(x, y, z)
        glBegin(GL_QUADS)

        # Green grass-like color
        glColor3f(0.3, 0.8, 0.3)

        # Front
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        glVertex3f(1, 1, 0)
        glVertex3f(0, 1, 0)

        # Back
        glVertex3f(0, 0, -1)
        glVertex3f(1, 0, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(0, 1, -1)

        # Left
        glVertex3f(0, 0, -1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1, 0)
        glVertex3f(0, 1, -1)

        # Right
        glVertex3f(1, 0, 0)
        glVertex3f(1, 0, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(1, 1, 0)

        # Top
        glVertex3f(0, 1, 0)
        glVertex3f(1, 1, 0)
        glVertex3f(1, 1, -1)
        glVertex3f(0, 1, -1)

        # Bottom
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        glVertex3f(1, 0, -1)
        glVertex3f(0, 0, -1)

        glEnd()
        glPopMatrix()

    def draw_particle_cube(self):
        glBegin(GL_QUADS)
        for face in self.cube_faces():  # ← this must be inside a method
            glColor3f(1.0, 0.5, 0.0)
            for vertex in face:
                glVertex3f(vertex[0]*0.1, vertex[1]*0.1, vertex[2]*0.1)
        glEnd()

    def cube_faces(self):
        return [
            [(0,0,0),(1,0,0),(1,1,0),(0,1,0)],  # back
            [(1,0,0),(1,0,1),(1,1,1),(1,1,0)],  # right
            [(0,0,1),(1,0,1),(1,1,1),(0,1,1)],  # front
            [(0,0,0),(0,0,1),(0,1,1),(0,1,0)],  # left
            [(0,1,0),(1,1,0),(1,1,1),(0,1,1)],  # top
            [(0,0,0),(1,0,0),(1,0,1),(0,0,1)],  # bottom
        ]
