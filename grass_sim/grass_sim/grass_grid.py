from grass_sim.config_loader import get_height

# Generating cells!!!
def generate_cell_grid (config, heightmap):

    # Terrain characteristics:
    width_w = config['terrain']['size']['x'] # Total width of world array in meters
    height_w = config['terrain']['size']['y'] # Total height of world array in meters
    cell_size = config['grass']['cell_size'] # Size of each side of a cell
    num_x_cells = round(width_w / cell_size) # Total number of cells in x direction
    num_y_cells = round(height_w / cell_size) # Total number of cells in y direction

    cell_grid = [] # Array storing calculated cell information for whole grid
    for v in range(num_y_cells): # Loops through rows
        grid_u = []
        for u in range(num_x_cells): # Loops through columns
            X_c = -(width_w/2)+(0.5+u)*cell_size # Calculates cell x coordinate
            Y_c = (height_w/2)-(0.5+v)*cell_size # Calculates cell y coordinate
            elevation = get_height(X_c, Y_c, config, heightmap) # Retreives cell elevation from heightmap

            # Dictionary for each cell
            cell = {
                "row": v,
                "column": u,
                "x": X_c,
                "y": Y_c,
                "z": elevation,
                "size": cell_size,
            }
            grid_u.append(cell)
        cell_grid.append(grid_u)
    return cell_grid

# Generating Chunks!!!
def generate_chunks(cell_grid,config):

    # Chunk Characteristics:
    chunk_width = config['grass']['chunk_cells']['x']
    chunk_height = config['grass']['chunk_cells']['y']
    num_y_cells = len(cell_grid) # Measures number of rows in  cell grid
    num_x_cells = len(cell_grid[0]) # Measures number of columns in cell grid

    chunk_grid = [] # Array storing all chunks

    # loops through chunks
    for chunk_v in range(0, num_y_cells, chunk_height): # Loops through all cell rows while incrementing by chunk height
        for chunk_u in range(0, num_x_cells, chunk_width): # Loops through all cell columns while incrementing by chunk width

            chunk_cells = [] # Array storing all cells in given chunk

            for v in range(chunk_v, min(chunk_v+chunk_height, num_y_cells)): # Loops through all cell rows in chunk up to chunk height
                for u in range(chunk_u, min(chunk_u+chunk_width, num_x_cells)): # Loops through all cell columns in chunk up to chunk width
                    chunk_cells.append(cell_grid[v][u])

            # Dictionary for each chunk
            chunk = {
               "row": chunk_v // chunk_height,
               "column": chunk_u // chunk_width,
               "cells": chunk_cells,
            }
            chunk_grid.append(chunk)
    return chunk_grid