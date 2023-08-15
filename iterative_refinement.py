#%%
import random
from shapely.ops import cascaded_union
from shapely import affinity
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon, Polygon as ShapelyPolygon

def bounding_area(polygons):
    """Compute the area of the bounding box containing all polygons."""
    total_union = cascaded_union(polygons)
    minx, miny, maxx, maxy = total_union.bounds
    return (maxx - minx) * (maxy - miny)

def random_shift(polygon, max_shift=0.5):
    """Shift a polygon by a random amount within [-max_shift, max_shift] in both x and y directions."""
    dx = random.uniform(-max_shift, max_shift)
    dy = random.uniform(-max_shift, max_shift)
    return affinity.translate(polygon, xoff=dx, yoff=dy)

# Initial placement of polygons - you can use the grid placement or any other method

def generate_valid_irregular_polygon(vertices=8, perturb_strength=0.3):  # Reduced perturb_strength
    while True:
        t = np.linspace(0, 2 * np.pi, vertices, endpoint=False)
        x = np.cos(t)
        y = np.sin(t)

        perturb = 1.0 + perturb_strength * (2 * np.random.rand(vertices) - 1.0)
        x *= perturb
        y *= perturb

        poly = ShapelyPolygon(np.column_stack([x, y]))
        if poly.is_valid:
            return np.column_stack([x, y])

# Generate polygons using the valid polygon generator
num_polygons = 10
polygons = [generate_valid_irregular_polygon(vertices=8) for _ in range(num_polygons)]

# Initialize canvas
canvas = ShapelyPolygon([(0, 0), (0, 10), (10, 10), (10, 0)])

# Place polygons on canvas without attempting to union
placed_polygons = []
offsets = [(5, 5)]  # starting point for the first polygon

for idx, polygon in enumerate(polygons):
    best_area = float('inf')
    best_position = None
    poly_shape = ShapelyPolygon(polygon + offsets[-1])
    
    # Grid search with extremely fine steps (0.01)
    for x in np.linspace(0, 10, 101):  # Now checks every 0.01 units
        for y in np.linspace(0, 10, 101):
            shifted_polygon = ShapelyPolygon(polygon + np.array([x, y]))

            # Ensuring that the polygons don't intersect with previously placed ones
            if all(not shifted_polygon.intersects(other) for other in placed_polygons):
                area = shifted_polygon.area
                if area < best_area:
                    best_area = area
                    best_position = (x, y)

    if best_position:  # Place the polygon only if a position is found
        placed_polygons.append(ShapelyPolygon(polygon + np.array(best_position)))
        offsets.append(best_position)

# Iterative refinement
NUM_ITERATIONS = 100000
best_polygons = list(placed_polygons)  # Make a copy
best_area = bounding_area(best_polygons)

for iteration in range(NUM_ITERATIONS):
    # Pick a random polygon
    idx = random.choice(range(len(best_polygons)))
    
    # Save the current position
    old_polygon = best_polygons[idx]
    
    # Try a random shift
    shifted_polygon = random_shift(old_polygon)
    
    # Replace the old polygon with the shifted one
    best_polygons[idx] = shifted_polygon
    
    # Check if the change is good
    new_area = bounding_area(best_polygons)
    if (new_area < best_area) and all(not shifted_polygon.intersects(other) for i, other in enumerate(best_polygons) if i != idx):
        # Accept the change
        best_area = new_area
    else:
        # Reject the change and revert
        best_polygons[idx] = old_polygon

# Visualization or further processing with best_polygons...
# Visualize the result
fig, ax = plt.subplots(figsize=(6, 6))
for polygon in placed_polygons:
    x, y = polygon.exterior.xy
    ax.fill(x, y, alpha=0.6)

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect('equal', 'box')
ax.axis('off')
plt.show()
#%%