import random
import math

# Randomly generates different pathway combinations
def CreateInitialPopulation(size, cities):

    initial_population = []

    for i in range(size):

        initial_population.append(random.sample(range(len(cities)), len(cities)))

    return initial_population

# Simulated Annealing to avoid local minima
def simulated_annealing(cities, initial_solution):
    initial_temp = 1000
    cooling_rate = 0.995
    min_temp = 1
    max_iterations = 1000

    current_solution = initial_solution[:]
    current_distance = calculate_path_distance(current_solution, cities)
    temperature = initial_temp
    best_solution = current_solution[:]
    best_distance = current_distance

    iteration = 0
    while temperature > min_temp and iteration < max_iterations:

        new_solution = current_solution[:]
        i, j = random.sample(range(len(current_solution)), 2)
        new_solution[i], new_solution[j] = new_solution[j], new_solution[i]

        new_distance = calculate_path_distance(new_solution, cities)

        if new_distance < current_distance or random.random() < math.exp(
                (current_distance - new_distance) / temperature):
            current_solution = new_solution[:]
            current_distance = new_distance

            if current_distance < best_distance:
                best_solution = current_solution[:]
                best_distance = current_distance

        temperature *= cooling_rate
        iteration += 1

    return best_solution


# Creates the two parents (one through roulette wheel and one through tourney selection)
def CreateMatingPool(population, RankList):
    matingPool = []

    total_fitness = sum(RankList)
    index_probabilities = []
    for rank in RankList:
        index_probabilities.append(rank / total_fitness)

    selected_indices = random.choices(
        population=population,
        weights=index_probabilities,
        k=2
    )
    matingPool.append(selected_indices[0])
    tournament = random.sample(range(len(population)), 3)
    matingPool.append(population[min(tournament, key=lambda idx: distances[idx])])

    return matingPool

# Creates the child based on the two parents
def Crossover (Parent1, Parent2, Start_Index, End_Index):
    child = [-1] * len(Parent1)
    child[Start_Index::End_Index+1] = Parent1[Start_Index::End_Index+1]

    Current_Index = 0
    for city in Parent2:
        if city not in child:
            while child[Current_Index] != -1:
                Current_Index += 1
            child[Current_Index] = city
    return child

# Randomly mutates the path to add variety
def mutate(path, mutation_rate):
    for i in range(len(path)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(path) - 1)
            path[i], path[j] = path[j], path[i]
    return path

# Calculates how far a path travels
def calculate_path_distance(path, cities):
    distance = 0
    for i in range(len(path) - 1):
        distance += calculate_distance(cities[path[i]], cities[path[i+1]])
    # Add the return to the starting point
    distance += calculate_distance(cities[path[-1]], cities[path[0]])
    return distance


# Basic distance calculator
def calculate_distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2 + (city1[2] - city2[2]) ** 2)


if __name__ == "__main__":

    with open('input.txt', 'r') as file:
        # Read the first line to get the number of cities
        num_cities = int(file.readline().strip())

        if num_cities == 1:
            x, y, z = map(int, file.readline().strip().split())
            with open("output.txt", "w") as file:

                total_distance = 0.000
                file.write(f"{total_distance}\n")
                file.write(f"{x} {y} {z}\n")
                file.write(f"{x} {y} {z}\n")
        else:

            cities = []

            for _ in range(num_cities):

                x, y, z = map(int, file.readline().strip().split())

                cities.append((x, y, z))

            all_children = []
            all_children_distances = []
            count = 0
            population = CreateInitialPopulation(300, cities)  # Creates 300 permutations of paths

            for generation in range(1250):
                count += 1
                if count >= 10:
                    population.append(all_children[all_children_distances.index(min(all_children_distances))])

                    first_half = all_children_distances[: int(len(all_children_distances) / 2)]
                    second_half = all_children_distances[int(len(all_children_distances) / 2):]
                    population.append(all_children[all_children_distances.index(min(first_half))])
                    population.append(all_children[all_children_distances.index(min(second_half))])

                distances = []
                for path in population:
                    totalDistance = calculate_path_distance(path, cities)
                    distances.append(totalDistance)

                if count >= 10:
                    population.pop(distances.index(max(distances)))
                    distances.pop(distances.index(max(distances)))
                    population.pop(distances.index(max(distances)))
                    distances.pop(distances.index(max(distances)))
                    population.pop(distances.index(max(distances)))
                    distances.pop(distances.index(max(distances)))

                theMinDistancePath = population[distances.index(min(distances))]
                all_children.append(theMinDistancePath)
                all_children_distances.append(min(distances))

                distProp = []  # distance proportion
                for distance in distances:
                    distProp.append(1/distance)

                rankList = []
                for prop in distProp:
                    rankList.append(prop)

                for repetition in range(2):

                    matingPool = CreateMatingPool(population, rankList)

                    start_index, end_index = sorted(random.sample(range(len(matingPool[0])), 2))
                    child = Crossover(matingPool[0], matingPool[1], start_index, end_index)

                    child = mutate(child, 0.01)

                    child_distance = calculate_path_distance(child, cities)

                    all_children.append(child)
                    all_children_distances.append(child_distance)

            minDistanceIndex = all_children_distances.index(min(all_children_distances))
            theChild = all_children[minDistanceIndex]

            theChild = simulated_annealing(cities, theChild)

            with open("output.txt", "w") as file:
                total_distance = calculate_path_distance(theChild, cities)
                file.write(f"{total_distance}\n")
                for city_index in theChild:
                    city_coords = cities[city_index]
                    file.write(f"{city_coords[0]} {city_coords[1]} {city_coords[2]}\n")

                start_city_coords = cities[theChild[0]]
                file.write(f"{start_city_coords[0]} {start_city_coords[1]} {start_city_coords[2]}\n")