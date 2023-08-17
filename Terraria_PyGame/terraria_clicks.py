import pygame
import environment as env

class Click_Handler():
    def __init__(self):
        self.mouseX = 0
        self.mouseY = 0
        self.timeOfLastBreak = pygame.time.get_ticks()
        self.breakSpeed = 150
        self.breakable = [1, 2, 3, 4]

    def updateMousePos(self, x, y):
        self.mouseX, self.mouseY = x, y
        self.clickedRow = int(y / env.BLOCK_SIZE)
        self.clickedColumn = int(x / env.BLOCK_SIZE)

    def isBlockWithinPlayerRange(self, playerRange, playerRect):
        blockY = self.clickedRow * env.BLOCK_SIZE
        blockX = self.clickedColumn *env.BLOCK_SIZE
        if blockX-(playerRange*env.BLOCK_SIZE) <= playerRect.midtop[0] <= blockX+(playerRange*env.BLOCK_SIZE):
            if blockY-(playerRange*env.BLOCK_SIZE) <= playerRect.midbottom[1] <= blockY+(playerRange*env.BLOCK_SIZE):
                return True
        return False
    
    def isOffMiningCooldown(self):
        currentTime = pygame.time.get_ticks()
        if currentTime - self.timeOfLastBreak >= self.breakSpeed:
            self.timeOfLastBreak = currentTime
            return True
        return False

    def isBreakable(self, block):
        if block in self.breakable:
            return True
        return False