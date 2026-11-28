from grass_sim.config_loader import load_config, load_heightmap, get_height

#First test of load_config() function
config = load_config()

print("\n--- CONFIGURATION TEST ---")
print(config)

print("\nTerrain dimensions:")
print("Width:", config['terrain']['size']['x'])
print("Height:", config['terrain']['size']['y'])
print("Maximum elevation:", config['terrain']['size']['z'])

print("\nGrass configuration:")
print("Cell size:", config['grass']['cell_size'])
print("Chunk dimensions:", config['grass']['chunk_cells'])

#Second test of load_heightmap() function
heightmap = load_heightmap(config)

print("\n--- HEIGHTMAP TEST ---")
print("Heightmap loaded successfully!")
print("Dimensions:", heightmap.size)
print("Image mode:", heightmap.mode)
heightmap.show()

#Third test of get_height() function
print("\n--- HEIGHT TEST ---")

test_points = [
    (0.0, 0.0),
    (5.0, 0.0),
    (-5.0, 0.0),
    (0.0, 5.0),
    (0.0, -4.0),
    (10.0, 9.0),
    (-8.0, -10.0)
]

for x, y in test_points:
    elevation = get_height(x, y, config, heightmap)

    print(
        f"World ({x:6.2f}, {y:6.2f}) "
        f"-> Elevation: {elevation:.4f} m"
    )
