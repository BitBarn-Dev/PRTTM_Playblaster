import maya.cmds as cmds
import os

def export_image_sequence():
    # Get the current scene file path
    file_path = cmds.file(query=True, sceneName=True)
    
    if not file_path:
        cmds.error("Please save your scene before running the script.")
        return

    # Parse the file path to determine the output directory and base filename
    file_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)

    # Replace "tasks" with "outputs"
    output_dir = file_dir.replace('/tasks/', '/outputs/')
    output_dir = os.path.join(output_dir, name, 'playblast')
    output_dir = os.path.normpath(output_dir)  # Normalize path separators
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Determine the output file pattern
    output_pattern = os.path.join(output_dir, name)
    output_pattern = os.path.normpath(output_pattern)  # Normalize path separators

    # Debugging: Print output directory and file pattern
    print("Output Directory: {}".format(output_dir))
    print("Output File Pattern: {}".format(output_pattern))

    # Get the currently active panel
    current_panel = cmds.getPanel(withFocus=True)

    # Check if the current panel is a model panel and not one of the default views
    invalid_cameras = ['top', 'front', 'side', 'persp']
    if not current_panel or cmds.getPanel(typeOf=current_panel) != "modelPanel" or cmds.modelPanel(current_panel, query=True, camera=True) in invalid_cameras:
        # If not, get the first available model panel that is not a default view
        model_panels = cmds.getPanel(type="modelPanel")
        if not model_panels:
            cmds.error("No model panels available.")
            return
        for panel in model_panels:
            camera = cmds.modelPanel(panel, query=True, camera=True)
            if camera not in invalid_cameras:
                current_panel = panel
                break
        else:
            # If no suitable panel is found, fall back to the first available model panel
            current_panel = model_panels[0]

    current_camera = cmds.modelPanel(current_panel, query=True, camera=True)

    # Debugging: Print the current panel and camera
    print("Using Panel: {}, Camera: {}".format(current_panel, current_camera))

    # Get the camera shape node
    camera_shape = cmds.listRelatives(current_camera, shapes=True)[0]

    # Get the current frame range
    start_frame = cmds.playbackOptions(query=True, minTime=True)
    end_frame = cmds.playbackOptions(query=True, maxTime=True)

    # Get render resolution
    render_width = cmds.getAttr("defaultResolution.width")
    render_height = cmds.getAttr("defaultResolution.height")
    render_aspect = cmds.getAttr("defaultResolution.deviceAspectRatio")

    # Create an off-screen model panel
    offscreen_panel = cmds.modelPanel()
    offscreen_editor = cmds.modelPanel(offscreen_panel, query=True, modelEditor=True)

    # Set the camera in the off-screen panel
    cmds.modelPanel(offscreen_panel, edit=True, camera=current_camera)
    
    # Ensure the panel is offscreen
    cmds.modelEditor(offscreen_editor, edit=True, displayLights='default')
    cmds.modelEditor(offscreen_editor, edit=True, displayTextures=True)
    cmds.modelEditor(offscreen_editor, edit=True, displayAppearance='smoothShaded')

    # Perform the playblast
    cmds.playblast(
        filename=output_pattern,
        format='image',
        startTime=start_frame,
        endTime=end_frame,
        sequenceTime=0,
        clearCache=1,
        viewer=0,
        showOrnaments=0,
        fp=4,  # force a particular format (jpg)
        percent=100,
        compression='jpg',
        quality=100,
        widthHeight=[render_width, render_height],
        offScreen=True,
        framePadding=4
    )

    # Delete the off-screen panel
    cmds.deleteUI(offscreen_panel, panel=True)

# Example usage
export_image_sequence()
