import environment as env
import terraria_menu as menu
import pygame
import random


class Inventory():
    def __init__(self):
        self.storage = []
        self.level = 0
        self.fortune = 0
        self.item_id_capacity = self.item_id_capacity = {0: {1: 1000, 2: 1000, 3:500, 4:500, 5:250, 6:150, 7:150, 8:5}, 1: {1: 2000, 2: 2000, 3:1000, 4:1000, 5:500, 6:300, 7:300, 8:10}, 2: {1: 4000, 2: 4000, 3:2000, 4:2000, 5:1000, 6:600, 7:600, 8:20}}
        self.item_id_block_award_quantity = {1: 20, 2: 20, 3:10, 4:4, 5:3, 6:2, 7:2, 8:1}
        self.block_placement_cost = {1: 20, 2: 20, 3:10, 4:5, 5:3, 6:3, 7:3, 8:2}
        self.money = 0
        self.menu = Inventory_Menu()
    
    def print_storage(self):
        print("[")
        for unit in self.storage:
            print(f"   {unit.id} : {unit.name} -> {unit.count}")
        print("]")
    
    def get_storage(self):
        return self.storage

    def get_count(self, id):
        for unit in self.storage:
            if unit.id == id:
                return unit.count
        print("None Current Available")
        return 0

    
    def add_item(self, item):
        for unit in self.storage:
            if unit.name == item.name:
                newCount = unit.count + item.count
                if newCount <= self.item_id_capacity[self.level][unit.id]:
                    unit.count = newCount
                else:
                    unit.count = self.item_id_capacity[self.level][unit.id]
                return unit.count
        
        # Clone the new item object so that it doesn't point to the exact object passed in but instead a new object with the same Values
        unique_item_object = item.clone()
        self.storage.append(unique_item_object)

    def get_random_block_reward(self, block):
        return {1: 20, 2: 20, 3:10, 4:5, 5:random.randint(1, self.fortune+3), 6:random.randint(1, self.fortune+1), 7:random.randint(1, self.fortune+1), 8:random.randint(1, self.fortune+1)}[block]

    def create_text_popup(self, window, font, block, amount, mouse_pos):
        popup = font.render(f"Collected {amount}: {Item_Bundle.id_names[block]}", True, env.PINK)
        window.blit(popup, (mouse_pos[0]+20, mouse_pos[1]))
    
    def remove_item(self, amount, **kwargs):
        name = kwargs.get('item_name', None)
        id = kwargs.get('item_id', None)

        if name is not None:
            for unit in self.storage:
                if unit.name == name:
                    if unit.count < amount:
                        print(f"Don't have enough to remove {amount}")
                    elif unit.count >= amount:
                        unit.count -= amount
                    return True
        elif id is not None:
            for unit in self.storage:
                if unit.id == id:
                    if unit.count < amount:
                        print(f"Don't have enough to remove {amount}")
                    elif unit.count >= amount:
                        unit.count -= amount
                    
                    return True
        
        print("-Did not remove any items-")
        return False

class Item_Bundle():
    id_names = {1:"Grass", 2:"Dirt", 3:"Stone", 4:"Metal", 5:"Diamond", 6:"Topaz", 7:"Garnet", 8:"Alzo"}
    allIds = list(id_names)    

    def __init__(self, id, count):
        self.id = id
        self.count = count
        self.name = Item_Bundle.id_names[id]
    
    def clone(self):
        return Item_Bundle(self.id, self.count)
    
    def print_info(self):
        print(f"Name : {self.name}")
        print(f"ID : {self.id}")
        print(f"Count : {self.count}")

class Inventory_Menu(menu.Menu):
    def __init__(self):
        super().__init__()
        self.displayStorage = None
    
    def activate(self, inventory):
        super().activate()
        self.displayStorage = inventory
    
    def deactivate(self):
        super().deactivate()
        self.displayStorage = None
    
    def draw(self, window, font, money):
        if super().draw(window):
            if len(self.displayStorage) != 0:
                for i, unit in enumerate(self.displayStorage):
                    text = font.render(f"{unit.name} -> {unit.count}", True, env.WHITE)
                    window.blit(text, (self.width-(text.get_size()[0]/2), (self.top + ((text.get_size()[1]*2)*i)+20)))
            else:
                text = font.render("No Resources Available", True, env.WHITE)
                window.blit(text, (self.width-(text.get_size()[0]/2), (self.top + text.get_size()[1])))

            text = font.render(f"Money: {money}", True, env.WHITE)
            window.blit(text, ((self.width/2)+(text.get_size()[0]/5), (self.top + self.height- (text.get_size()[1])-10)))
            