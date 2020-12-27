import pyglet
from pyglet.gl import *
from pyglet.window import key
import re
import random
import math


INCREMENT = 2.0

class Game:
    '''
    Parameters:\n
    coords:
    *List with 3d coordinates
    rules:
    *list with 2 arrays. First array gives the amount of active neighbors for a dead cell to become active. Second array gives the numbers for which an active cell stays active.
    neighbor_distance_threshhold: 
    *distance for which a coordinate given in coords counts a neighboring another cell
    '''
    def __init__(self, coords, rules, neighbor_distance_threshhold):
        self._conway_rules = rules

        self._neighbors = []
        for i in range(len(coords)):
            distances = {math.dist(coords[i], coords[other]):other for other in range(len(coords)) if other != i}
            cur_neighbors = [distances[key] for key in sorted(distances.keys()) if key < neighbor_distance_threshhold]
            self._neighbors.append(cur_neighbors)

        self.active_coords = []
        self.next_active = [random.random() < 0.25 for _ in coords]
        self.next_life_cycle()


    def _count_active_neighs(self, i):
        return sum(1 for x in self._neighbors[i] if self.next_active[x])


    def next_life_cycle(self):
        new_active = [self._count_active_neighs(i) in self._conway_rules[self.next_active[i]] for i in range(len(self.next_active))]

        self.active_coords = self.next_active
        self.next_active = new_active

class Window(pyglet.window.Window):
    xRotation = yRotation = 0  

    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)

        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST) 

        coordfilename = "coords.txt"
	
        fin = open(coordfilename,'r')
        coords_raw = fin.readlines()
        
        coords_bits = [i.split(",") for i in coords_raw]
        
        self.coords = []

        for slab in coords_bits:
            new_coord = []
            for i in slab:
                new_coord.append(int(re.sub(r'[^-\d]','', i)))
            self.coords.append(new_coord)

        rules = [[3], [2,3]]
        dist_threshhold = 100
        self.game = Game(self.coords, rules, dist_threshhold)
        self.delta = 0

        pyglet.clock.schedule(self.next_frame)

    def on_draw(self):
        self.clear()
        glPushMatrix()
        glRotatef(self.xRotation, 1, 0, 0)
        glRotatef(self.yRotation, 0, 1, 0)

        self.draw_cells()
        #self.draw_neighbors()

        glPopMatrix()

    def get_color(self, index):
        if self.game.active_coords[index]:
            if self.game.next_active[index]:
                return (155, 155, 155)
            else:
                r = int(155 * (1.0 - self.delta))
                gb = int(155 * (1.0 - self.delta * 2))
                if self.delta > 0.5:
                    return (r, 0, 0)
                else:
                    return (r, gb, gb)
        elif self.game.next_active[index]:
            g = int(155 * self.delta * 2)
            rb = int(155 * self.delta)
            if self.delta > 0.5:
                return (rb, 155, rb)
            else:
                return (rb, g, rb)
        else:
            return (10, 0, random.randint(30, 50))

    def get_color_simple(self, index):
        b = int(self.game.active_coords[index] * 155 * (1.0 - self.delta) + self.game.next_active[index] * 155 * self.delta)
        return (b, b, b)

    def draw_cells(self):
        glBegin(GL_QUADS)
        for i in range(len(self.coords)):
            r, g, b = self.get_color(i)
            glColor3ub(r, g, b)
            
            yinc = int(10 * ((self.yRotation % 180) / 90))
            xinc = int(10 * (1.0 - (self.yRotation % 180) / 90))

            x, y, z = self.coords[i]
            glVertex3i(x, z, y)
            glVertex3i(x, z - 10 , y)
            glVertex3i(x - xinc, z - 10 , y - yinc)
            glVertex3i(x - xinc, z , y  - yinc)
        glEnd()

    def draw_neighbors(self):
        glLineWidth(1.0)
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        for i in range(len(self.coords)):
            if self.game.active_coords[i]:
                x, y, z = self.coords[i]
                for other in self.game._neighbors[i]:
                    x2, y2, z2 = self.coords[other]
                    glVertex3i(x, z, y)
                    glVertex3i(x2, z2, y2)
        glEnd()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        gluPerspective(35, aspectRatio, 1, 4000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -2100)


    def next_frame(self, delta):
        self.delta += delta * 1.3

        if self.delta > 1.0:
            self.game.next_life_cycle()
            self.delta = 0.0

    def on_text_motion(self, motion):
        if motion == key.UP:
            self.xRotation -= INCREMENT
        elif motion == key.DOWN:
            self.xRotation += INCREMENT
        elif motion == key.LEFT:
            self.yRotation -= INCREMENT
        elif motion == key.RIGHT:
            self.yRotation += INCREMENT

            
if __name__ == '__main__':
    window = Window(800, 800, 'Game of life tree')
    pyglet.app.run()