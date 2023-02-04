import pygame
from constantes import *

class Barra:

	def __init__(self, x, y, index):
		self.x = self.original_x = x
		self.y = self.original_y = y
		self.width = BARRA_WIDTH
		self.height = BARRA_HEIGHT
		self.index = index

		self.vel = BARRA_VEL

	def draw(self, win):
		pygame.draw.rect(win, WHITE, (self.x, self.y, self.width, self.height))

	def move(self):
		tecla = pygame.key.get_pressed()

		if (self.index == 'e'):
			if tecla[pygame.K_w] and self.y - self.vel >= 0:
				self.y -= self.vel
			if tecla[pygame.K_s] and self.y + self.vel + self.height <= WIN_HEIGHT:
				self.y += self.vel

		if (self.index == 'd'):
			if tecla[pygame.K_UP] and self.y - self.vel >= 0:
				self.y -= self.vel
			if tecla[pygame.K_DOWN] and self.y + self.vel + self.height <= WIN_HEIGHT:
				self.y += self.vel

	def reset(self):
		self.x = self.original_x
		self.y = self.original_y