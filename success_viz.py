import matplotlib.pyplot as plt
import numpy as np

# Binary data
aqua_success = [1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1]
mbpp_success = [0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0]

def viz(data, ds):
    # Convert each value to RGB (Red for 0, Green for 1)
    rgb_data = np.array([[ [1, 0, 0] if val == 0 else [0, 1, 0] for val in data ]], dtype=np.float32)

    # Plot it
    fig, ax = plt.subplots(figsize=(len(data) * 0.3, 0.75))
    ax.imshow(rgb_data, aspect='auto')
    ax.axis('off')
    ax.set_title(f'Successful Prompts Over Time During Single Search on Dataset {ds}', fontsize=10)

    plt.tight_layout()
    plt.show()

viz(aqua_success, "aqua")
viz(mbpp_success, "mbpp")
