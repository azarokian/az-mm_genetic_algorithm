import numpy as np
import heapq
from scipy.spatial import distance
import random
from lib.Travelling_Salesman_Optimization.genetic import GeneticAlgorithm 
from lib.Travelling_Salesman_Optimization.util import * 

import warnings
warnings.filterwarnings("ignore", message="Creating an ndarray from ragged nested sequences")
warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive, and thus cannot be shown")

def get_key_by_value(dictionary, target_value, store):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return store

store_amount = 3
order_amount = 30

chart_range_x = 100
chart_range_y = 100

# set store locations 
store_locations = {
    'Store A': (10, 20),
    'Store B': (40, 60),
    'Store C': (70, 30)
}

# randomize order locations
order_locations = {}
for order in range(order_amount):
    rand_x = random.randint(0, chart_range_x)
    rand_y = random.randint(0, chart_range_y)
    rand_location = (rand_x, rand_y)
    order_locations.update({f'Order {order}':rand_location})

# Create an empty matrix to store distances between orders and stores
num_stores = len(store_locations)
num_orders = len(order_locations)
distance_matrix = np.zeros((num_orders, num_stores))

# Calculate distances and populate the distance matrix
for i, order_location in enumerate(order_locations.values()):
    for j, store_location in enumerate(store_locations.values()):
        dist = distance.euclidean(order_location, store_location)
        distance_matrix[i][j] = dist

# Define store capacities, input n + 1 = capacity 
store_capacities = {
    'Store A': 9,
    'Store B': 9,
    'Store C': 9
}

# Create a dictionary to keep track of the orders assigned to each store
orders_assigned_count = {store: 0 for store in store_locations.keys()}

# Assign each order to the nearest store with no capacity
# order_assignments = {}
# for i in range(num_orders):
#     closest_store_idx = np.argmin(distance_matrix[i])
#     closest_store = list(store_locations.keys())[closest_store_idx]
#     order_assignments[list(order_locations.keys())[i]] = closest_store

# Assign each order to the nearest store with capacity
# Assumption If more than capacity of orders come in, FIFO
order_assignments = {}
for i in range(num_orders):
    # counter for how many order assignments each store has
    assignment_counter = {}
    for value in order_assignments.values():
        assignment_counter[value] = assignment_counter.get(value, 0) + 1

    # sort lowest to highest distance to every store in case capacity has been reached
    for j in range(len(store_locations)):
        sorted_store_locations = heapq.nsmallest(j + 1, enumerate(distance_matrix[i]), key=lambda x :x[1])

    # assign next closest store to order
    for store in sorted_store_locations:
        closest_store = list(store_locations.keys())[store[0]]

        if assignment_counter.get(closest_store, 0) <= store_capacities[closest_store]:
            order_assignments[list(order_locations.keys())[i]] = closest_store
            break
        else:
            continue


# Print the list of orders per store
for store, orders in order_assignments.items():
    print(f'{store}: {orders}')

# Reconfigure order list to organize based on store
orders_per_store = {}
for order, store in order_assignments.items():
    if store not in orders_per_store:
        orders_per_store[store] = []
    
    orders_per_store[store].append({order:order_locations[order]})

# Add in store locations to orders_per_store dictionary
for store, location in store_locations.items():
    orders_per_store[store].append({store:location})


# Generate proposed solution per store
for store, orders in orders_per_store.items():

    # Convert store assignment of orders for GeneticAlgorithm cities list
    orders_list = [list(value) for d in orders for value in d.values()]
    city_orders_list = read_orders(orders_list)
    
    # Run genetic algorithm with specified parameters
    genetic_algorithm = GeneticAlgorithm(cities=city_orders_list, iterations=100, population_size=50,
                                         elites_num=10, mutation_rate=0.008, greedy_seed=1,
                                         roulette_selection=True, plot_progress=True, store=store_locations[store])
    genetic_algorithm.run()

    # Plot and save route of order delivery per store
    genetic_algorithm.plot(label=store)
    plt.savefig(f'/mnt/c/Users/User/Downloads/{store}.png')

    # Print best distance from results of GA per store
    print(f"BEST DISTANCE FOR STORE {store}:  " + str(genetic_algorithm.best_distance()))

    # Create order sequence per store
    store_in_list = genetic_algorithm.best_chromosome()
    store_in_list = [(int(x.x), int(x.y)) for x in store_in_list]
    index_of_store = store_in_list.index(store_locations[store])
    order_sequence = store_in_list[index_of_store:] + store_in_list[:index_of_store]
    order_sequence_with_order_name = [(x, get_key_by_value(order_locations, x, store)) for x in order_sequence]

    # Print order sequence per store
    print(f'Order Sequence for {store}: ')
    for val in order_sequence_with_order_name:
        print(val)
