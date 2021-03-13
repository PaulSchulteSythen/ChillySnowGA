import random
import numpy as np
from scipy.stats import expon
import gym
import time

def sigmoid(x):
    return 1/(1+np.exp(-x))
def ReLU(x):
    x[x<0]=0
    return x
def nothing(x):
    return x

# Neuronales Netz Klasse
class neural_network:
        # Netzwerk initialisieren
        def __init__(self,network): 
            self.weights = []
            self.activations = []
            for layer in network:
                if layer[0] == None:
                    input_size = network[network.index(layer)-1][1]
                else:
                    input_size = layer[0]
                output_size = layer[1]
                activation = layer[2] 
                self.weights.append(np.random.randn(input_size,output_size))
                self.activations.append(activation)

        # Einschaetzung des Neuronalen Netzes 
        def propagate(self,data): 
            inputs = data
            for i in range(len(self.weights)):
                z = np.dot(inputs,self.weights[i])
                a = self.activations[i](z)
                inputs = a
            yhat = a
            return yhat


# Agent Klasse 
class Agent:
    def __init__(self,network):
        self.neural_network = neural_network(network)
        self.fitness = 0


# GA-Methoden
def generate_agents(pop_size, network):
    return [Agent(network) for _ in range(pop_size)]

def selection(agents):
    agents = sorted(agents, key=lambda agent: agent.fitness, reverse=True)
    agents = agents[:int(0.5 * len(agents))]
    return agents

def unflatten(flattened,shapes):
    newarray = []
    index = 0
    for shape in shapes:
        size = np.product(shape)
        newarray.append(flattened[index : index + size].reshape(shape))
        index += size
    return newarray

def get_expon_dist_random(n):
    inv_l = 1.0/(n**float(-1))
    x = np.array([i for i in range(0,n)]) 
    p = expon.pdf(x, scale=inv_l)
    rand = np.random.random() * np.sum(p)
    for i, p_i in enumerate(p):
        rand -= p_i
        if rand < 0:
            return i
    return 0

def crossover(agents,network,pop_size):
    offspring = []
    offspring.append(agents[0])
    while(len(offspring) < pop_size):
        parent1 = agents[get_expon_dist_random(len(agents))]
        if np.random.uniform() > 0.75:
            offspring.append(parent1)
        else:
            parent2 = agents[get_expon_dist_random(len(agents))]
            child1 = Agent(network)
            shapes = [a.shape for a in parent1.neural_network.weights]
            genes1 = np.concatenate([a.flatten() for a in parent1.neural_network.weights])
            genes2 = np.concatenate([a.flatten() for a in parent2.neural_network.weights])
            split = random.randint(0,len(genes1)-1)
            child1_genes = np.array(genes1[0:split].tolist() + genes2[split:].tolist())
            child1.neural_network.weights = unflatten(child1_genes,shapes)
            offspring.append(child1)
        offspring[-1] = mutation(offspring[-1])
    return offspring

def mutation(agent):
    if random.uniform(0.0, 1.0) <= 0.1: # 10% Chance auf Mutation
        weights = agent.neural_network.weights
        shapes = [a.shape for a in weights]
        flattened = np.concatenate([a.flatten() for a in weights])
        randint = random.randint(0,len(flattened)-1)
        flattened[randint] = np.random.randn()
        newarray = []
        indeweights = 0
        for shape in shapes:
            size = np.product(shape)
            newarray.append(flattened[indeweights : indeweights + size].reshape(shape))
            indeweights += size
        agent.neural_network.weights = newarray
    return agent



if __name__ == "__main__":
	env = gym.make("CartPole-v1")
	generations = 200
	pop_size = 30
	threshold = 400
	network = [[4,5,sigmoid],[None,1,sigmoid]]
	# zufaellig Agenten initialisieren
	agents = generate_agents(pop_size, network)
	# Generationen entwickeln
	try:
		for i in range(generations):
		        print('****** Generation',str(i),'******\n')
		        start = time.time()
		        for agent in agents:
		            observation = env.reset()
		            agent.fitness = 0
		            for _ in range(1000):
		                env.render()
		                action = agent.neural_network.propagate(observation)
		                if action[0] >= 0.5:
		                    action = 1
		                else:
		                    action = 0
		                observation, reward, done, info = env.step(action)
		                agent.fitness += reward
		                if done:
		                    observation = env.reset()
		                    break
		        # Fakten ueber Generation ausgeben
		        summe = 0
		        for agent in agents:
		            summe += agent.fitness
		        summe = summe / len(agents)
		        agents_sorted = sorted(agents, key=lambda agent: agent.fitness, reverse=True)
		        print("Durchschnittliche Fitness der Population:", summe)
		        print("Beste Fitness", agents_sorted[0].fitness)
		        print("Population von", pop_size)
		        print("Zeit fuer die Generation:", time.time() - start, "Sekunden\n")
		        # ab bestimmter Fitness aufhoeren
		        if summe >= threshold:
		            print("Grenze erreicht ab Generation:", str(i))
		            break
		        # Reproduktion fuer die naechste Generation
		        agents = selection(agents)
		        agents = crossover(agents,network,pop_size)
	except:
		pass
	env.close()