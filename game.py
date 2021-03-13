import os, pygame
from pygame.locals import *
import random
import numpy as np
from scipy.stats import expon

# constants
BACKGROUND_COLOR = (255, 255, 255)
PLAYER_COLOR = (0, 0, 0)
OBSTACLE_COLOR = (200, 200, 100)
SCREEN_SIZE = (300, 500)

def sigmoid(x):
    return 1/(1+np.exp(-x))
def ReLU(x):
    x[x<0]=0
    return x
def nothing(x):
    return x


# create Player class
class Player():
	def __init__(self, color):
		self.color = color
		self.y = 100
		self.x = 150
		self.vel_x = -1
		self.vel_max = 5
		self.radius = 10

	def draw(self, surface):
		self.collision_mask = pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 10)

	def step(self):
		self.x += self.vel_x

	def touch(self, obstacle):
		return self.collision_mask.colliderect(obstacle.collision_mask)

# create obstacle class
class Obstacle():
	def __init__(self, color, x, y):
		self.color = color
		self.x = x
		self.y = y
		self.vel_y = -2
		self.rect = Rect(self.x, self.y, 10, 15)

	def draw(self, surface):
		self.collision_mask = pygame.draw.rect(surface, self.color, self.rect)

	def step(self):
		self.y += self.vel_y
		self.rect.y = self.y


"""
	# enemy
	#rectangle = Rect(50, 150, 10, 10)

		#pygame.draw.rect(background, OBSTACLE_COLOR, rectangle)
		#rectangle = rectangle.move(1, 1)
"""


def game_loop(agent, details, wait_clock):
	# blit background to screen
	screen.blit(background, (0, 0))
	pygame.display.flip()

	# init clock
	clock = pygame.time.Clock()

	# init player
	player = Player(PLAYER_COLOR)

	# init obstacles
	obstacles = list()

	# start game-loop
	fitness, score_old = (0, 0)
	while True:
		# 1 wait time
		clock.tick(wait_clock)

		# 2 check if agents wants to change direction
		observations = [] # create inputs
		for obstacle in obstacles:
			observations.append(obstacle.x - player.x)
			observations.append(player.y - obstacle.y)
		while len(observations) < 100:
			observations.append(0)
		observations = np.array(observations)

		if agent.neural_network.propagate(observations) > 0.5: # take action
				if player.vel_x == 1:
					player.vel_x = -1
				else:
					player.vel_x = 1

		# 3 check for collision and calculate next step
		if player.x - player.radius < 0 or player.x + player.radius > SCREEN_SIZE[0]: # check for collision with edge
			return fitness
		for obstacle in obstacles: # check for collision with obstacles
			if player.touch(obstacle):
				return fitness

		player.step()
		for obstacle in obstacles:
				obstacle.step()
		fitness += 0.5
		if fitness % 5 == 0:
			score_old = fitness


		# 4 remove old obstacles and create new
		new_line = True
		for obstacle in obstacles:
			if obstacle.y < -10:
				obstacles.remove(obstacle)
			elif obstacle.y > SCREEN_SIZE[1] - 50:
				new_line = False
		if new_line: # generate new line of obstacles
			for i in range(random.randint(0, 5)):
				obstacles.append(Obstacle(OBSTACLE_COLOR, random.randint(0, SCREEN_SIZE[0]), SCREEN_SIZE[1] + 20))




		# 5 clear screen for next rendering
		background.fill(BACKGROUND_COLOR)

		# 6 render simulation to screen
		player.draw(background) # draw player
		for obstacle in obstacles:
			obstacle.draw(background) # draw obstacle
		for obstacle in obstacles: # draw lines to player
			pygame.draw.line(background, (255, 0, 0), (player.x, player.y), (obstacle.x, obstacle.y), width=1)
		# draw score
		text = score_font.render("Score: " + str(score_old), 1, (0, 0, 50))
		textpos = text.get_rect(centerx = background.get_width()/2, centery = 50)
		background.blit(text, textpos)

		# draw agent number
		text = small_font.render("Generation: " + str(details[0] + 1), 1, (0, 0, 50))
		textpos = text.get_rect(centerx = 40, centery = background.get_height() - 40)
		background.blit(text, textpos)

		# draw generation number individual_number
		text = small_font.render("Individual: " + str(details[1] + 1), 1, (0, 0, 50))
		textpos = text.get_rect(centerx = 40, centery = background.get_height() - 20)
		background.blit(text, textpos)

		# 7 draw everything to screen
		screen.blit(background, (0, 0))
		pygame.display.flip()



if __name__ == '__main__':
	random.seed(17)

	pygame.init()
	screen = pygame.display.set_mode(SCREEN_SIZE)
	pygame.display.set_caption('Chilly Snow')

	# draw background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill(BACKGROUND_COLOR)

	# create fonts
	if pygame.font:
		score_font = pygame.font.Font(None, 36)
		small_font = pygame.font.Font(None, 20)

	# generational algorithm
	import neft

	generations = 1000
	pop_size = 100
	threshold = 3000
	wait = 120
	network = [[100,100,sigmoid], [None,100,sigmoid], [None,1,sigmoid]]

	# generate agents
	agents = neft.generate_agents(pop_size, network)

	# run for amount of generations
	for i in range(generations):
		print("***** Generation", str(i), "*****")
		for index, agent in enumerate(agents):
			agent.fitness = game_loop(agent, (i, index), wait_clock = wait)
		# Fakten ueber Generation ausgeben
		summe = 0
		for agent in agents:
			summe += agent.fitness
		summe = summe / len(agents)
		agents_sorted = sorted(agents, key=lambda agent: agent.fitness, reverse=True)
		print("Durchschnittliche Fitness der Population:", summe)
		print("Beste Fitness", agents_sorted[0].fitness)
		print("Population von", pop_size)
		# ab bestimmter Fitness aufhoeren
		if summe >= threshold:
			print("Grenze erreicht ab Generation:", str(i))
			break
		# Reproduktion fuer die naechste Generation
		agents = neft.selection(agents)
		agents = neft.crossover(agents,network,pop_size)
