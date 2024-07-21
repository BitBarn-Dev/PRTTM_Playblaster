# PRTTM Playblaster Tool

The PRTTM Playblaster Tool is a custom Maya utility designed to streamline the process of creating playblast sequences and uploading them to ShotGrid. It allows users to configure playblast settings, convert image sequences to MP4 using FFmpeg, and automate the upload of the resulting video to ShotGrid.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Environment Detection](#environment-detection)
- [Components](#components)
- [Extending the Tool](#extending-the-tool)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Custom Playblast Settings**: Configure camera, resolution, and other settings for playblasting.
- **FFmpeg Integration**: Convert image sequences to MP4 using FFmpeg.
- **ShotGrid Integration**: Automatically upload playblast videos to ShotGrid.
- **User Prompts**: Handles existing file checks with user prompts for overwriting.

## Installation
### Prerequisites
- Autodesk Maya
- FFmpeg
- ShotGrid account and API credentials

### Steps
1. **Download and Extract the Tool**:
    ```sh
    git clone https://github.com/your-repo/prttm_playblaster.git
    ```
2. **Install Dependencies**:
    Copy `shotgun_api3` into the same directory as your `prttm_playblaster.py`.

3. **Set Up Shelf Script**:
    Create a new shelf button in Maya and paste the following script:
    ```python
    import sys
    import os
    import maya.cmds as cmds

    # Corrected path to your script
    playblaster_path = r"C:\Users\srchr\Documents\PRTTM\Playblaster\src"
    if playblaster_path not in sys.path:
        sys.path.append(playblaster_path)

    # Debugging: Print sys.path to ensure the path is added
    print("sys.path:")
    for p in sys.path:
        print(p)

    # Import and execute the playblaster script
    try:
        import prttm_playblaster as playblaster
        if __name__ == "__main__":
            try:
                playblaster.playblast_ui.close()  # Close the window if it exists
                playblaster.playblast_ui.deleteLater()
            except:
                pass
            playblaster.playblast_ui = playblaster.PlayblastUI()
            playblaster.playblast_ui.show()
    except ImportError as e:
        cmds.error("Failed to import prttm_playblaster.py: {}".format(e))
        # Debugging: Print the ImportError details
        import traceback
        traceback.print_exc()
    ```

## Usage
1. **Launch the Tool**:
    Click on the shelf button in Maya to launch the Playblast Settings UI.

2. **Configure Playblast Settings**:
    Select the camera, resolution, and FFmpeg path. Disable film and resolution gates manually as prompted.

3. **Create and Upload Playblast**:
    Click the "Submit" button to create the playblast. If the MP4 file already exists, choose whether to overwrite it. The tool will convert the image sequence to MP4 and upload it to ShotGrid.

## File Structure
```
prttm_playblaster/
├── src/
│   ├── prttm_playblaster.py
│   ├── shotgrid_utils.py
│   ├── shotgun_api3/
│   │   └── ...
├── README.md
```

## Environment Detection
The tool adapts to the Maya environment by dynamically adjusting paths and settings based on user input. It checks for the presence of FFmpeg and ShotGrid credentials.

## Components
- **prttm_playblaster.py**: Main UI and functionality for creating playblasts and converting them to MP4.
- **shotgrid_utils.py**: Helper functions for interacting with ShotGrid, including parsing filenames, creating entities, and uploading files.

## Extending the Tool
To add new features or modify existing ones, follow these guidelines:
1. **Clone the Repository**:
    ```sh
    git clone https://github.com/your-repo/prttm_playblaster.git
    ```
2. **Make Your Changes**:
    Edit the relevant files in the `src` directory.
3. **Test Your Changes**:
    Ensure your changes work correctly by running the tool in Maya.
4. **Submit a Pull Request**:
    Submit your changes for review and inclusion in the main project.

## Contributing
We welcome contributions! Please fork the repository and submit pull requests with your improvements. Make sure to follow the existing code style and include comments for clarity.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

By following this README, you should be able to install, configure, and use the PRTTM Playblaster Tool effectively. Happy playblasting!