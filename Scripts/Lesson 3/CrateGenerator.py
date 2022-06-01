# Author - Sindre E. Hinderaker
# Description - Generates a cubed crate based on user-input.

from email.policy import default
from logging import root
import adsk.core, adsk.fusion, adsk.cam, traceback

cubeSize = None

def run(context):
    ui = None
    try:
        # Get Fusino 360 application, user interface, and active design-document
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        (returnValue, cancelled) = ui.inputBox('Specify crate size', 'Crate Generator', '10')

        if not cancelled:
                # Get specified value from user input
                cubeSize = adsk.core.ValueInput.createByString(f'{returnValue} cm')
                
                # Get root component of the design
                root_comp = design.rootComponent

                # Create sketch
                sketches = root_comp.sketches
                crate_sketch = sketches.add(root_comp.xZConstructionPlane)

                # Add main/centre rectangle lines
                origin = adsk.core.Point3D.create(0, 0, 0)
                crate_corner = adsk.core.Point3D.create(float(returnValue)/2, float(returnValue)/2, 0)
                crate_lines = crate_sketch.sketchCurves.sketchLines.addCenterPointRectangle(origin, crate_corner)

                # Get the crate profile and create extrude feature
                crate_profile = crate_sketch.profiles.item(0)
                extrudecrate = root_comp.features.extrudeFeatures.addSimple(crate_profile, cubeSize, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                # extInput = root_comp.features.extrudeFeatures.createInput(crate_profile,  adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                # extInput.setDistanceExtent(False, cubeSize)
                # root_comp.features.extrudeFeatures.add(extInput)

                # Create object collection with the desired face entity
                crate_face_entity = adsk.core.ObjectCollection.create()
                crate_face_entity.add(extrudecrate.endFaces.item(0)) # end face of the extruded body/crate

                # Shell body in the object collection
                shellFeats = root_comp.features.shellFeatures
                shellFeatureInput = shellFeats.createInput(crate_face_entity)
                shellFeatureInput.insideThickness = adsk.core.ValueInput.createByReal(float(returnValue)/10)
                shellFeats.add(shellFeatureInput)

        if cancelled:
            ui.messagecrate('crate generation was canceled')

    except:
        if ui:
            ui.messagecrate('Failed:\n{}'.format(traceback.format_exc()))
