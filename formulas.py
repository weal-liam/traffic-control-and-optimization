#import necessary libraries such as numpy for matrix operations
import numpy as np
#import random for random sample values like traffic
import random

#make an adjacency matrix which is the network layout of the traffic network
#this matrix is a bi-directional graph showing the connections between the nodes
adjacency_matrix = np.array([
    [0, 1, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 1, 0]
    ])

#make a transition matrix that will be used to predict, redistribute and organise the traffic flow
#this is a probability matrix that shows the likely direction that traffic will flow such as A to B or A to D but never A to C 
# since there's no connection or route from interection A to intersection C
transition_matrix = np.array([
    [0, 0.5, 0, 0.5],
    [0.5, 0, 0.5, 0],
    [0, 0.5, 0, 0.5],
    [0.5, 0, 0.5, 0]
    ])

#make the vector that holds the incoming traffic into the network's nodes
traffic_vector = np.array(
    [10, 90, 10, 10]
    )

#make a matrix that holds the interesction(node) capacity
capacity_matrix=np.array([700, 800, 700, 600])

#use random to generate new traffic simulating inflow
traffic = random.randint

entrants_vector = np.array(
    [traffic(0,100), traffic(0,100), traffic(0,100), traffic(0,100)]
    )

#make a vector to hold the queue sizes for each node(intersection)
queue=np.array([0,0,0,0])

#create functions that make various calculations for traffic flow and optimisation
#1. make_prediction of the new traffic using the product of the transpose of the transition matrix and the traffic vector
# new x = transpose of TM x old x
#use the function below
def make_prediction(transition_matrix, traffic_vector):
    #parameters(required input) => transition matrix and traffic vector
    return transition_matrix.T @ traffic_vector # @ is the multiplication symbol for matrices in python's numpy library
    #returns our new inflow vector

#since each intersection has a fixed capacity, there will always be congestion if that capacity is exceeded
#To account for it, the difference btn the inflow into and the capacity of an intersection gives the extra vehicles called the congestion
#use the function below
def get_congestion(traffic_vector, capacity_matrix):
    #parameters => traffic vector, capacity matrix
    return np.clip(traffic_vector - capacity_matrix,0,None) # numpy.clip function forces all negative values in the vector to zero so as to avoid negative queues
    #returns the waiting vehicles or excess vehicles that caused the congestion

#since sometimes the might be an already existing queue as new traffic enters, we combine the existing and new to get all vehicles waiting(total queue)
#to get the total queue, we need the original queue and congestion plus the retained(vehicles that don't make it out of traffic)
# new queue = original queue + conjestion + (inflow - outfow)
#use the function below
def get_queue(original_q=0, inflow=0, saturation=3800, green_time=0):
    #outflow are the vehicles that successfully make it out of traffic
    #these are got from the discharge rate during every green time
    #green time is the time when the light turns green and traffic is moving
    #so discharge rate(outflow) is the amount of cars that move out of an intersection per green time
    #its the product of saturation(vehicles per hour out of an intersection) and green time 
    outflow = ((saturation)/3600) * green_time # saturation is divided by 3600 to convert it to vehicles per second
    #here we get the difference btn inflow and outflow vectors and add it to the sum of existing queue and conjestion (original queue)    
    return np.clip(original_q, 0, None) + np.clip(inflow - outflow, 0, None)
    #return new queue

#the green time is the effective time in the full traffic cycle(red light to green and back to red) for traffic to move freely i.e G.T = time - lost time
# lost time is the waste time for other activities like not moving, driver starting move when light is already green, passengers crossing, etc... 
#use the function below
def get_green_time(queue=0, alpha=1, beta=4, demand=0,demands=[], cycle_time=180, lost_time=8.5):
    #on the basis of traffic optimisation, we use a priority ratio that helps assign more green time to congested intersections and less to those not congested
    #But priority can either be given to demand(incoming traffic) or queue(waiting vehicles) hence the weights, alpha and beta
    #these weights leverage priority between demand and queue depending on the system
    #the priority ratio is the weighted sum of demand and queue for a particular intersection divided by the sum of the weighted sums for all intersections
    #so if an intersection has a high demand and queue, it will have a higher priority ratio and thus more green time allocated to it
    #priority ratio = (alpha*demand + beta*queue) / sum of (alpha*demand + beta*queue) for all intersections
    priority_ratio = float((alpha*demand + beta*queue)/sum([alpha*int(demand) + beta*queue for demand in demands]))
    #so for each intersection, green time = priority ratio X overall green time
    return priority_ratio*(cycle_time - lost_time) #return green time for an intersection

#the weighted probability is a measure of the likelihood of traffic moving from one intersection to another
#based on various factors such as adjacency, traffic volume, capacity, green time, travel time and congestion
#the formula for weighted probability is a product of these factors, with congestion penalized heavily to discourage traffic from moving towards congested intersections
#use  the function below
def get_weighted_probability(adjacency=0, traffic=0, capacity=0, green_time=0, travel_time=250, congestion=0):
    #calculate the congestion ratio which is the ratio of total traffic (current traffic + congestion) to the capacity of the intersection
    #a higher congestion ratio indicates a more congested intersection, which should be less attractive for traffic to move towards
    congestion_ratio = (traffic + int(congestion)) / (capacity)

    # Penalize congested destinations heavily
    congestion_penalty = 1 / (1 + congestion_ratio*10)  # Adjust multiplier for sensitivity
    # Lower travel time = higher probability
    travel_time_factor = 1 / (1 + travel_time*0.001)
    
    #the adjacency factor ensures that traffic can only move to adjacent intersections
    #while the other factors influence the likelihood of that movement based on current conditions
    #the formula combines these factors to calculate a weighted probability for traffic movement from one intersection to another,
    #encouraging movement towards less congested and more efficient routes
    return float((adjacency * capacity * green_time * congestion_penalty * travel_time_factor) / ((1 + congestion_ratio)))
    #return the weighted probability

#the normalised probability is the weighted probability divided by the sum of all weighted probabilities for a particular intersection
#this ensures that the probabilities for all possible movements from an intersection sum up to 1,
#making it a valid probability distribution for predicting traffic flow
#use the function below
def normalise_probability(weighted_probability, total_weighted_probability):
    #to avoid division by zero, we check if the total weighted probability is zero and return zero in that case
    if total_weighted_probability == 0:
        return 0
    return weighted_probability/(total_weighted_probability)#return the normalised probability

#the generate_transition_matrix function is the main function that generates the transition matrix
# and updates the queue sizes based on the current traffic conditions and the original queue sizes
#it takes the original queue sizes, traffic vector, and dimensions of the transition matrix as input
#use the function below
def generate_transition_matrix(org_queue, traffic_vector, rows=0, cols=0):
    #initialize empty lists for the transition matrix, probabilities, and green times
    transition_matrix, probabilities, green_times = [], [], []

    #create empty transition matrix and probabilities matrix with the specified dimensions (rows and cols)
    #this is done to prepare for the calculations of the weighted probabilities and the normalised transition matrix based on the current traffic conditions and queue sizes
    #use nested loops to fill the transition matrix and probabilities matrix with zeros as initial values
    for i in range(rows):
        #append empty lists to the transition matrix and probabilities list for each row
        transition_matrix.append([])
        probabilities.append([])
        for j in range(cols):
            #since the transition matrix is a probability matrix that shows the likelihood of traffic moving from one intersection to another, we initialize it with zeros
            transition_matrix[i].append(0)
            probabilities[i].append(0)

    #calculate the congestion for each intersection using the get_congestion function,
    # which gives us the number of vehicles waiting due to congestion based on the current traffic vector and capacity matrix
    queue = get_congestion(traffic_vector, capacity_matrix)
    print("First queue",queue)

    #calculate the green time for each intersection using the get_green_time function,
    # which allocates green time based on the priority ratio of demand and queue sizes
    #use a loop to iterate through each intersection and calculate the green time based on the combined queue (original queue + congestion) and the demand (traffic vector) for that intersection
    for i in range(len(transition_matrix)):
        #append the calculated green time for each intersection to the green_times list, which will be used later to calculate the weighted probabilities for traffic movement
        green_times.append(get_green_time(queue=int(queue[i])+int(org_queue[i]),demand=int(traffic_vector[i]), demands=traffic_vector))
        for j in range(len(transition_matrix[i])):
            #calculate the weighted probability for traffic movement from intersection i to j using the get_weighted_probability function,
            # which takes into account the adjacency, traffic volume, capacity, green time, travel time, and congestion for that movement
            probabilities[i][j] = get_weighted_probability(adjacency=int(adjacency_matrix[i][j]),traffic = int(traffic_vector[i]), capacity=int(capacity_matrix[i]), green_time=green_times[i], congestion=queue[i])

    #after calculating the weighted probabilities for all possible movements from each intersection,
    #  we need to normalise these probabilities to ensure they sum up to 1 for each intersection
    #use nested loops to iterate through the probabilities matrix and normalise each probability by dividing it by the sum of the probabilities for that intersection (row)
    for i in range(len(transition_matrix)):
        for j in range(len(transition_matrix[i])):
            transition_matrix[i][j] = normalise_probability(probabilities[i][j],sum(probabilities[i]))
    #after generating the transition matrix based on the current traffic conditions and queue sizes,
    #we need to update the queue sizes for each intersection to reflect the new traffic flow and congestion levels
    queue = get_queue(original_q=queue, inflow=traffic_vector, saturation=3800, green_time=np.array(green_times))
    print("final",queue)

    #the function returns the generated transition matrix and the updated queue sizes for each intersection,
    # which can be used in subsequent iterations to predict traffic flow and optimise signal timings
    return np.array(transition_matrix), queue

#the main loop of the program simulates the traffic flow and signal optimisation over multiple iterations (100 in this case)
#in each iteration, we generate a new transition matrix based on the current traffic conditions and queue sizes,
# make a prediction for the new traffic vector using the transition matrix, and update the traffic vector for the next iteration
#this loop allows us to observe how the traffic flow evolves over time and how the signal timings can be optimised based on the changing traffic conditions and congestion levels at each intersection
#use the loop below(with n as the iteration counter)
n=0
while(n < 100):
    transition_matrix, queue = generate_transition_matrix(org_queue=queue, traffic_vector=traffic_vector, rows=4, cols=4)
    print("TM:",transition_matrix)

    prediction = make_prediction(transition_matrix=transition_matrix, traffic_vector=traffic_vector)
    traffic_vector = (entrants_vector + prediction).astype(np.int64)

    print("T_V:",traffic_vector)

    n+=1