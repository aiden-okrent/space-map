# config.py
from pathlib import Path

# Get the directory of the current script
script_dir = Path(__file__).resolve().parent

# construct full paths to all directories
CORE_DIR = script_dir / "core"
GUI_DIR = script_dir / "gui"
UTILS_DIR = script_dir / "utils"
ASSETS_DIR = script_dir / "assets"
CONFIG_DIR = ASSETS_DIR / "config"
stylesheet_path = CONFIG_DIR / "stylesheet.json"
satellite_list_items_path = CONFIG_DIR / "satellite_query_category_types.json"
map_textures = Path(__file__).resolve().parent / "assets" / "textures"