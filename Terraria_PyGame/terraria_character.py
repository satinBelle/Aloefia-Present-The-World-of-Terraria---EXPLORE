import pygame
import environment as env
import terraria_menu as menu
import os
import math

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.width = env.BLOCK_SIZE*1.8
        self.height = env.BLOCK_SIZE*2.75

        self.x = 0
        self.y = 100

        self.xRectOffset = -1*self.width/2
        self.yRectOffset = -1*self.height/2

        self.rect = pygame.Rect(self.x, self.y, self.width-3, self.height)

        self.image_index = 0

        self.walkAnimation, self.standingImage, self.jumpingImage = self._image_handle()

        self.currentImage = self.standingImage
        self.doWalkAnimation = False
        self.isFacingRight = True

        self.yVel = 0.0
        self.xVel = 0.0
        self.maxXVel = 1
        self.maxYVel = 14
        self.gravitationalAcceleration = -1.1

        self.isGrounded = False
        self.isCollidingRight = False
        self.isCollidingLeft = False

        self.heldBlock = 1

        self.miningRange = 10


    def isTouchingGround(self, terrain, window, yOffset, drawRects):
        self.isGrounded = False
        self.isCollidingRight = False
        self.isCollidingLeft = False
        groundCollisionTile = None 


        for i in range(len(terrain)):

            for j in range(int(env.GRID_WIDTH/3), len(terrain[i])-int(env.GRID_WIDTH/3)):
                if terrain[i][j] != 0 and terrain[i-1][j] == 0:
                    thisRect = pygame.Rect(j*env.BLOCK_SIZE+4, (i-yOffset)*env.BLOCK_SIZE, env.BLOCK_SIZE-12, env.BLOCK_SIZE)
                    if drawRects:pygame.draw.rect(window, env.RED, thisRect)
                    if self.rect.colliderect(thisRect):
                        self.isGrounded = True
                        groundCollisionTile = thisRect
                if j+1 < len(terrain[i]):
                    if terrain[i][j] == 0 and terrain[i][j+1] != 0:
                        thisRect = pygame.Rect((j)*(env.BLOCK_SIZE), ((i-yOffset)*env.BLOCK_SIZE)+6, env.BLOCK_SIZE, env.BLOCK_SIZE-6)
                        if drawRects: pygame.draw.rect(window, env.YELLOW, thisRect)
                        if self.rect.colliderect(thisRect):
                            self.isCollidingRight = True
                if j-1 > 0:
                    if terrain[i][j] == 0 and terrain[i][j-1] != 0:
                        thisRect = pygame.Rect((j+1)*(env.BLOCK_SIZE)-env.BLOCK_SIZE, (i-yOffset)*env.BLOCK_SIZE+6, env.BLOCK_SIZE, env.BLOCK_SIZE/2)
                        if drawRects: pygame.draw.rect(window, env.BLUE, thisRect)
                        if self.rect.colliderect(thisRect):
                            self.isCollidingLeft = True

        if not self.isCollidingRight and not self.isCollidingLeft:
            if self.isGrounded: 
                self.rect.bottomleft = (env.WINDOW_WIDTH/2,  groundCollisionTile.midtop[1])

    def update(self, window, terrain, yOffset):
        keys = pygame.key.get_pressed()
        self.set_model()
        
        self.move(keys)
        self.isTouchingGround(terrain,window, yOffset, False)
        
    
        self.draw(window, False)

    def _image_handle(self):
        image_folder = os.path.join(os.path.dirname(__file__), "player_model")

        numOfWalkingImages = 9
        walkingSheet = pygame.image.load(os.path.join(image_folder,"Terraria_Characters_Walking.png"))
        walkingSheetScale = pygame.transform.scale(walkingSheet, (self.width*numOfWalkingImages, self.height))

        jumping = walkingSheetScale.subsurface(self.width*8-2, 0, self.width, self.height)

        walkingSeries = []        
        
        walkingSeries.append(walkingSheetScale.subsurface(self.width+6, 0, self.width+2, self.height))
        walkingSeries.append(walkingSheetScale.subsurface(0, 0, self.width, self.height))
        walkingSeries.append(walkingSheetScale.subsurface((self.width*2.5)-12, 0, self.width+2, self.height))
        walkingSeries.append(walkingSheetScale.subsurface(0, 0, self.width, self.height))
        
        numOfStandingImages = 2
        standingSheet = pygame.image.load(os.path.join(image_folder, "Terraria_Characters_Standing.png"))
        standingSheetScale = pygame.transform.scale(standingSheet, (self.width*numOfStandingImages, self.height))

        standing = standingSheetScale.subsurface(0, 0, self.width, self.height)

        return walkingSeries, standing, jumping

    def move(self, keys):

        #Horizontal Move
        self.xVel = int(keys[pygame.K_d])-int(keys[pygame.K_a])

        self.xVel = max(-1, self.xVel)
        self.xVel = min(1, self.xVel)

        if self.xVel > 0 and self.isCollidingRight:
            self.xVel = 0
        if self.xVel < 0 and self.isCollidingLeft:
            self.xVel = 0
        """-----------------------------------------------------------------------------------------------------------"""

        #Vertical Move
        if keys[pygame.K_SPACE] and self.isGrounded:
            self.yVel = self.maxYVel
            self.isGrounded = False
        elif not self.isGrounded:
            self.yVel += self.gravitationalAcceleration
        elif self.isGrounded:
            self.yVel = 0
        

        self.y -= self.yVel
        self.x += int(self.xVel)

        if self.y > env.WINDOW_HEIGHT:
            self.y = 0
            self.yVel = 0
        
        self.x = max(self.x, 10)
        self.x = min(self.x, int(env.GRID_WIDTH*(env.WORLD_HORIZONTAL_EXTENSION_FACTOR-1.5))-2)
        

        self.rect.topleft = (env.WINDOW_WIDTH/2, self.y)

    def set_model(self):

        #   If moving or not
        if self.xVel == 0:
            self.currentImage = self.standingImage
            self.image_index = 0
            self.doWalkAnimation = False
        else:
            self.doWalkAnimation = True
            self.image_index += 0.08
            if self.image_index > len(self.walkAnimation):
                self.image_index = 0

        if self.yVel != 0:
            self.showJumpImage = True
        else:
            self.showJumpImage = False

        rightFacingWalk = self.walkAnimation[int(self.image_index)]
        leftFacingWalk = pygame.transform.flip(rightFacingWalk, True, False)
        rightFacingJump = self.jumpingImage
        leftFacingJump = pygame.transform.flip(rightFacingJump, True, False)
        
        # In what direction are you moving
        if self.xVel > 0:
            self.currentImage = rightFacingWalk
            if self.showJumpImage:
                self.currentImage = rightFacingJump
            
        elif self.xVel < 0:
            self.currentImage = leftFacingWalk
            if self.showJumpImage:
                self.currentImage = leftFacingJump



    def draw(self, window, drawRect):   
        if drawRect:
            pygame.draw.rect(window, env.RED, self.rect)
        
        window.blit(self.currentImage, (self.rect.topleft[0], self.rect.topleft[1]))


class BlockMenu(menu.Menu):


    def __init__(self):
        super().__init__()
        self.chosenBlock = None
        self.blocks = []
        self.width = 45
        self.height = 45
        self.rects = {}

    def activate(self, currentInventory):
        if len(currentInventory) != 0:
            super().activate()
            self.blocks = currentInventory

    def draw(self, window, font):
        if self.isActive:
            self.rects = {}
            pygame.draw.circle(window, env.BLACK, (env.WINDOW_WIDTH/2, env.WINDOW_HEIGHT/2), 292)
            pygame.draw.circle(window, env.PINK, (env.WINDOW_WIDTH/2, env.WINDOW_HEIGHT/2), 292-4)

            angleIncrement = 2 * math.pi / len (self.blocks)
            angle = math.pi*-0.5
            for i, block in enumerate(self.blocks):
                angle += angleIncrement
                xPos = env.WINDOW_WIDTH/2 + int(202 * math.cos(angle)) - (self.width/2)
                yPos = env.WINDOW_HEIGHT/2 + int(202 * math.sin(angle)) - (self.width/2)

                rect = pygame.Rect(xPos, yPos, 30, 30)
                self.rects[block.id] = rect
                pygame.draw.rect(window, env.BLOCK_COLORS[block.id], rect)

                blockText = font.render (f"{block.name}", True, env.WHITE)
                window.blit(blockText, (xPos+(self.width/2)-(blockText.get_size()[0]/2), yPos+blockText.get_size()[1] + 25))
                

    def blockHovering(self, mouseX, mouseY, player):
        if self.isActive:
            clickRect = pygame.Rect(mouseX, mouseY, 1, 1)

            for id, rect in self.rects.items():
                

                if rect.colliderect(clickRect):
                    player.heldBlock = id


class Trader(pygame.sprite.Sprite):
    def __init__(self, terrain, yOffset):
        self.width = 270 * 1.2
        self.height = 245 * 1.2

        self.global_x_index = 10
        self.yIndex = self.findPlacementHeight(terrain, yOffset)

        self.onScreenXPos = self.global_x_index*env.BLOCK_SIZE-self.width
        self.onScreenYPos = (self.yIndex+0.8)*env.BLOCK_SIZE-self.height

        self.onScreenCamXValue = 50

        self.yRectOffset = 38
        self.xRectOffset = 24

        self.isActive = True

        self.rect = pygame.Rect(self.onScreenXPos+self.xRectOffset/2, self.onScreenYPos+self.yRectOffset, self.width-self.xRectOffset, self.height-self.yRectOffset)

        self.image, self.characterModel = self.__handle_image()

        self.isMouseHovering = False

        self.mining_upgrades = {"mining_range": 0, "mining_speed": 0, "mining_level": 0, "fortune": 0, "storage_level": 0}

        self.mining_upgrade_costs = {"mining_range": [10, 100, 1000], "mining_speed": [10, 100, 1000], "mining_level": [10, 100, 1000], "fortune": [10, 100, 1000], "storage_level": [10, 100, 1000]}

        self.attacking_upgrades = {"attacking_range": 0, "attacking_speed": 0, "attacking_level": 0}

        self.item_name_price={"Dirt":3, "Stone":4, "Metal":10, "Diamond":25, "Garnet":50, "Topaz":50, "Alzo":100, "Grass": 3}

        self.menu = TraderMenu()

    def __handle_image(self):
        image_folder = os.path.join(os.path.dirname(__file__), "trader_model")
        trader = pygame.image.load(os.path.join(image_folder,"terraria_trader.png"))
        traderScaled = pygame.transform.scale(trader, (self.width/6, self.height/4))
        hut = pygame.image.load(os.path.join(image_folder,"trading_hut_dark.png"))
        hutScaled = pygame.transform.scale(hut, (self.width, self.height))

        return hutScaled, traderScaled
    
    def __isOnScreen(self, cameraX):
        if cameraX < self.onScreenCamXValue+self.global_x_index+1:
            self.isActive = True
        else:
            self.isActive = False
            self.isMouseHovering = False
        if self.yIndex < 1:
            self.isActive = False
        elif self.yIndex > 1:
            self.isActive = True

    
    def __updatePosition(self, cameraX):
        self.onScreenXPos = (self.onScreenCamXValue-cameraX+self.global_x_index)*env.BLOCK_SIZE-self.width
        
        self.rect.topleft = (self.onScreenXPos+self.xRectOffset/2, self.onScreenYPos+self.yRectOffset)

    def draw(self, window, font, drawRect, mouseX, mouseY):
        if self.isActive:
            if drawRect:
                pygame.draw.rect(window, env.RED, self.rect)
            window.blit(self.image, (self.rect.topleft[0]-self.xRectOffset/2, self.rect.topleft[1]-self.yRectOffset))
            if self.menu.isActive:
                window.blit(self.characterModel, (self.rect.midbottom[0]+self.characterModel.get_size()[0]/2+10, self.rect.midbottom[1]-self.characterModel.get_size()[1]))


            if self.isMouseHovering and not self.menu.isActive:
                text = font.render(f"Press {env.K_INTERACT}", True, env.WHITE)
                textRect = text.get_rect()
                textRect.topleft = (mouseX+15, mouseY+12)
                window.blit(text, textRect)
            

    def update(self, window, cameraX, mouseX, mouseY, font, mouseOneClicked, inventory, player, clicker):
        self.__isOnScreen(cameraX)
        self.__updatePosition(cameraX)
        self.draw(window, font, False, mouseX, mouseY)
        self.checkMouse(mouseX, mouseY, mouseOneClicked)
        self.upgrade(inventory, player, clicker)

    def findPlacementHeight(self, terrain, yOffset):
        for rowIndex in range(len(terrain)):
            if terrain[rowIndex][0] != 0:
                self.yIndex = rowIndex-yOffset
                self.onScreenYPos = (self.yIndex+0.8)*env.BLOCK_SIZE-self.height
                return self.yIndex
    
    def checkMouse(self, mouseX, mouseY, mouseOneClicked):
        self.upgradeClicked = None
        if self.isActive and not self.menu.isActive:
            clickRect = pygame.Rect(mouseX, mouseY, 1, 1)
            if self.rect.colliderect(clickRect):
                self.isMouseHovering = True
            else:
                self.isMouseHovering = False
        elif self.isActive and self.menu.isActive:
            if mouseOneClicked:
                self.upgradeClicked = self.menu.determineUpgradeClicked(mouseX, mouseY)
                
    def upgrade(self, inventory, player, clicker):
        if self.upgradeClicked != None:
            if self.upgradeClicked <= 4:
                if self.upgradeClicked == 0 and self.mining_upgrades["mining_range"] < 3:
                    upgradeCost = self.mining_upgrade_costs["mining_range"][self.mining_upgrades["mining_range"]]
                    if upgradeCost <= inventory.money:
                        inventory.money -= upgradeCost
                        player.miningRange += 2
                        self.mining_upgrades["mining_range"] += 1

                elif self.upgradeClicked == 1 and self.mining_upgrades["mining_speed"] < 3:
                    upgradeCost = self.mining_upgrade_costs["mining_speed"][self.mining_upgrades["mining_speed"]]
                    if upgradeCost <= inventory.money:
                        inventory.money -= upgradeCost
                        clicker.breakSpeed -= 25
                        self.mining_upgrades["mining_speed"] += 1

                elif self.upgradeClicked == 2 and self.mining_upgrades["mining_level"] < 3:
                    upgradeCost = self.mining_upgrade_costs["mining_level"][self.mining_upgrades["mining_level"]]
                    if upgradeCost <= inventory.money:
                        inventory.money -= upgradeCost
                        if self.mining_upgrades["mining_level"] == 0:
                            clicker.breakable.append(5)
                        if self.mining_upgrades["mining_level"] == 1:
                            clicker.breakable.append(6, 7)
                        if self.mining_upgrades["mining_level"] == 2:
                            clicker.breakable.append(8)
                            
                        self.mining_upgrades["mining_level"] += 1


                elif self.upgradeClicked == 3 and self.mining_upgrades["fortune"] < 3:
                    upgradeCost = self.mining_upgrade_costs["fortune"][self.mining_upgrades["fortune"]]
                    if upgradeCost <= inventory.money:
                        inventory.money -= upgradeCost
                        inventory.fortune += 1
                        self.mining_upgrades["fortune"] += 1

                elif self.upgradeClicked == 4 and self.mining_upgrades["storage_level"] < 3:
                    upgradeCost = self.mining_upgrade_costs["storage_level"][self.mining_upgrades["storage_level"]]
                    if upgradeCost <= inventory.money:
                        inventory.money -= upgradeCost
                        inventory.level += 1
                        self.mining_upgrades["storage_level"] += 1


            if self.upgradeClicked > 4 and self.upgradeClicked < 8:
                self.attacking_upgrades[list(self.attacking_upgrades)[self.upgradeClicked-5]] += 1
            if self.upgradeClicked == 8 and self.inventoryPrice != 0:
                inventory.money += self.inventoryPrice
                self.inventoryPrice = 0
                inventory.storage = []
                self.activateMenu 

    def activateMenu(self, inventory): 
        self.inventoryPrice = 0
        for unit in inventory:
            self.inventoryPrice += self.item_name_price[unit.name] * unit.count
        
        
        if self.isMouseHovering:
            self.menu.activate(self.mining_upgrades, self.attacking_upgrades, self.inventoryPrice)


class TraderMenu(menu.Menu):

    
    def __init__(self):
        super().__init__()
        self.mining_upgrades = None
        self.attacking_upgrades = None        

    def activate(self, *args):
        super().activate()
        self.mining_upgrades = args[0]
        self.attacking_upgrades = args[1]
        self.inventoryPrice = args[2]

    def draw(self, window, headerFont, font):
        self.textRects = []
        if super().draw(window):
            miningHeaderText = headerFont.render(f"Mining", True, env.WHITE)
            headerSize = miningHeaderText.get_size()
            window.blit(miningHeaderText, ((self.rect[0]+(self.width/4))-(headerSize[0]/2), (self.top + 20)))
            
            underline_y = (self.top + 20) +  headerSize[1]
            pygame.draw.rect(window, env.WHITE, ((self.rect[0]+(self.width/4))-(headerSize[0]/2), underline_y-10, headerSize[0], 2))

            AttackingHeaderText = headerFont.render(f"Attacking", True, env.WHITE)
            attackingHeaderSize = AttackingHeaderText.get_size()
            window.blit(AttackingHeaderText, ((self.rect[0]+(self.width*3/4))-( attackingHeaderSize[0]/2), (self.top + 20)))
            
            underline_y = (self.top + 20) +   attackingHeaderSize[1]
            pygame.draw.rect(window, env.WHITE, ((self.rect[0]+(self.width*3/4))-( attackingHeaderSize[0]/2), underline_y-10,  attackingHeaderSize[0], 2))
            
            for i, (upgrade, level) in enumerate(self.mining_upgrades.items()):
                upgradeText = None

                if upgrade == "mining_range":
                    upgradeText = "Range"
                if upgrade == "mining_speed":
                        upgradeText = "Mining Speed"
                if upgrade == "mining_level":
                        upgradeText = "Mining Level"
                if upgrade == "fortune":
                    upgradeText = "Fortune"
                if upgrade == "storage_level":
                    upgradeText = "Inventory Size"

                text = font.render(f"{upgradeText} -> {level}", True, env.WHITE)
                self.textRects.append(pygame.Rect((self.rect[0]+(self.width/4))-(text.get_size()[0]/2), ((headerSize[0])+ self.top + ((text.get_size()[1]*2)*i)), *text.get_size()))
                window.blit(text, ((self.rect[0]+(self.width/4))-(text.get_size()[0]/2), ((headerSize[0])+ self.top + ((text.get_size()[1]*2)*i))))            

            for i, (upgrade, level) in enumerate(self.attacking_upgrades.items()):
                
                upgradeText = None

                if upgrade == "attacking_range":
                    upgradeText = "Range"
                if upgrade == "attacking_speed":
                    upgradeText = "Attacking Speed"
                if upgrade == "attacking_level":
                    upgradeText = "Attacking Level"

                text = font.render(f"{upgradeText} -> {level}", True, env.WHITE)
                window.blit(text, ((self.rect[0]+(self.width*3/4))-(text.get_size()[0]/2), ((headerSize[0])+ self.top + ((text.get_size()[1]*3)*i))))
                self.textRects.append(pygame.Rect((self.rect[0]+(self.width*3/4))-(text.get_size()[0]/2), ((headerSize[0])+ self.top + ((text.get_size()[1]*3)*i)), *text.get_size()))
            
            
    
            text = font.render(f"Sell Price: {self.inventoryPrice}", True, env.WHITE)
            window.blit(text, (self.rect[0]+self.width-text.get_size()[0]-18, self.rect[1]+self.height-text.get_size()[1]-5))
            self.textRects.append(pygame.Rect(self.rect[0]+self.width-text.get_size()[0], self.rect[1]+self.height-text.get_size()[1], *text.get_size()))

    
    def determineUpgradeClicked(self, mouseX, mouseY):
        if self.isActive:
            if len(self.textRects) != 0:
                for i, rect in enumerate(self.textRects):
                    clickRect = pygame.Rect(mouseX, mouseY, 1, 1)
                    if rect.colliderect(clickRect):
                        return(i)


"""
UPGRADES:
- Extended Range
- Increase Mining Speed x3
- Mining Level = which blocks you're able to break x3
- Attack Speed x3
- Attack Damage x3
- Fortune x3
- Capacity

"""