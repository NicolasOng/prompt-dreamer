import matplotlib.pyplot as plt
import numpy as np

# The fitness data
aqua_m_fitness = [
    [0.24, 0.24, 0.24, 0.32, 0.12],
    [0.32, 0.24, 0.32, 0.28, 0.32],
    [0.28, 0.32, 0.36, 0.32, 0.48],
    [0.2, 0.32, 0.32, 0.4, 0.24],
    [0.32, 0.24, 0.36, 0.28, 0.28]
]

mbpp_m_fitness = [
    [0.2, 0.24, 0.2, 0.32, 0.2],
    [0.28, 0.28, 0.24, 0.24, 0.24],
    [0.28, 0.24, 0.36, 0.24, 0.24],
    [0.32, 0.32, 0.28, 0.32, 0.12],
    [0.28, 0.28, 0.4, 0.24, 0.28]
]

def visualize_fitness(fitness, dataset):
    # Convert to NumPy array for easier manipulation
    fitness_array = np.array(fitness)

    # Compute average, min, and max per column
    average = np.mean(fitness_array, axis=0)
    min_vals = np.min(fitness_array, axis=0)
    max_vals = np.max(fitness_array, axis=0)

    # Plotting
    x = np.arange(fitness_array.shape[1])

    plt.figure(figsize=(10, 6))
    for i, row in enumerate(fitness_array):
        plt.plot(x, row, linestyle='--', alpha=0.4, label=f'Prompt {i+1}')

    plt.plot(x, average, color='blue', label='Average', linewidth=2)
    plt.plot(x, min_vals, color='green', linestyle=':', label='Min', linewidth=2)
    plt.plot(x, max_vals, color='red', linestyle=':', label='Max', linewidth=2)

    plt.title(f"Fitness over Iterations During Multi-Search on Dataset {dataset}")
    plt.xlabel("Population Iteration")
    plt.ylabel("Fitness")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

visualize_fitness(aqua_m_fitness, "aqua")
visualize_fitness(mbpp_m_fitness, "mbpp")
