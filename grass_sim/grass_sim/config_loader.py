import yaml
from pathlib import Path
from PIL import Image
from ament_index_python.packages import get_package_share_directory

# Stores config values in config variable
def load_config():
    config_path = Path(get_package_share_directory('grass_sim')) / 'config' / 'grass_config.yaml'
    with open(config_path, 'r') as config:
        return yaml.safe_load(config)

# Loads the heightmap using the path in the config.yaml, converts it to greyscale
def load_heightmap(config):
    heightmap_path = Path(config['terrain']['heightmap'])
    heightmap_path = Path(get_package_share_directory('grass_sim')) / heightmap_path
    image = Image.open(heightmap_path).convert('L')
    return image

def get_height(X_w,Y_w, config, heightmap):
    # Terrain characteristics:
    width_w = config['terrain']['size']['x'] # Total width of world array in meters
    height_w = config['terrain']['size']['y'] # Total height of world array in meters
    z_h = config['terrain']['size']['z'] # Configured maximum z-axis height of heightmap in Gazebo
    width_h , height_h = heightmap.size # Total width and height of heightmap.png file in pixels
    N = width_h

    # Main logic
    X_h = ((N-1)/2)+X_w*((N-1)/width_w) # Converts world x coordinate to heightmap x coordinate
    X_h = round(X_h)
    Y_h = ((N-1)/2)-Y_w*((N-1)/height_w) # Converts world y coordinate to heightmap y coordinate
    Y_h = round(Y_h)

    intensity = heightmap.getpixel((X_h, Y_h))
    elevation = (intensity / 255.0) * z_h # converts pixel intensity and calculates elevation
    return elevation



