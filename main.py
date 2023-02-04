import gzip
import sys
import os
import pickle
from random import randint
from pygame import QUIT, init
import pygame
import neat

WIN_WIDTH = 700
WIN_HEIGHT = 500
GEN = 0
WIN_ON = True

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

BARRA_WIDTH = 10
BARRA_HEIGHT = 100
BARRA_VEL = 5

BOLA_R = 7
BOLA_MAX_VEL = 5
BOLA_VEL_X = 5
BOLA_VEL_Y = 3

pygame.font.init()
STAT_FONT = pygame.font.Font(None, 32)
VIVOS_FONT = pygame.font.Font(None, 32)

pygame.init()
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Pong!")

# --------------------------------------------------------------------------------------------------
# Save e Load do melhor genoma



# --------------------------------------------------------------------------------------------------
# BARRA

class Barra:

	def __init__(self, x, y, index, cor):
		self.x = self.original_x = x
		self.y = self.original_y = y
		self.width = BARRA_WIDTH
		self.height = BARRA_HEIGHT
		self.index = index
		self.cor = cor

		self.vel = BARRA_VEL

	def draw(self, win):
		pygame.draw.rect(win, self.cor, (self.x, self.y, self.width, self.height))

	def move(self):
		if self.y - self.vel >= 0:
			self.vel = 0
		if self.y + self.vel + self.height <= WIN_HEIGHT:
			self.vel = 0

	def move_up(self):
		self.vel = BARRA_VEL
		self.y -= self.vel
	
	def move_down(self):
		self.vel = BARRA_VEL
		self.y += self.vel

	def move_stop(self):
		self.vel = 0

	def reset(self):
		self.x = self.original_x
		self.y = self.original_y

	def get_y(self):
		return self.y

	def get_x(self):
		return self.x

# --------------------------------------------------------------------------------------------------
# BOLA

class Bola:
	def __init__(self, cor):
		self.x = self.original_x = WIN_WIDTH // 2
		self.y = self.original_y = WIN_HEIGHT // 2
		self.raio = BOLA_R
		self.x_vel = BOLA_MAX_VEL
		self.y_vel = BOLA_VEL_Y
		self.cor = cor

	def draw(self, win):
		pygame.draw.circle(win, self.cor, (self.x, self.y), self.raio)

	def move(self):
		self.x += self.x_vel
		self.y += self.y_vel

	def reset(self):
		self.x = self.original_x
		self.y = self.original_y
		self.x_vel = BOLA_MAX_VEL
		self.y_vel = BOLA_VEL_Y

	def colisao_tetos(self):
		if self.y - self.raio <= 0 or self.y + self.raio >= WIN_HEIGHT:
			self.y_vel *= -1

	def colisao_laterais(self):
		if self.x > WIN_WIDTH - 11 - BARRA_WIDTH//2: # Direito
			return True

		if self.x < BARRA_WIDTH//2 - 1: # Esquerdo
			return True

	def colisao_barra_esq(self, esquerdo):
		if self.y >= esquerdo.y and self.y <= esquerdo.y + esquerdo.height:
			if self.x - self.raio <= esquerdo.x + esquerdo.width:
				self.x_vel *= -1
				meio_y = esquerdo.y + esquerdo.height / 2
				diff_y = meio_y - self.y
				reduction_factor = (esquerdo.height / 2) / BOLA_MAX_VEL
				y_vel = diff_y /reduction_factor
				self.y_vel = -1*y_vel

				return True

	def colisao_barra_dir(self, direito):
		if self.y >= direito.y and self.y <= direito.y + direito.height:
			if self.x + self.raio >= direito.x:
				self.x_vel *= -1
				meio_y = direito.y + direito.height / 2
				diff_y = meio_y - self.y
				reduction_factor = (direito.height / 2) / BOLA_MAX_VEL
				y_vel = diff_y /reduction_factor
				self.y_vel = -1*y_vel

				return True
				
			

# --------------------------------------------------------------------------------------------------

# Desenha as coisas na tela
def draw_window(win, barra_esq, barra_dir, bola_list):
	win.fill(BLACK)
	
	for bolas in bola_list:
		bolas.draw(win)

	for barra in barra_esq:
		barra.draw(win)
	
	for barra in barra_dir:
		barra.draw(win)

	# Linha do meio
	for i in range(10, WIN_HEIGHT, WIN_HEIGHT//20):
		if i % 2 == 1:
			continue
		pygame.draw.rect(win, WHITE, (WIN_WIDTH//2 - 2.5, i, 5, WIN_HEIGHT//20))

	# Gerações
	score_label = STAT_FONT.render("Gen: " + str(GEN-1), 1, (255, 255, 255))
	win.blit(score_label, (30, 10))

	# Vivos
	vivos = VIVOS_FONT.render("Vivos: " + str(len(barra_esq)), 1, WHITE)
	win.blit(vivos, (30, 40))

	pygame.display.flip()

def eval_genomes(genomes, config):

	global GEN
	global WIN_ON
	GEN += 1
	score = 0

	barra_esq = []
	barra_dir = []
	bola_list = []
	nets = []
	ge = []

	for genomes_id, g in genomes:
		cor_aleat = (randint(100, 255), randint(100, 255), randint(100, 255))
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		barra_esq.append(Barra(10, WIN_HEIGHT//2 - BARRA_HEIGHT//2, 'e', cor_aleat))
		barra_dir.append(Barra(WIN_WIDTH - 10 - BARRA_WIDTH, WIN_HEIGHT//2 - BARRA_HEIGHT//2, 'd', cor_aleat))
		bola_list.append(Bola(cor_aleat))

		g.fitness = 0
		ge.append(g)

	clock = pygame.time.Clock()

	run = True
	while run and len(barra_esq) > 0:
		if WIN_ON: clock.tick(FPS)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				sys.exit()
				break

		''' Barra Esquerda '''
		for x_c, barra in enumerate(barra_esq):
			# Ganha um pouco de fitness por ficar viva
			ge[x_c].fitness += 0.05
			barra.move()

				# Decisão da NN	
			outputs = nets[barra_esq.index(barra)].activate( (barra.get_y(), abs(barra.get_x() - bola_list[barra_esq.index(barra)].x), bola_list[barra_esq.index(barra)].y) )
			
			if outputs[0] > outputs[1]:
				if outputs[0] > 0.5:
					barra.move_up()
				else:
					barra.move_stop()
			elif outputs[1] > 0.5:
				barra.move_down()
			else:
				barra.move_stop()

		''' Barra Direita '''
		for x_c, barra in enumerate(barra_dir):
			# Ganha um pouco de fitness por ficar viva
			ge[x_c].fitness += 0.05
			barra.move()

				# Decisão da NN	
			outputs = nets[barra_dir.index(barra)].activate((barra.get_y(), 
			abs(barra.get_x() - bola_list[barra_dir.index(barra)].x), bola_list[barra_dir.index(barra)].y))
			
			if outputs[0] > outputs[1]:
				if outputs[0] > 0.5:
					barra.move_up()
				else:
					barra.move_stop()
			elif outputs[1] > 0.5:
				barra.move_down()

		''' Bola '''
		for bolas in bola_list:
			bolas.colisao_tetos()
			bolas.move()

			if bolas.colisao_barra_esq(barra_esq[bola_list.index(bolas)]):
				ge[bola_list.index(bolas)].fitness += 5
				score += 1
			if bolas.colisao_barra_dir(barra_dir[bola_list.index(bolas)]):
				ge[bola_list.index(bolas)].fitness += 5
				score += 1
			
			if bolas.colisao_laterais():
				ge[bola_list.index(bolas)].fitness -= 2

				nets.pop(bola_list.index(bolas))
				ge.pop(bola_list.index(bolas))
				barra_esq.pop(bola_list.index(bolas))
				barra_dir.pop(bola_list.index(bolas))
				bola_list.pop(bola_list.index(bolas))

		if WIN_ON:
			draw_window(win, barra_esq, barra_dir, bola_list)

		#if score > 500:
			#break

def run(config_file):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(eval_genomes, 1000)
    
	print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config-feedforward.txt')
	run(config_path)