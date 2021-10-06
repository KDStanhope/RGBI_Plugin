from imageMerge import RGBI_model
import Metashape
import os, sys


def combine_and_export_rgbi():
    path = Metashape.app.getExistingDirectory("Select a working directory...")
    doc = Metashape.app.document
    if not len(doc.chunks):
        raise Exception("No chunks!")

    print("Script started...")
    chunk = doc.chunk
    chunk.exportOrthophotos(path+"\{filename}.tif" ,save_world=True,save_alpha=False)

    matching_images = []
    all_images = []
    for filename in os.listdir(path):
        all_images.append(filename)
    for item in all_images:
        if "RGB_" in item:
            frame_number = item.replace('RGB_','')
            frame_number = frame_number.replace('.tif','')
            for match in all_images:
                if "IR_" and frame_number in match:
                    matching_images.append((item,match))
    
    RGBI_model(matching_images[5])


def orthorectify():
    doc = Metashape.app.document
    if not len(doc.chunks):
        raise Exception("No chunks!")

    print("process started...")
    chunk = doc.chunk
    gsd = Metashape.app.getFloat(label='What pixel size to use?')
    bbox = Metashape.BBox()
    bbox.min = (Metashape.Vector((chunk.elevation.left,chunk.elevation.top)))
    bbox.max = (Metashape.Vector((chunk.elevation.right,chunk.elevation.bottom)))
    chunk.buildOrthomosaic(
        surface_data=Metashape.DataSource(4),
        blending_mode=Metashape.BlendingMode(4),
        region=bbox,
        resolution=gsd,
        )
    item2 = "RGBI Tools/Orthorectify all frames"
    Metashape.app.removeMenuItem(item2)


def checklist():
    camera_status = "camera_status: FAILED"
    elevations_status = "elevations_status: FAILED"
    orthomosaics_status = "orthomosaics_status: FAILED"

    doc = Metashape.app.document
    chunk = doc.chunk

    if not len(doc.chunk.cameras):
        camera_status = "FAIL: There are no images present. You need to align a set of 24bit RGB images along with 24bit IR images"
    else:
        camera_status="PASS: Imagery present"

    if not len(chunk.elevations):
        elevations_status="FAIL: You need a DEM so you can orthorectify the frames"
        Metashape.app.messageBox(camera_status+"\n"+elevations_status+"\n"+orthomosaics_status)
        raise Exception("Cannot Continue")
    else:
        elevations_status="PASS: DEM Present"

    if not len(chunk.orthomosaics):
        orthomosaics_status="FAIL: Please run RGBI Tools/Orthorectify all frames; orthorectification is required"
        item2 = "RGBI Tools/Orthorectify all frames"
        Metashape.app.removeMenuItem(item2)
        Metashape.app.addMenuItem(item2, orthorectify)
    elif len(chunk.orthomosaics) > 1:
        item2 = "RGBI Tools/Orthorectify all frames"
        Metashape.app.removeMenuItem(item2)
        Metashape.app.addMenuItem(item2, orthorectify)
        orthomosaics_status = "FAIL! \n You have 2 orthomosaics present already. It is a good idea to let RGBI Tools do this step. A menu item has been added."
    else:
        orthomosaics_status = "PASS: Orthomosaic Present"
        item1 = "RGBI Tools/Generate RGBI models for OrthoVista"
        Metashape.app.addMenuItem(item1, combine_and_export_rgbi)

    item1 = "RGBI Tools/OVERRIDE Generate RGBI models for OrthoVista"
    Metashape.app.addMenuItem(item1, combine_and_export_rgbi)
    Metashape.app.messageBox(camera_status+"\n"+elevations_status+"\n"+orthomosaics_status)

    



label = "RGBI Tools/Checklist"
Metashape.app.addMenuItem(label, checklist)


