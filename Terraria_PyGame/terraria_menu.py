import environment as env
import pygame

class Menu():
    def __init__(self):
        self.isActive = False

        self.left, self.top, self.width, self.height  = env.WINDOW_WIDTH/4, env.WINDOW_HEIGHT/4,  env.WINDOW_WIDTH/2, env.WINDOW_HEIGHT/2
        
        self.rect = (self.left, self.top, self.width, self.height)
    
    def activate(self):
        self.isActive = True

    
    def deactivate(self):
        self.isActive = False
    
    def draw(self, window):
        if self.isActive:
            self._draw_rounded_rect(window, pygame.Rect(self.left-5, self.top-5, self.width+10, self.height+10), env.BLACK, 30)
            self._draw_rounded_rect(window, pygame.Rect(self.rect), env.BROWN, 30)
            return True


    def _draw_rounded_rect(self, surface, rect, color, radius):
        x, y, w, h = rect

        pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
        pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))

        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)