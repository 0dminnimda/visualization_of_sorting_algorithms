import random
from sortvis import *

length = 2**10
array = list(range(1, length + 1))
# randomize the array
random.shuffle(array)
# or reverse the array
# array = array[::-1]

# sort = BubbleSort
sort = CocktailShakerSort
# sort = MergeSort

visualizer = SortVisualizer()
# visualizer.framerate = 60
visualizer.run(sort, array, ops_per_frame=30)
