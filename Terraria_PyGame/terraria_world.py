import pygame
import environment as env
import random
import math

class PerlinNoise():
    def __init__(self, seed, amplitude=1, frequency=1, octaves=1):
        self.seed = random.Random(seed).random()
        self.amplitude = amplitude
        self.frequency = frequency
        self.octaves = octaves

        self.mem_x = dict()


    def __noise(self, x):
        # made for improve performance
        if x not in self.mem_x:
            self.mem_x[x] = random.Random(self.seed + x).uniform(-1, 1)
        return self.mem_x[x]


    def __interpolated_noise(self, x):
        prev_x = int(x) # previous integer
        next_x = prev_x + 1 # next integer
        frac_x = x - prev_x # fractional of x
        res = self.__cubic_interp(
            self.__noise(prev_x - 1), 
            self.__noise(prev_x), 
            self.__noise(next_x),
            self.__noise(next_x + 1),
            frac_x)

        return res


    def get(self, x):
        frequency = self.frequency
        amplitude = self.amplitude
        result = 0
        for _ in range(self.octaves):
            result += self.__interpolated_noise(x * frequency) * amplitude
            frequency *= 2
            amplitude /= 2

        return result

    def __cubic_interp(self, v0, v1, v2, v3, x):
        p = (v3 - v2) - (v0 - v1)
        q = (v0 - v1) - p
        r = v2 - v0
        s = v1
        return p * x**3 + q * x**2 + r * x + s

def generate_terrain(seed=2):
    # Perlin Noise
    amp = 25
    freq = 0.015
    octaves = 6
    noise = PerlinNoise(seed, amp, freq, octaves)

    # Surface Terrain Generation

    def isBetween(val, row, bound1, bound2):
        if row-bound1 > val  and row-bound2 < val: 
            return True
        else: return False
    

    row_range = (-5, env.GRID_DEPTH *env.WORLD_VERTICAL_EXTENSION_FACTOR)
    column_range = (1, env.GRID_WIDTH*env.WORLD_HORIZONTAL_EXTENSION_FACTOR)

    terrain = []
    for row in range(*row_range):
        terrainRow = []
        for column in range(*column_range):

            
            noiseY = abs(noise.get(column))
            if column < 80:
                noiseY = abs(noise.get(81))
            if isBetween(noiseY, row, 0, 1):
                terrainRow.append(1)
            elif isBetween(noiseY, row, 1, 2):
                block = random.choices([1,2], cum_weights=(82,100))[0]
                terrainRow.append(block)
            elif isBetween(noiseY, row, 2, 4):
                terrainRow.append(2)
            elif isBetween(noiseY, row, 2, 8):
                block = random.choices([2,3], cum_weights=(98, 100))[0]
                terrainRow.append(block)
            elif isBetween(noiseY, row, 8, 15):
                block = random.choices([2,3], cum_weights=(40,100))[0]
                terrainRow.append(block)
            elif isBetween(noiseY, row, 15, 19):
                block = random.choices([2,3], cum_weights=(12,100))[0]
                terrainRow.append(block)
            elif isBetween(noiseY, row, 19, 31):
                block = random.choices([3,4], cum_weights=(80,100))[0]
                terrainRow.append(block)
            elif isBetween(noiseY, row, 31, 48):
                block = random.choices([3, 4, 5], cum_weights=(85, 97, 100))[0]
                terrainRow.append(block)
            elif isBetween(noiseY, row, 48, 54):
                block = random.choices([3, 4, 6, 7], cum_weights=(92, 98, 99, 100))[0]
                terrainRow.append(block)
            elif isBetween(noiseY, row, 54, 72):
                block = random.choices([3, 6, 7, 8], cum_weights=(95, 97, 99, 100))[0]
                terrainRow.append(block)
            elif row-71 > noiseY:
                terrainRow.append(3)
            else:
                terrainRow.append(0)

        terrain.append(terrainRow)
    return terrain

def draw_sun(screen, x, y, rays=9, ray_length=100, ray_width=5):
    for i in range(rays):
        angle = math.radians(360 / rays * i)
        x1 = x + ray_length * math.cos(angle)
        y1 = y + ray_length * math.sin(angle)
        pygame.draw.line(screen, env.YELLOW, (x, y), (x1, y1), ray_width)
        pygame.draw.circle(screen, env.YELLOW, (x,y), ray_length*2/3)

def get_square_from_2d_list(matrix, start_row, start_col, height, width):

    square = []
    for row in range(start_row, start_row + height):
        my_list = matrix[row][start_col:start_col + width]
        square.append(my_list)
    
    return square

def get_surrounding_elements(matrix, row, col):
    # Define the possible relative positions of the surrounding elements
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1), (1, 1)
    ]

    surrounding_elements = []
    num_rows = len(matrix)
    num_cols = len(matrix[0])



    for dr, dc in directions:
        r = row + dr
        c = col + dc

        # Check if the position is within the bounds of the matrix
        if 0 <= r < num_rows and 0 <= c < num_cols:
            if matrix[r][c] != "x":
                surrounding_elements.append(matrix[r][c]**(2/3))
            else:
                surrounding_elements.append(0)

    return surrounding_elements

def has_air_surrounding(matrix, row, col):
    if matrix[row][col] == 0: return False
    # Define the possible relative positions of the surrounding elements
    directions = [
        (-1, 0),(0, -1),(0, 1),(1, 0)
    ]

    num_rows = len(matrix)
    num_cols = len(matrix[0])
    
    for dr, dc in directions:
        r = row + dr
        c = col + dc

        # Check if the position is within the bounds of the matrix
        if 0 <= r < num_rows and 0 <= c < num_cols:
            if matrix[r][c] == 0:
                return True


    return False

def generate_shaders(fullHeightOnScreenTerrain):
    lighting = []
    for x in fullHeightOnScreenTerrain:
        lightingRow = []
        for y in x:
            if y == 0:
                lightingRow.append(1)
            else:
                lightingRow.append("x")
        lighting.append(lightingRow)
    
    for x in range(len(lighting)):
        for y in range(len(lighting[x])):
            if lighting[x][y] == "x":
                surroundingLighting = get_surrounding_elements(lighting, x, y)
                averageLight = sum(surroundingLighting) / len(surroundingLighting)
                if len(surroundingLighting) >  5:
                    lighting[x][y] = averageLight if averageLight > 0.19 else max(0, averageLight-0.06)
                elif len(surroundingLighting) >= 4:  
                    lighting[x][y] = 0.1 
                else:
                    lighting[x][y] = max(0, 1)
    return lighting

def get_terrain_arrays(terrain, cameraX, cameraY, yOffset):
    fullHeightTerrain = get_square_from_2d_list(terrain, 0, cameraX-env.X_MAPPING_OFFSET, env.GRID_DEPTH*env.WORLD_VERTICAL_EXTENSION_FACTOR, env.GRID_WIDTH+env.X_MAPPING_OFFSET*2)
    onScreenTerrain = get_square_from_2d_list(fullHeightTerrain, cameraY, env.X_MAPPING_OFFSET, env.GRID_DEPTH*env.WORLD_VERTICAL_EXTENSION_FACTOR-cameraY, env.GRID_WIDTH)

    return fullHeightTerrain, onScreenTerrain

def generator_draw(window, terrainOnScreen, shader, cameraY, yOffset):
    cameraY  = max(cameraY, 0)
    cameraY = min(cameraY, env.GRID_DEPTH*(env.WORLD_VERTICAL_EXTENSION_FACTOR)-1)








    for i, row in enumerate(terrainOnScreen):
        for j, block in enumerate(row):
            xPos = j * env.BLOCK_SIZE 
            yPos = (i- yOffset) * env.BLOCK_SIZE
            
            color = env.BLOCK_COLORS[block]

            if block != 0:
                pygame.draw.rect(window, tuple(int(c * shader[i+cameraY][j+env.X_MAPPING_OFFSET]) for c in color), pygame.Rect(xPos, yPos, env.BLOCK_SIZE, env.BLOCK_SIZE))