def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
    import board
    import neopixel
    import re
    import math
    
    # You are welcome to add any of these:
    import random
    # import numpy
    # import scipy
    # import sys
    
    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])
    
    # IMPORT THE COORDINATES (please don't break this bit)
    
    coordfilename = "Python/coords.txt"
	
    fin = open(coordfilename,'r')
    coords_raw = fin.readlines()
    
    coords_bits = [i.split(",") for i in coords_raw]
    
    coords = []
    
    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]','', i)))
        coords.append(new_coord)
    
    #set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords) # this should be 500
    
    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)
    
    
    # YOU CAN EDIT FROM HERE DOWN
    
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
    
    #rules for the game. first array gives the number of cells required for a dead cell to become alive
    #second array gives the number of active cells required for a living cell to stay alive
    rules = [[3], [2,3]] 
    dist_threshhold = 100 #distance within another light/cells counts as neighbor
    game = Game(coords, rules, dist_threshhold)

    slow = 0
    delta = 0
    delta_per_cycle = 0.05 #change this for faster/slower animation

    MAX_RGB_VAL = 60

    def get_color_simple(index):
        b = int(game.active_coords[index] * MAX_RGB_VAL * (1.0 - delta) + game.next_active[index] * MAX_RGB_VAL * delta)
        return [b, b, b]


    def get_color_with_transition(index):
        if game.active_coords[index]:
            if game.next_active[index]:
                return [MAX_RGB_VAL, MAX_RGB_VAL, MAX_RGB_VAL]
            else:
                red = int(MAX_RGB_VAL * (1.0 - delta))
                gb = int(MAX_RGB_VAL * (1.0 - delta * 2))
                if delta > 0.5:
                    return [0, red, 0]
                else:
                    return [gb, red, gb]
        elif game.next_active[index]:
            green = int(MAX_RGB_VAL * delta * 2)
            rb = int(MAX_RGB_VAL * delta)
            if delta > 0.5:
                return [MAX_RGB_VAL, rb, rb]
            else:
                return [green, rb, rb]
        else:
            return [0, MAX_RGB_VAL // 30, MAX_RGB_VAL // 10]


    # yes, I just run which run is true
    run = 1
    while run == 1:
        time.sleep(slow)
        
        LED = 0
        while LED < len(coords):
            pixels[LED] = get_color_with_transition(LED)
            #use next line for a simple transition instead
            #pixels[LED] = get_color_simple(LED)
            LED += 1
        
        # use the show() option as rarely as possible as it takes ages
        # do not use show() each time you change a LED but rather wait until you have changed them all
        pixels.show()
        
        # now we get ready for the next cycle
        delta += delta_per_cycle

        if delta > 1.0:
            game.next_life_cycle()
            delta = 0.0
        
    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
