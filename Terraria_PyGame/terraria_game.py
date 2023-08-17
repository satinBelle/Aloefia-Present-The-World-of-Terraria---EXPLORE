import pygame
import environment as env
import terraria_world as map
import terraria_character as character
import terraria_inventory as warehouse
import terraria_clicks as click
import pickle

# Pygame initialization
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((env.WINDOW_WIDTH, env.WINDOW_HEIGHT))
pygame.display.set_caption("Aloefia Present: The Two Mini Worlds of Terraria (A Fighting and Resources Exploration Game)")
clock = pygame.time.Clock()
# Font
HEADER_FONT = pygame.font.Font(None, 65)
FONT = pygame.font.Font(None, 38)
FONT2 = pygame.font.Font(None, 34)
INSTRUCTIONS_FONT = pygame.font.Font(None, 24)

def break_block(mouse, player, cameraX, inventory, terrain, yOffset, window, font):
    if mouse.isOffMiningCooldown():
        mouse.updateMousePos(*pygame.mouse.get_pos())
        if mouse.isBlockWithinPlayerRange(player.miningRange, player.rect):
            if map.has_air_surrounding(terrain, mouse.clickedRow+yOffset, mouse.clickedColumn+cameraX):
                block = terrain[mouse.clickedRow+yOffset][mouse.clickedColumn+cameraX]
                if mouse.isBreakable(block):
                    amount = inventory.get_random_block_reward(block)
                    inventory.add_item(warehouse.Item_Bundle(block, amount))
                    inventory.create_text_popup(window, font, block, amount, pygame.mouse.get_pos())
                    terrain[mouse.clickedRow+yOffset][mouse.clickedColumn+cameraX] = 0
                    return True
    return False

def place_block(mouse, event, player, cameraX, inventory, terrain, yOffset):
    mouse.updateMousePos(*event.pos)
    if mouse.isBlockWithinPlayerRange(player.miningRange, player.rect):
        if terrain[mouse.clickedRow+yOffset][mouse.clickedColumn+cameraX] == 0:
            if inventory.get_count(player.heldBlock) >= inventory.block_placement_cost[player.heldBlock]:
                inventory.remove_item(inventory.block_placement_cost[player.heldBlock], item_id=player.heldBlock)
                terrain[mouse.clickedRow+yOffset][mouse.clickedColumn+cameraX] = player.heldBlock
                return True
    return False

def save_game(obj):
    file_name = 'data.pickle'
    with open(file_name, 'wb') as file:
        pickle.dump(obj, file)

def main():
    Running = True

    prevCameraX, cameraX, cameraY, yCamOffset = 2, 2, 0, 0
    gameSeed = 4
    terrain = map.generate_terrain(gameSeed)
    fullHeightTerrain, onScreenTerrain = None, None
    shader = None
    shaderUpToDate = False
    player = character.Player()
    trader = character.Trader(terrain, yCamOffset)
    blockMenu = character.BlockMenu()
    inventory = warehouse.Inventory()
    mouse = click.Click_Handler()


    while Running:
        clock.tick(env.FPS)
        screen.fill(env.SKY_BLUE)
        isMouseOneClicked = False

        trader.findPlacementHeight(terrain, yCamOffset)

        prevCameraX = cameraX
        cameraX = player.x + int(env.GRID_WIDTH/2)
        
        fullHeightTerrain, onScreenTerrain = map.get_terrain_arrays(terrain, cameraX, cameraY, yCamOffset)
        if (prevCameraX != cameraX) or (not shaderUpToDate):
            shader = map.generate_shaders(fullHeightTerrain)
            shaderUpToDate = True
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Running = False
                save_game("inventory.pickle", inventory)
                save_game("map.pickle", terrain)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    isMouseOneClicked = True
                if event.button == 3 and not trader.menu.isActive and not inventory.menu.isActive:
                    place_block(mouse, event, player, cameraX, inventory, terrain, yCamOffset)
                    shaderUpToDate = False
            if event.type == pygame.KEYDOWN:
                if event.key == 101 or event.key == 9: # "E" or "Tab"
                    inventory.menu.activate(inventory.get_storage())
                elif event.key == 27: # "Escape"
                    inventory.menu.deactivate()
                    trader.menu.deactivate()
                elif event.key == 102: # "F"
                    trader.activateMenu(inventory.storage)
                elif event.key == 113:
                    blockMenu.activate(inventory.storage)
            if event.type == pygame.KEYUP:
                if event.key == 113:
                    blockMenu.deactivate() 
            
        if pygame.mouse.get_pressed()[0]:
            if not trader.menu.isActive and not inventory.menu.isActive:
                if break_block(mouse, player, cameraX, inventory, terrain, yCamOffset, screen, FONT):
                    shaderUpToDate = False


        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            yCamOffset += 1
            yCamOffset = min(yCamOffset, 36)
            shaderUpToDate = False


        elif keys[pygame.K_w]:
            yCamOffset -= 1
            yCamOffset = max(yCamOffset, -10)
            shaderUpToDate = False
        
        if blockMenu.isActive:
            blockMenu.blockHovering(*pygame.mouse.get_pos(), player)

        map.draw_sun(screen, env.WINDOW_WIDTH-100, 100)
        map.generator_draw(screen, onScreenTerrain, shader, cameraY, yCamOffset)
        player.update(screen, onScreenTerrain, yCamOffset)
        trader.update(screen, cameraX, *pygame.mouse.get_pos(), INSTRUCTIONS_FONT, isMouseOneClicked, inventory, player, mouse)
        inventory.menu.draw(screen, FONT, inventory.money)
        trader.menu.draw(screen, FONT, FONT2)

        blockMenu.draw(screen, FONT2)

        if pygame.mouse.get_pressed()[0]:
            if not trader.menu.isActive and not inventory.menu.isActive:
                if break_block(mouse, player, cameraX, inventory, terrain, yCamOffset, screen, FONT):
                    shaderUpToDate = False
        pygame.display.flip()



if __name__ == "__main__":
    main()
    pygame.quit()








