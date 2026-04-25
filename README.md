# traffic-control-and-optimization

# Open with VScode or any IDE
# in your project directory, run these commands in the terminal
# make a virtual environment
windows -> python -m venv "any name of choice"
linux -> python3 -m venv "any name of choice"

# this installs all required python libraries
pip install -r requirements.txt

# Guide
Section 1: Traffic Flow
Traffic flow theory models the movement of vehicles through a road network. The system is represented as a directed graph where intersections form nodes and roads form edges, each characterised by capacity, flow, and cost per unit time.

1.1 Graph-Based Network Representation
The road network is modelled as a bidirectional graph G = (V, E) where:
•	V = set of intersections (nodes / vertices)
•	E = set of road segments (edges / links)
•	Each edge (i, j) has: capacity u_ij, flow f_ij, and travel cost t_ij

1.1.1 Adjacency Matrix
The network topology is encoded in an adjacency matrix A, which is a core linear algebra construct:
A[i][j] = 1  if road exists from i to j, else 0	Adjacency Matrix

A (Adjacency)	n x n matrix; A[i][j] = 1 if edge exists, 0 otherwise
Bidirectional	A[i][j] = 1 implies A[j][i] = 1 for undirected roads

The adjacency matrix is symmetric for undirected graphs. For directed (one-way) roads, A may be asymmetric.

1.1.2 Transition Matrix (Driver Movement)
Driver route choices are modelled using a stochastic transition matrix P(t):
P(t) = [p_ij(t)]	Transition Matrix

Properties of the transition matrix:
•	p_ij >= 0  for all i, j   (non-negative probabilities)
•	Sum_j p_ij = 1  for all i   (rows are probability distributions)
•	p_ij = 0  if a_ij = 0   (no movement on non-existent roads)

P(t) is a row-stochastic matrix — each row sums to 1, making it a valid probability distribution over next destinations from each node.

1.2 Flow Conservation Law
At each intersection (node), the fundamental principle of conservation must hold. This is analogous to Kirchhoff's current law in electrical circuits:

Inflow + Supply = Outflow + Demand	Conservation Law

The relationship between demand and supply determines the operating regime:

Demand > Supply	Congestion — vehicles queue and cannot enter the link
Supply < Demand	Smooth flow — capacity is not saturated
Supply = Demand	Equilibrium / Critical operating point

1.3 Traffic Redistribution Equation
The traffic state vector x(t) is a column vector representing the number of vehicles at each intersection at time t:
x(t) = [x_i(t)]	State Vector

Traffic redistribution follows the matrix equation:
x(t+1) = P(t)^T  x(t) + s(t)	Redistribution / Prediction

Where:
•	P(t)^T is the transpose of the transition matrix
•	x(t) is the current traffic state vector
•	s(t) accounts for new cycle inflow (new vehicles entering)
•	The result redistributes exiting vehicles and adds new arrivals

This is a linear dynamical system: x(t+1) = A x(t) + b(t), where A = P(t)^T. The system evolves through successive matrix-vector multiplication, which is a fundamental operation in linear algebra.

1.3.1 Prediction Model
A simplified prediction model for next-step traffic state:
x_next = P^T  x_prev	Prediction Model

Steps in applying the prediction model:
•	1. Check capacity constraints at each node
•	2. Compare demand vs supply at each link
•	3. Apply prediction to get next state
•	4. Update queue sizes accordingly

1.4 Queue Growth Model
1.4.1 Queue Dynamics Equation
The queue at intersection i evolves according to:
Q_i(t+1) = Q_i(t) + I_i(t) - mu_i(t)	Queue Growth

Q_i(t)	Queue length at node i at time t (existing queue)
I_i(t)	Inflow: vehicles arriving at node i in cycle t
mu_i(t)	Discharge rate: vehicles leaving node i in cycle t

1.4.2 Discharge Rate
The discharge rate (outflow) depends on the saturation flow rate and green time:
mu_i(t) = S_i * g_i(t)	Discharge Rate

S_i	Saturation flow rate at node i (vehicles per hour, e.g. 1900 veh/h)
g_i(t)	Green time allocated at cycle t (seconds)

The saturation flow rate S_i represents the maximum throughput of a road under ideal conditions. Typical values range from 1600-2000 vehicles per hour per lane.

1.4.3 Congestion Ratio
The congestion ratio at node i measures how loaded the intersection is relative to its capacity:
rho_i(t) = x_i(t) + Q_i(t)  /  u_i	Congestion Ratio

rho_i(t)	Congestion ratio at node i (dimensionless, 0 to 1+)
x_i(t)	Current traffic volume at node i
Q_i(t)	Queue length at node i
u_i	Capacity of node i

1.5 Green Time Allocation Formula
Green time is allocated proportionally based on traffic demand and queue length. This is a weighted resource allocation problem:
g_i(t) = [alpha * x_i(t) + beta * Q_i(t)] / [Sum_k (alpha * x_k(t) + beta * Q_k(t))]  *  (C - L)	Green Time Allocation

Where the variables are:
•	alpha — weighting coefficient for current traffic volume
•	beta  — weighting coefficient for queue length
•	C     — total cycle length (seconds)
•	L     — total lost time per cycle (seconds)

This formula is a linear combination (weighted sum) of two traffic metrics, normalised to allocate the available green time (C - L) proportionally. It ensures sum of all green times equals C - L.

1.5.1 Simplified Green Time (Demand-Proportional)
A simpler proportional allocation based on demand alone:
g_i = (d_i / Sum_k d_k) * (C - L)	Proportional Green Time

Additional constraints on green time:
0 <= p_ij <= 1   and   Sum_j g_i + L = C   and   g_i >= g_min   and   Q_i >= 0	Signal Constraints

1.6 Weighted Probability (Route Attractiveness)
The probability of a driver choosing route (i,j) is updated based on route attractiveness, incorporating travel time and congestion:
w_ij(t) = a_ij * C_ij * g_ij(t)  /  [t_ij * (1 + rho_i(t))]	Weighted Probability

w_ij(t)	Unnormalised weight / attractiveness of route (i,j) at time t
a_ij	Adjacency indicator (1 if road exists, 0 otherwise)
C_ij	Capacity of link (i,j)
g_ij(t)	Green time for movement from i to j
t_ij	Travel time on link (i,j)
rho_i(t)	Congestion ratio at origin node i

Higher green time and capacity increase route attractiveness. Higher travel time and congestion decrease it. This creates a feedback loop where congested routes become less preferred.

1.6.1 Normalised Transition Probability Update
Driver probabilities are updated at each cycle by normalising the weights:
p_ij(t+1) = w_ij(t)  /  Sum_j w_ij(t)	Normalised Probability Update

Interpretation:
•	More green time → higher probability of choosing that route
•	More congestion → lower probability (drivers divert)
•	Ensures sum of probabilities from each node remains 1
Section 2: Traffic Optimisation
Optimisation in traffic systems aims to minimise congestion, reduce delays, and improve overall network throughput. The approach combines signal timing optimisation, route diversion, and multi-objective mathematical programming.

2.1 Overview and Objective
The primary objective is to minimise total congestion across the network, measured as queue length and/or waiting/delay time:
min Z = Sum_i Q_i	Primary Objective

Alternative formulation minimising excess demand over capacity:
min Z = Sum_i max(0, d_i - c_i)	Excess Demand Objective

Combined multi-objective formulation balancing queues and delays:
min Z = Sum_i Q_i  +  lambda * Sum_i W_i	Multi-Objective

Q_i	Queue length at intersection i (primary congestion measure)
W_i	Total waiting / delay time at intersection i
lambda	Weighting factor: small lambda focuses on queues; large lambda focuses on delay

Lambda (weighting factor): A small lambda value focuses the optimisation primarily on minimising queue lengths. A large lambda shifts focus to reducing driver waiting/delay time. The choice depends on the operational priority.

2.2 Signal Timing Optimisation
The core principle of signal timing optimisation is that green time must be proportional to demand:
g_i proportional to d_i  (demand)   OR   g_i proportional to Q_i  (queue)	Signal Timing Principle

This leads to the full allocation formula (repeated from Section 1.5 for completeness):
g_i(t) = [alpha * x_i(t) + beta * Q_i(t)] / [Sum_k (alpha * x_k(t) + beta * Q_k(t))]  *  (C - L)	Green Time (Optimisation Form)

2.2.1 Feasibility Constraints
Signal timing must satisfy the following linear constraints:
Sum_i g_i + L = C	Cycle Length Constraint
g_i >= g_min  for all i	Minimum Green Constraint
0 <= g_i <= C - L  for all i	Bound Constraint

These constraints form a feasible set that is a convex polytope in R^n (where n is the number of signals). The optimisation seeks a point in this set that minimises the objective function.

2.3 Route Diversion Strategy
When intersections become congested, the system redirects drivers away from saturated nodes. This is a network flow optimisation decision:
•	Identify congested intersections: Q_i > threshold
•	Compute alternative routes via less-congested paths
•	Update transition matrix P(t) to favour diverted routes
•	Re-run prediction and update queue states

Route diversion changes the off-diagonal entries of the transition matrix P(t), redistributing probability mass away from congested routes. This is equivalent to modifying the stochastic matrix while preserving the row-sum = 1 property.

2.4 Probability-Based Driver Behaviour Model
2.4.1 Route Selection Probability
The probability p_ij that a driver at node i selects link (i,j) depends on:
•	Historical usage patterns (past route choices)
•	Current congestion ratio rho_i(t) on the link
•	Capacity C_ij of the link
•	Travel time t_ij on the link

Formal dependence structure:
p_ij proportional to  C_ij / [t_ij * b_ij * (1+P)]	Route Selection Probability

b_ij	Base travel time or friction factor for link (i,j)
P	Congestion penalty factor (increases with congestion ratio)

2.4.2 Stochastic Matrix Properties
The transition matrix P(t) must always satisfy:
p_ij >= 0   and   Sum_j p_ij = 1   and   p_ij = 0 if a_ij = 0	Stochastic Constraints

These three conditions ensure:
•	Non-negativity: probabilities cannot be negative
•	Row-stochastic: all probability mass is conserved (vehicles must go somewhere)
•	Structural: drivers cannot use roads that do not exist

2.5 Optimisation Algorithm
The complete iterative optimisation algorithm (Question 6) is structured as follows:

ALGORITHM: Traffic Flow Optimisation
───────────────────────────────────────────────────────
START
  Initialise: x(0), Q(0), P(0)
  FOR i FROM 1 TO 100, INCREMENT BY 1
    CALL function_cv(i)
    // Inside function_cv:
    1. Compute green times g_i(t) via allocation formula
    2. Predict next traffic state: x(t+1) = P(t)^T x(t) + s(t)
    3. Update queues: Q_i(t+1) = Q_i(t) + I_i(t) - mu_i(t)
    4. Compute congestion ratios rho_i(t)
    5. Update weights w_ij(t) and normalise to get P(t+1)
    6. Evaluate objective Z = Sum Q_i + lambda * Sum W_i
    7. If congestion detected: redirect some drivers
  END FOR
END

2.6 Linear Algebra Concepts Summary
The following table summarises all key linear algebra structures used in the traffic flow and optimisation model:

Concept	Mathematical Object	Role in Traffic Model
Adjacency Matrix	A ∈ {0,1}^(n×n)	Encodes road network topology; A[i][j]=1 if road exists
State Vector	x(t) ∈ R^n	Vehicle counts at each intersection at time t
Transition Matrix	P(t): row-stochastic	Driver route probabilities; rows sum to 1
Matrix Transpose	P(t)^T	Used in redistribution equation x(t+1) = P^T x(t) + s(t)
Linear Dynamical System	x(t+1) = Ax(t) + b	Core traffic evolution equation
Weighted Sum / Linear Combo	g_i = w_i · v / ||w||_1 × (C-L)	Green time allocation formula
Stochastic Normalisation	p_ij = w_ij / Sum_j w_ij	Converts weights to valid probabilities
Objective Function	min Z = Sum Q_i + λ Sum W_i	Scalar-valued function to minimise
Constraint Set (Polytope)	Sum g_i + L = C, g_i >= g_min	Feasible region for signal optimisation
Congestion Vector	ρ(t) ∈ R^n	Per-node congestion ratios; element-wise computation


2.7 Complete Equation Reference
All equations from both Flow and Optimisation sections, consolidated for reference:

Flow Equations:
x(t+1) = P(t)^T * x(t) + s(t)	Traffic Redistribution

Q_i(t+1) = Q_i(t) + I_i(t) - mu_i(t)	Queue Update

mu_i(t) = S_i * g_i(t)	Discharge Rate

rho_i(t) = [x_i(t) + Q_i(t)] / u_i	Congestion Ratio

Allocation Equations:
g_i(t) = [alpha*x_i(t) + beta*Q_i(t)] / [Sum_k(alpha*x_k + beta*Q_k)] * (C-L)	Green Time

w_ij(t) = a_ij * C_ij * g_ij(t) / [t_ij * (1 + rho_i(t))]	Route Weight

p_ij(t+1) = w_ij(t) / Sum_j w_ij(t)	Prob. Update

Optimisation Equations:
min Z = Sum_i Q_i  +  lambda * Sum_i W_i	Multi-Objective

Sum_i g_i + L = C   and   g_i >= g_min   and   Q_i >= 0	Constraints

min Z(z) = Sum_i max(0, d_i - c_i)	Excess Demand Min.
