import os

# Get absolute path of the asset
asset_path = os.path.abspath("assets/kenney-voxel-items-png/sword_silver.png")
print("Absolute path:", asset_path)

# Check if the file exists
if os.path.exists(asset_path):
    print("File found!")
else:
    print("File not found!")