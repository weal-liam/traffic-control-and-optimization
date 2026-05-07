#import necessary libraries such as numpy for matrix operations
import numpy as np

#create functions that make various calculations for traffic flow and optimisation
#1. make_prediction of the new traffic using the product of the transpose of the transition matrix and the traffic vector
# new x = transpose of TM x old x
#use the function below
def make_prediction(transition_matrix, traffic_vector, entrants=np.array([0,0,0,0])):
    #parameters(required input) => transition matrix and traffic vector
    return (transition_matrix.T @ traffic_vector) + entrants # @ is the multiplication symbol for matrices in python's numpy library
    #returns our new inflow vector

#since sometimes the might be an already existing queue as new traffic enters, we combine the existing and new to get all vehicles waiting(total queue)
#to get the total queue, we need the original queue and congestion plus the retained(vehicles that don't make it out of traffic)
# new queue = original queue + conjestion + (inflow - outfow)
#use the function below
def get_queue(inflow=0, saturation=3800, green_time=0):
    #outflow are the vehicles that successfully make it out of traffic
    #these are got from the discharge rate during every green time
    #green time is the time when the light turns green and traffic is moving
    #so discharge rate(outflow) is the amount of cars that move out of an intersection per green time
    #its the product of saturation(vehicles per hour out of an intersection) and green time 
    outflow = ((saturation)/3600) * green_time # saturation is divided by 3600 to convert it to vehicles per second
    #here we get the difference btn inflow and outflow vectors and add it to the sum of existing queue and conjestion (original queue)    
    return np.clip(inflow - outflow, 0, None)
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
    priority_ratio = float((alpha*demand + beta*queue)/max(sum([alpha*int(demand) + beta*queue for demand in demands]), 1))
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
def generate_transition_matrix(transition_matrix, adjacency_matrix, capacity_matrix, org_queue, traffic_vector, prediction, rows=0, cols=0):
    #initialize empty lists for the transition matrix, probabilities, and green times
    probabilities = transition_matrix.copy() #copy the original transition matrix to preserve its structure while we fill in the new probabilities
    green_times = [] #this list will hold the calculated green times for each intersection based on the current traffic conditions and queue sizes

    #calculate the green time for each intersection using the get_green_time function,
    # which allocates green time based on the priority ratio of demand and queue sizes
    #use a loop to iterate through each intersection and calculate the green time based on the combined queue (original queue + congestion) and the demand (traffic vector) for that intersection
    for i in range(len(transition_matrix)):
        #append the calculated green time for each intersection to the green_times list, which will be used later to calculate the weighted probabilities for traffic movement
        green_times.append(get_green_time(queue=int(org_queue[i]),demand=int(prediction[i]), demands=prediction))
        for j in range(len(transition_matrix[i])):
            #calculate the weighted probability for traffic movement from intersection i to j using the get_weighted_probability function,
            # which takes into account the adjacency, traffic volume, capacity, green time, travel time, and congestion for that movement
            probabilities[i][j] = get_weighted_probability(adjacency=int(adjacency_matrix[i][j]),traffic = int(traffic_vector[i]), capacity=int(capacity_matrix[i]), green_time=green_times[i], congestion=org_queue[i])

    #after calculating the weighted probabilities for all possible movements from each intersection,
    #  we need to normalise these probabilities to ensure they sum up to 1 for each intersection
    #use nested loops to iterate through the probabilities matrix and normalise each probability by dividing it by the sum of the probabilities for that intersection (row)
    for i in range(len(transition_matrix)):
        for j in range(len(transition_matrix[i])):
            transition_matrix[i][j] = normalise_probability(probabilities[i][j],sum(probabilities[i]))
    #after generating the transition matrix based on the current traffic conditions and queue sizes,
    #we need to update the queue sizes for each intersection to reflect the new traffic flow and congestion levels
    queue = get_queue(inflow=traffic_vector,green_time=np.array(green_times))
    print("queue",queue)

    #the function returns the generated transition matrix and the updated queue sizes for each intersection,
    # which can be used in subsequent iterations to predict traffic flow and optimise signal timings
    return np.array(transition_matrix), queue

def tabulate(n, *traffic, table=None):
    table[0].append(n)  # Append the current time point (iteration number) to the first row of the table
    table[1].append(traffic[0][0])  # Append the traffic volume for intersection A to the second row of the table
    table[2].append(traffic[0][1])  # Append the traffic volume for intersection B to the third row of the table
    table[3].append(traffic[0][2])  # Append the traffic volume for intersection C to the fourth row of the table
    table[4].append(traffic[0][3])  # Append the traffic volume for intersection D to the fifth row of the table

