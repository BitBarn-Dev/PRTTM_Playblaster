import os
import re
import shotgun_api3
from shotgun_api3 import Shotgun

# Placeholder for your API keys
SHOTGRID_URL = 'https://prttm.shotgrid.autodesk.com'
SCRIPT_NAME = 'animation_publisher'
SCRIPT_KEY = 'wyd7zivGjdqptsbwq?qphmqqk'

# Connect to ShotGrid
sg = Shotgun(SHOTGRID_URL, SCRIPT_NAME, SCRIPT_KEY)

PROJECT_ID = 222  # Hardcoded project ID

def parse_filename(filename):
    """Parse the Maya file short name to extract project details."""
    pattern = r'(?P<project>.+?)_(?P<episode>.+?)_(?P<sequence>.+?)_(?P<shot>.+?)_(?P<task>.+?)_v(?P<version>\d+)\.(ma|mb)'
    match = re.match(pattern, filename)
    if not match:
        raise ValueError(f"Filename '{filename}' does not match the expected pattern.")
    return match.groupdict()

def get_entity(entity_type, filters, fields=None):
    """Retrieve an entity from ShotGrid."""
    return sg.find_one(entity_type, filters, fields)

def create_entity(entity_type, data):
    """Create a new entity in ShotGrid."""
    return sg.create(entity_type, data)

def update_version(short_name, proxy=None):
    """Update or create a version in ShotGrid based on the parsed filename."""
    try:
        print(f'parsing filename: {short_name}')
        data = parse_filename(short_name)
    except ValueError as e:
        print(f"Error parsing filename: {e}")
        return

    sequence = data['sequence']
    shot = data['shot']
    task_name = data['task']
    version_number = int(data['version'])

    # Check if the shot exists
    shot_code = f"{sequence}_{shot}"
    shot_entity = get_entity('Shot', [['code', 'is', shot_code]])
    if not shot_entity:
        print(f"Shot '{shot_code}' not found. Creating new shot.")
        shot_entity = create_entity('Shot', {'code': shot_code, 'project': {'type': 'Project', 'id': PROJECT_ID}})

    # Check if the task exists
    task_entity = get_entity('Task', [['entity', 'is', shot_entity], ['content', 'is', task_name]])
    if not task_entity:
        print(f"Task '{task_name}' not found. Creating new task.")
        task_entity = create_entity('Task', {'entity': shot_entity, 'content': task_name, 'project': {'type': 'Project', 'id': PROJECT_ID}})

    # Check if the version exists
    version_code = f"{short_name.split('.')[0]}"
    version_entity = get_entity('Version', [['code', 'is', version_code]])
    if version_entity:
        print(f"Version '{version_code}' found. Updating version.")
        if proxy:
            sg.upload("Version", version_entity['id'], proxy, field_name="sg_uploaded_movie")
    else:
        print(f"Version '{version_code}' not found. Creating new version.")
        version_data = {
            'code': version_code,
            'entity': shot_entity,
            'sg_task': task_entity,
            'project': {'type': 'Project', 'id': PROJECT_ID}
        }
        version_entity = sg.create('Version', version_data)
        if proxy:
            sg.upload("Version", version_entity['id'], proxy, field_name="sg_uploaded_movie")

    # Print the link to the new version in ShotGrid
    version_url = f"{SHOTGRID_URL}/detail/Version/{version_entity['id']}"
    print(f"Upload complete. Version URL: {version_url}")

################################################################################
# Unit Testing
################################################################################
def test_update_version():
    # Test data
    short_name = "SOUL_1001_JUL_005_anim_v004.ma"
    proxy_path = r"G:\Shared drives\dh_projects\prttm\SOUL\Episodes\1001\shots\JUL_005\outputs\anim\SOUL_1001_JUL_005_anim_v004\playblast\SOUL_1001_JUL_005_anim_v004.mp4"

    # Call the function with the test data
    update_version(short_name, proxy=proxy_path)

if __name__ == "__main__":
    test_update_version()
