import random
import time
import math # Needed for Radix Sort
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Main Visualization Engine ---

def visualize_sorting(algorithm_name, generator_func, num_elements):
    """
    Main function to set up the Matplotlib figure and animation.
    
    Args:
        algorithm_name (str): The name of the sorting algorithm for the title.
        generator_func (generator): A generator function that yields a 
                                     dictionary with the current state.
        num_elements (int): The number of elements in the list.
    """
    
    # --- Setup ---
    sorter_generator = generator_func() 
    n = num_elements                   
    
    # Get the initial full list from the first yield
    try:
        initial_frame = next(sorter_generator)
        initial_list = initial_frame['list_state']
    except StopIteration:
        print("Generator is empty!")
        return

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('#f0f0f0') 
    ax.set_facecolor('#333333') 
    
    ax.set_title(f"{algorithm_name} Visualization", fontsize=16, color='white')
    ax.set_xlabel("Index", fontsize=12, color='white')
    ax.set_ylabel("Value", fontsize=12, color='white')
    
    # Set tick colors
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    
    # Set spine colors
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    # Create the initial bar chart
    bar_rects = ax.bar(range(len(initial_list)), initial_list, align="edge", color='#95a5a6')
    
    # Set axis limits
    ax.set_xlim(-1, n)
    ax.set_ylim(0, int(max(initial_list) * 1.1)) # Use max value for Radix sort
    
    # Text to display the number of operations
    text = ax.text(0.01, 0.95, "", transform=ax.transAxes, fontsize=12, color='white',
                   bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))
    
    operation_count = [0] 
    start_time = [time.time()] 

    # --- Animation Function ---
    def update_fig(frame_data, rects, op_count):
        """
        This function is called for each frame of the animation.
        It updates the height and color of the bars based on the yielded dictionary.
        """
        op_count[0] += 1
        
        # Get data from the frame
        data_list = frame_data['list_state']
        
        # Use sets for fast lookups
        sorted_set = set(frame_data.get('sorted', []))
        red_set = set(frame_data.get('red', []))
        orange_set = set(frame_data.get('orange', []))
        blue_set = set(frame_data.get('blue', []))
        
        # Update bar heights and colors
        for i, (rect, height) in enumerate(zip(rects, data_list)):
            rect.set_height(height)
            
            # Color logic
            if i in sorted_set:
                rect.set_color('#2ecc71') # Green (sorted)
            elif i in red_set:
                rect.set_color('#e74c3c') # Red (comparison/swap)
            elif i in orange_set:
                rect.set_color('#f39c12') # Orange (pivot/key/pass)
            elif i in blue_set:
                rect.set_color('#3498db') # Blue (range/pointers)
            else:
                rect.set_color('#95a5a6') # Grey (default)

        # Update the operations counter text
        elapsed_time = time.time() - start_time[0]
        pass_info = frame_data.get('pass_info', '')
        text.set_text(f"Operations: {op_count[0]} | Time: {elapsed_time:.2f}s\n{pass_info}")
        return (*rects, text) # Return all artists that were updated

    # --- Run Animation ---
    ani = animation.FuncAnimation(
        fig,
        update_fig,
        frames=sorter_generator,
        fargs=(bar_rects, operation_count),
        blit=True,
        repeat=False,
        interval=10, 
    )

    plt.tight_layout() 
    plt.show()

# --- Sorting Algorithm Generators ---

def bubble_sort_gen(n=50):
    data = random.sample(range(1, n + 1), n)
    sorted_indices = []
    yield {'list_state': data.copy(), 'sorted': sorted_indices}

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            yield {'list_state': data.copy(), 'sorted': sorted_indices, 'red': [j, j+1]}
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
                yield {'list_state': data.copy(), 'sorted': sorted_indices, 'red': [j, j+1]}
        sorted_indices.append(n - i - 1)
        if not swapped:
            break
    sorted_indices = list(range(n))
    yield {'list_state': data.copy(), 'sorted': sorted_indices}
    return data

def insertion_sort_gen(n=50):
    data = random.sample(range(1, n + 1), n)
    sorted_indices = [0]
    yield {'list_state': data.copy(), 'sorted': sorted_indices}

    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        sorted_indices = list(range(i))
        while j >= 0 and key < data[j]:
            yield {'list_state': data.copy(), 'sorted': sorted_indices, 'orange': [i], 'red': [j]}
            data[j + 1] = data[j]
            j -= 1
            yield {'list_state': data.copy(), 'sorted': sorted_indices, 'orange': [i], 'red': [j+1]}
        data[j + 1] = key
        yield {'list_state': data.copy(), 'sorted': sorted_indices, 'orange': [i], 'red': [j+1]}
    yield {'list_state': data.copy(), 'sorted': list(range(n))}
    return data

def quick_sort_gen(n=50):
    data = random.sample(range(1, n + 1), n)
    sorted_indices = []
    stack = [(0, n - 1)]
    yield {'list_state': data.copy(), 'sorted': sorted_indices}

    while stack:
        low, high = stack.pop()
        if low >= high:
            if low == high:
                sorted_indices.append(low)
            continue
        pivot_idx = high 
        pivot_val = data[pivot_idx]
        i = low - 1
        yield {'list_state': data.copy(), 'sorted': sorted_indices, 'orange': [pivot_idx], 'blue': list(range(low, high))}
        for j in range(low, high):
            yield {'list_state': data.copy(), 'sorted': sorted_indices, 'orange': [pivot_idx], 'red': [j], 'blue': [i+1]}
            if data[j] <= pivot_val:
                i += 1
                data[i], data[j] = data[j], data[i]
                yield {'list_state': data.copy(), 'sorted': sorted_indices, 'orange': [pivot_idx], 'red': [i, j], 'blue': [i]}
        data[i + 1], data[pivot_idx] = data[pivot_idx], data[i + 1]
        final_pivot_pos = i + 1
        sorted_indices.append(final_pivot_pos)
        yield {'list_state': data.copy(), 'sorted': sorted_indices, 'orange': [final_pivot_pos]}
        stack.append((low, final_pivot_pos - 1))
        stack.append((final_pivot_pos + 1, high))
    yield {'list_state': data.copy(), 'sorted': list(range(n))}
    return data

def merge_sort_gen(n=50):
    data = random.sample(range(1, n + 1), n)
    sorted_indices = []
    
    def merge_sort_recursive(arr, l, r):
        if l < r:
            m = (l + r) // 2
            yield from merge_sort_recursive(arr, l, m)
            yield from merge_sort_recursive(arr, m + 1, r)
            L = arr[l : m+1]
            R = arr[m+1 : r+1]
            i, j, k = 0, 0, l
            while i < len(L) and j < len(R):
                yield {'list_state': arr.copy(), 'sorted': sorted_indices, 'blue': list(range(l, r+1)), 'red': [l+i, m+1+j]}
                if L[i] <= R[j]:
                    arr[k] = L[i]
                    i += 1
                else:
                    arr[k] = R[j]
                    j += 1
                k += 1
                yield {'list_state': arr.copy(), 'sorted': sorted_indices, 'blue': list(range(l, r+1)), 'red': [k-1]}
            while i < len(L):
                arr[k] = L[i]
                yield {'list_state': arr.copy(), 'sorted': sorted_indices, 'blue': list(range(l, r+1)), 'red': [k]}
                i += 1
                k += 1
            while j < len(R):
                arr[k] = R[j]
                yield {'list_state': arr.copy(), 'sorted': sorted_indices, 'blue': list(range(l, r+1)), 'red': [k]}
                j += 1
                k += 1
            if l == 0 and r == n - 1:
                sorted_indices.extend(list(range(n)))

    yield {'list_state': data.copy(), 'sorted': sorted_indices}
    yield from merge_sort_recursive(data, 0, n - 1)
    yield {'list_state': data.copy(), 'sorted': list(range(n))}
    return data

def heap_sort_gen(n=50):
    data = random.sample(range(1, n + 1), n)
    sorted_indices = []

    def heapify_gen(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        red_nodes = [x for x in [l, r] if x < n]
        yield {'list_state': arr.copy(), 'sorted': sorted_indices, 'orange': [i], 'red': red_nodes}
        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            yield {'list_state': arr.copy(), 'sorted': sorted_indices, 'red': [i, largest]}
            yield from heapify_gen(arr, n, largest)

    yield {'list_state': data.copy(), 'sorted': sorted_indices}
    for i in range(n // 2 - 1, -1, -1):
        yield from heapify_gen(data, n, i)
    for i in range(n - 1, 0, -1):
        data[i], data[0] = data[0], data[i]
        sorted_indices.append(i)
        yield {'list_state': data.copy(), 'sorted': sorted_indices, 'red': [0, i]}
        yield from heapify_gen(data, i, 0)
    sorted_indices.append(0)
    yield {'list_state': data.copy(), 'sorted': sorted_indices}
    return data

def radix_sort_gen(n=50):
    """
    Generator for Radix Sort (LSD).
    This visualization is not in-place, so the bars will "jump" 
    as they are gathered from the buckets.
    """
    # Radix sort works better with a wider range of numbers
    data = random.sample(range(1, n*3 + 1), n) 
    max_val = max(data)
    
    # Initial state
    yield {'list_state': data.copy(), 'sorted': []}

    exp = 1
    while max_val // exp > 0:
        pass_info = f"Sorting by {exp}s place"
        
        # 1. Distribution Pass (Bucketing)
        buckets = [[] for _ in range(10)] # 10 buckets for 10 digits
        
        for i in range(n):
            item = data[i]
            digit = (item // exp) % 10
            buckets[digit].append(item)
            # Yield to show which item is being processed
            yield {'list_state': data.copy(), 'red': [i], 'pass_info': pass_info}

        # 2. Gathering Pass (Re-collecting)
        k = 0 # Index for the main data list
        
        for i in range(10): # For each bucket
            pass_info_bucket = f"{pass_info} (Bucket {i})"
            for item in buckets[i]:
                data[k] = item
                # Yield to show the item being placed back
                yield {'list_state': data.copy(), 'orange': [k], 'pass_info': pass_info_bucket}
                k += 1
        
        exp *= 10 # Move to the next digit (10s, 100s, etc.)

    # Final sorted state
    yield {'list_state': data.copy(), 'sorted': list(range(n)), 'pass_info': "Sorted!"}
    return data


# --- Main execution ---
if __name__ == "__main__":
    random.seed(42)
    N_ELEMENTS = 75 
    
    print("--- Sorting Algorithm Visualizer ---")
    print("1: Bubble Sort")
    print("2: Insertion Sort")
    print("3: Quick Sort")
    print("4: Merge Sort")
    print("5: Heap Sort")
    print("6: Radix Sort (LSD)")
    print("--------------------------------------")
    
    choice = input("Enter your choice (1-6): ")
    
    algorithms = {
        "1": ("Bubble Sort", lambda: bubble_sort_gen(N_ELEMENTS)),
        "2": ("Insertion Sort", lambda: insertion_sort_gen(N_ELEMENTS)),
        "3": ("Quick Sort", lambda: quick_sort_gen(N_ELEMENTS)),
        "4": ("Merge Sort", lambda: merge_sort_gen(N_ELEMENTS)),
        "5": ("Heap Sort", lambda: heap_sort_gen(N_ELEMENTS)),
        "6": ("Radix Sort", lambda: radix_sort_gen(N_ELEMENTS))
    }
    
    if choice in algorithms:
        algo_name, gen_func = algorithms[choice]
        # Pass the generator function AND the number of elements
        visualize_sorting(algo_name, gen_func, N_ELEMENTS)
    else:
        print("Invalid choice. Please run the script again and enter a number from 1 to 6.")