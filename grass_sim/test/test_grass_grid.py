from grass_sim.config_loader import load_config, load_heightmap
from grass_sim.grass_grid import generate_cell_grid, generate_chunks
import math

#Config and heightmap tests:
config = load_config()
heightmap = load_heightmap(config)

# Importing all config information:
width_w = config['terrain']['size']['x']
height_w = config['terrain']['size']['y']
max_elevation = config['terrain']['size']['z']

cell_size = config['grass']['cell_size']
chunk_width = config['grass']['chunk_cells']['x']
chunk_height = config['grass']['chunk_cells']['y']

expected_cols = round(width_w / cell_size)
expected_rows = round(height_w / cell_size)
expected_total_cells = expected_cols * expected_rows

expected_chunk_cols = math.ceil(expected_cols / chunk_width)
expected_chunk_rows = math.ceil(expected_rows / chunk_height)
expected_total_chunks = expected_chunk_rows * expected_chunk_cols

print("\n========== INPUT TEST ==========")
print("Configuration loaded successfully!")
print("Heightmap dimensions:", heightmap.size)

#Test of cell generation:
cell_grid = generate_cell_grid(config, heightmap)

num_y_cells = len(cell_grid)
num_x_cells = len(cell_grid[0])
total_cells = num_x_cells * num_y_cells

print("\n========== CELL GRID TEST ==========")
print(f"Rows: expected={expected_rows}, actual={num_y_cells}")
print(f"Columns: expected={expected_cols}, actual={num_x_cells}")
print(f"Total cells: expected={expected_total_cells}, actual={total_cells}")

assert num_y_cells == expected_rows
assert num_x_cells == expected_cols
assert total_cells == expected_total_cells

#Test of cell positions:
print("\n========== CELL POSITION TEST ==========")

first_exp_x = -(width_w / 2) + (0.5 + 0) * cell_size
first_exp_y = (height_w / 2) - (0.5 + 0) * cell_size
first_cell = cell_grid[0][0]
last_cell = cell_grid[-1][-1]

last_row = num_y_cells - 1
last_col = num_x_cells - 1
last_exp_x = -(width_w / 2) + (0.5 + last_col) * cell_size
last_exp_y = (height_w / 2) - (0.5 + last_row) * cell_size

print(f"First cell expected: ({first_exp_x}, {first_exp_y}) | actual: ({first_cell['x']}, {first_cell['y']})")
print(f"Last cell expected:  ({last_exp_x}, {last_exp_y}) | actual: ({last_cell['x']}, {last_cell['y']})")

assert abs(first_cell['x'] - first_exp_x) < 1e-9
assert abs(first_cell['y'] - first_exp_y) < 1e-9

assert abs(last_cell['x'] - last_exp_x) < 1e-9
assert abs(last_cell['y'] - last_exp_y) < 1e-9

#Test cell elevations:
print("\n========== ELEVATION TEST ==========")

max_elevation = config['terrain']['size']['z']
print(f"Expected elevation range: [0.0, {max_elevation}] m")

for row in cell_grid:
    for cell in row:
        assert 0.0 <= cell['z'] <= max_elevation

print("All cell elevations are within valid limits!")

print("Sample elevations:")

for cell in [
    cell_grid[0][0],
    cell_grid[50][50],
    cell_grid[100][100],
    cell_grid[-1][-1]
]:
    print(
        f"Cell ({cell['row']}, {cell['column']}) "
        f"Elevation: {cell['z']:.4f} m"
    )

#Test chunk generation:
chunk_grid = generate_chunks(cell_grid, config)

print("\n========== CHUNK TEST ==========")
print(f"Total chunks: expected={expected_total_chunks}, actual={len(chunk_grid)}")
assert len(chunk_grid) == expected_total_chunks

for chunk in chunk_grid:
    start_row = chunk['row'] * chunk_height
    end_row = min(start_row + chunk_height, expected_rows)
    start_col = chunk['column'] * chunk_width
    end_col = min(start_col + chunk_width, expected_cols)
    expected_in_chunk = (end_row - start_row) * (end_col - start_col)

    print(
        f"Chunk ({chunk['row']}, {chunk['column']}) "
        f"Cells: expected={expected_in_chunk}, actual={len(chunk['cells'])}"
    )
    assert len(chunk['cells']) == expected_in_chunk

#Test chunks against cells:
print("\n========== CHUNK VERIFICATION ==========")

total_chunk_cells = sum(
    len(chunk['cells']) for chunk in chunk_grid
)

print("Cells in grid:", total_cells)
print("Cells in chunks:", total_chunk_cells)

assert total_chunk_cells == total_cells

# Verify every cell is included exactly once
grid_cell_ids = {
    id(cell)
    for row in cell_grid
    for cell in row
}

chunk_cell_ids = [
    id(cell)
    for chunk in chunk_grid
    for cell in chunk['cells']
]

assert len(chunk_cell_ids) == total_cells
assert len(set(chunk_cell_ids)) == total_cells
assert set(chunk_cell_ids) == grid_cell_ids

print("Every cell belongs to exactly one chunk!")

print("\n========== ALL TESTS PASSED ==========")
