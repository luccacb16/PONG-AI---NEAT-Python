import pygame
from barra import *
from constantes import *

class Bola:
	def __init__(self):
		self.x = self.original_x = WIN_WIDTH // 2
		self.y = self.original_y = WIN_HEIGHT // 2
		self.raio = BOLA_R
		self.x_vel = BOLA_MAX_VEL
		self.y_vel = BOLA_VEL_Y

		self.contadorEsq = 0
		self.contadorDir = 0

	def draw(self, win):
		pygame.draw.circle(win, RED, (self.x, self.y), self.raio)

		self.font = pygame.font.Font(None, 32)
		self.contadorEsq_texto = self.font.render(f'{self.contadorEsq}', False, WHITE) # Esquerdo
		self.contadorDir_texto = self.font.render(f'{self.contadorDir}', False, WHITE) # Direito

		win.blit(self.contadorEsq_texto, (WIN_WIDTH//4 - self.contadorEsq_texto.get_width()//2, 40)) # Esquerdo
		win.blit(self.contadorDir_texto, (WIN_WIDTH*3//4 - self.contadorDir_texto.get_width()//2, 40)) # Direito

	def move(self):
		self.x += self.x_vel
		self.y += self.y_vel

	def reset(self):
		self.x = self.original_x
		self.y = self.original_y
		self.x_vel = BOLA_MAX_VEL
		self.y_vel = BOLA_VEL_Y

	def colisao_lados(self, esquerdo, direito):
		if self.y - self.raio <= 0 or self.y + self.raio >= WIN_HEIGHT:
			self.y_vel *= -1

		if self.x > WIN_WIDTH - 10 - BARRA_WIDTH//2: # Direito
			self.contadorEsq += 1;
			self.reset()

		if self.x < BARRA_WIDTH//2: # Esquerdo
			self.contadorDir += 1;
			self.reset()

		if self.contadorDir >= WINNING_SCORE or self.contadorEsq >= WINNING_SCORE:
			self.reset()
			esquerdo.reset()
			direito.reset()
			self.contadorDir = 0
			self.contadorEsq = 0

	def colisao_barras(self, esquerdo, direito):
		if self.x_vel < 0:
			if self.y >= esquerdo.y and self.y <= esquerdo.y + esquerdo.height:
				if self.x - self.raio <= esquerdo.x + esquerdo.width:
					self.x_vel *= -1

					meio_y = esquerdo.y + esquerdo.height / 2
					diff_y = meio_y - self.y
					reduction_factor = (esquerdo.height / 2) / BOLA_MAX_VEL
					y_vel = diff_y /reduction_factor

					self.y_vel = -1*y_vel



		else:
			if self.y >= direito.y and self.y <= direito.y + direito.height:
				if self.x + self.raio >= direito.x:
					self.x_vel *= -1

					meio_y = direito.y + direito.height / 2
					diff_y = meio_y - self.y
					reduction_factor = (direito.height / 2) / BOLA_MAX_VEL
					y_vel = diff_y /reduction_factor

					self.y_vel = -1*y_vel

