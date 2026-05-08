# Import libraries for traffic flow calculations
import numpy as np
import random

# Functions for traffic flow and optimization

def make_prediction(transition_matrix, traffic_vector, entrants=np.array([0,0,0,0])):
    # Predict new traffic: TM^T @ current_traffic + entrants
    return (transition_matrix.T @ traffic_vector) + entrants

# Calculate new queue from inflow and outflow
def get_queue(inflow=0, saturation=None, green_time=0):
    # Outflow based on saturation flow during green time
    if saturation is None:
        if np.isscalar(inflow):
            saturation = random.randint(1600, 2500)
        else:
            saturation = np.array([random.randint(1600, 2500) for _ in range(len(inflow))])
    outflow = np.ceil((saturation / 3600) * green_time)
    return np.clip(inflow - outflow, 0, None)

# Allocate green time based on priority ratio of demand and queue
def get_green_time(queue=0, alpha=1, beta=2, demand=0, demands=[], cycle_time=180, lost_time=(random.randint(6, 8)+0.5)):
    # Priority ratio: weighted sum / total weighted sums across intersections
    priority_ratio = (alpha * demand + beta * queue) / max(sum(alpha * int(d) + beta * queue for d in demands), 1)
    return priority_ratio * (cycle_time - lost_time)

# Calculate weighted probability for traffic movement based on adjacency, capacity, green time, and congestion
def get_weighted_probability(adjacency=0, traffic=0, capacity=0, green_time=0, travel_time=random.randint(1800, 3600), congestion=0):
    congestion_ratio = (traffic + int(congestion)) / capacity
    return (adjacency * capacity * green_time) / (travel_time * (1 + congestion_ratio))

# Normalize probability to ensure row sums to 1
def normalise_probability(weighted_probability, total_weighted_probability):
    if total_weighted_probability == 0:
        return 0
    return weighted_probability / total_weighted_probability

# Generate transition matrix and update queues based on current conditions
def generate_transition_matrix(transition_matrix, adjacency_matrix, capacity_matrix, org_queue, traffic_vector, prediction, rows=0, cols=0):
    probabilities = [[0 for _ in range(cols)] for _ in range(rows)]
    green_times = []

    # Calculate green times for each intersection
    for i in range(len(transition_matrix)):
        green_times.append(get_green_time(queue=int(org_queue[i]), demand=int(prediction[i]), demands=prediction))
        for j in range(len(transition_matrix[i])):
            probabilities[i][j] = get_weighted_probability(
                adjacency=int(adjacency_matrix[i][j]),
                traffic=int(traffic_vector[j]),
                capacity=int(capacity_matrix[j]),
                green_time=green_times[i],
                congestion=org_queue[j]
            )

    # Normalize probabilities per row
    for i in range(len(transition_matrix)):
        row_sum = sum(probabilities[i])
        for j in range(len(transition_matrix[i])):
            probabilities[i][j] = normalise_probability(probabilities[i][j], row_sum)

    # Update queues
    queue = get_queue(inflow=traffic_vector, green_time=np.array(green_times))
    return probabilities, queue

def tabulate(n, *traffic, table=None):
    # Append iteration and traffic data to table
    table[0].append(n)
    table[1].append(traffic[0][0])
    table[2].append(traffic[0][1])
    table[3].append(traffic[0][2])
    table[4].append(traffic[0][3])

# Generate random traffic vectors for different scenarios
def define_traffic(normal_traffic, high_traffic, low_traffic):
    traffic = random.randint
    if normal_traffic:
        return np.array([traffic(0, 100) for _ in range(4)])
    elif high_traffic:
        return np.array([traffic(0, 1000) for _ in range(4)])
    elif low_traffic:
        return np.array([traffic(0, 50) for _ in range(4)])

# Set up traffic simulation based on user input
def set_traffic_simulation():
    situation = input("Enter traffic situation (normal, high, low): ")
    if situation.lower() == "normal":
        traffic_vector = define_traffic(True, False, False)
        def get_entrants():
            return define_traffic(True, False, False)
        queue = define_traffic(True, False, False)
        return traffic_vector, queue, get_entrants
    elif situation.lower() == "high":
        traffic_vector = define_traffic(False, True, False)
        def get_entrants():
            return define_traffic(False, True, False)
        queue = define_traffic(False, True, False)
        return traffic_vector, queue, get_entrants
    elif situation.lower() == "low":
        traffic_vector = define_traffic(False, False, True)
        def get_entrants():
            return define_traffic(False, False, True)
        queue = define_traffic(False, False, True)
        return traffic_vector, queue, get_entrants