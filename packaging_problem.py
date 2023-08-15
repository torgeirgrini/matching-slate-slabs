#%%
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon, Polygon as ShapelyPolygon

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