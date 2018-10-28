import pygame
import sys,os
from pygame.locals import *
import pygame.image as im
import csv

here = os.path.dirname(os.path.abspath(__file__))
imgdir = os.path.join(here,'img')
leveldir = os.path.join(here,'levels')
directions = ['u','l','d','r']
tilesize = 40
fontfile = '/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf'
rgb_white = (255,255,255)
rgb_black = (0,0,0)

def rot(surf,uldr):
    """Rotate a surface. Assumes starts facing down

    Parameters
    ----------
    surf : pygame Surface
        thing to rotate
    uldr : str, ['u','l','d','r']
        direction to face
    """
    if uldr=='l':
        return pygame.transform.rotate(surf,-90)
    elif uldr=='r':
        return pygame.transform.rotate(surf,90)
    elif uldr=='u':
        return pygame.transform.rotate(surf,180)
    elif uldr=='d':
        return surf
    else:
        raise ValueError('%s is not u l d or r' % (uldr))

def check_if_code_is_alias(tile_code_or_alias):
    """Allow shorthand for some common codes

    Parameters
    ----------
    tile_code_or_alias : str
        valid texture+direction tile code
        OR
        code alias
    
    Returns
    -------
    tile_code
        [description]
    """

    aliases = {
            'x':'fld'
            }

    if tile_code_or_alias in aliases:
        tile_code = aliases[tile_code_or_alias]
    else:
        tile_code = tile_code_or_alias
    return tile_code

def name_direction_to_code(name,uldr):
    return name[:2]+uldr


class Player(object):
    def __init__(self,spritefn='character.png',x=0,y=0):
        self.spritefn = os.path.join(imgdir,spritefn)
        base_surf = im.load(self.spritefn).convert_alpha()
        self.rotated_surfs = {uldr:rot(base_surf,uldr) for uldr in directions}
        self.last_pos = [0,0]
        self.pos = [x,y]
        self.direction = 'd'
        self.surf = self.rotated_surfs[self.direction]
            
    def move(self,direction):
        self.last_pos = self.pos
        self.surf = self.rotated_surfs[direction]
        coordinate_changes = {'l':[-1,0],'r':[1,0],'u':[0,-1],'d':[0,1]}    
        self.pos[0] += coordinate_changes[direction][0]
        self.pos[1] += coordinate_changes[direction][1]
        
    def blit(self,display):
        #seems to use a reversed coordinate system?
        x,y = self.pos[0],self.pos[1]
        render_x = x*tilesize
        render_y = y*tilesize
        txt = font.render('%d,%d' % (x,y),
                    True,
                    rgb_black,
                    rgb_white)
        display.blit(txt,
                    (render_x,
                    render_y))
        display.blit(self.surf,
                    (render_x,
                    render_y))

class Tile(object):
    def __init__(self,surf,name,direction,x=0,y=0):
        self.surf = surf
        self.code = name_direction_to_code(name,direction)
        self.name = name
        self.direction = direction
        self.pos = [x,y]

    def __str__(self):
        x,y = self.pos[0],self.pos[1]
        return '%s %s@%d,%d' % (self.name,self.direction,x,y)

    def blit(self,display):
        #seems to use a reversed coordinate system?
        x,y = self.pos[0],self.pos[1]
        render_x = x*tilesize
        render_y = y*tilesize
        display.blit(self.surf,
                    (render_x,
                    render_y))

class TileSet(object):
    def __init__(self,csvfile,textures,tile_codes):
        self.csvfile = csvfile
        self.textures = textures
        self.tile_codes = tile_codes
        self.code_matrix = self.read_code_matrix(csvfile)
        self.tile_matrix = self.matrix_to_tiles(self.code_matrix)
        self.nrows = len(self.tile_matrix)
        self.ncols = len(self.tile_matrix[0])
        
    def read_code_matrix(self,csvfile):
        """Reads the matrix of texture codes from the CSV file
        """
        code_matrix = []
        with open(csvfile,'rb') as f:
            reader = csv.reader(f)
            for row_codes in reader:
                code_matrix.append(row_codes)
        return code_matrix

    def __str__(self):
        s = ''
        for code_row in self.code_matrix:
            for code in code_row:
                s+='%4s' % (code)
            s+='\n'
        return s
    
    def __getitem__(self,pos):
        return self.tile_matrix[pos[0]][pos[1]]

    def matrix_to_tiles(self,code_matrix):
        """Transposes code_matrix so that
        it has columns along first dimension
        and rows along the second 
        (so it's (x,y) or visually like the CSV)
        """

        nrows = len(code_matrix)
        ncols = len(code_matrix[0])
        tile_matrix = []
        for icol in range(ncols):
            tile_row = []
            for irow in range(nrows):
                code = code_matrix[irow][icol]
                texture_name,direction = self.tile_codes[code]
                texture = self.textures[texture_name][direction]
                t = Tile(texture,texture_name,direction)
                t.pos = [icol,irow]
                tile_row.append(t)
            tile_matrix.append(tile_row)
        return tile_matrix
    

def init_textures():
    base_textures = {
    'floor':im.load(os.path.join(imgdir,'floor.bmp')),
    'counter':im.load(os.path.join(imgdir,'counter.bmp')),
    'shelf':im.load(os.path.join(imgdir,'shelf1.bmp')),
    'frozen':im.load(os.path.join(imgdir,'frozen.bmp')),
    'produce':im.load(os.path.join(imgdir,'produce1.bmp'))
    }

    #Rotated textures
    textures = {}
    for surfname,surf in base_textures.iteritems():
        textures[surfname]={uldr:rot(surf,uldr) for uldr in directions}

    return textures

def generate_tile_codes(textures):
    #Look up table to find texture name and direction from texture code
    tile_codes = {}
    for surfname in textures:
        for uldr in textures[surfname]:
            code = name_direction_to_code(surfname,uldr)
            tile_codes[code] = (surfname,uldr)

    return tile_codes

textures = init_textures()
tile_codes = generate_tile_codes(textures)
tile_codes['x'] = tile_codes['fld'] # Floor is represented as x in CSV
    
levelcsv = '0.csv'
tileset = TileSet(os.path.join(leveldir,levelcsv),
                    textures,
                    tile_codes)

print(tileset)
#Seems to use backward coordinates
#(not standard cartesian)
display_w = tilesize*tileset.nrows
display_h = tilesize*tileset.ncols

pygame.init()

font = pygame.font.Font(fontfile,12)

DISPLAY = pygame.display.set_mode((display_w,display_h))

for tile_row in tileset.tile_matrix:
    for tile in tile_row:
        tile.blit(DISPLAY)

player = Player()

while True:
    player_tile = tileset[player.pos]

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == ord('a'):
                player.move('l')
            elif event.key == ord('s'):
                player.move('d')
            elif event.key == ord('w'):
                player.move('u')
            elif event.key == ord('d'):
                player.move('r')

    player_tile.blit(DISPLAY)
    player.blit(DISPLAY)
    pygame.display.update()
