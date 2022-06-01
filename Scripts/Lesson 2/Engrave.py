# Author - Sindre E. Hinderaker
# Description - Script that engraves a predetermined text at the senter og a user-selected face.

import adsk.core, adsk.fusion, adsk.cam, traceback

# Global default engraving parameters
engravedText = "TIN200"
textHeight = 1
engraveDepth = 0.1

def run(context):
    ui = None
    try:
        # Get Fusino 360 application, user interface, and active design-document
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        # Verify correct workspace
        if not design:
            ui.messageBox('Current workspace is not supported, please change to "Design" workspace and try again.')
            return
        
        # Get root component
        root_comp = design.rootComponent

        # Prompt user to select a face and store in variable
        selected_face = ui.selectEntity('Select a surface for engraving: ', 'Faces').entity
        #ui.messageBox(f'Selected face centroid: {selected_face.centroid.asArray()}')
        
        # Find shortest edge of face
        shortest_edge = min([edge.length for edge in selected_face.edges])

        # Update text height parameter
        textHeight = shortest_edge/10

        # Create construction plane on selected face 
        # This will ensure that origo for this sketch is at the center of the face (not relative to the root component)
        const_plane_input = root_comp.constructionPlanes.createInput()
        const_plane_input.setByOffset(selected_face, adsk.core.ValueInput.createByReal(0))
        const_plane = root_comp.constructionPlanes.add(const_plane_input)

        # Create sketch on selected face
        sketch = root_comp.sketches.add(const_plane)

        # Draw text on sketch
        texts = sketch.sketchTexts
        engrave_input = texts.createInput2(formattedText=engravedText, height=textHeight)

        cornerPointText = adsk.core.Point3D.create(1, 1, 0)
        diagonalPointText = adsk.core.Point3D.create(-1, -1, 0)
        horizontalAlignmentText = adsk.core.HorizontalAlignments.CenterHorizontalAlignment
        verticalAlignmentText = adsk.core.VerticalAlignments.MiddleVerticalAlignment
        characterSpacing = 0
        
        engrave_input.setAsMultiLine(cornerPointText,
                                     diagonalPointText,
                                     horizontalAlignmentText,
                                     verticalAlignmentText,
                                     characterSpacing)
        texts.add(engrave_input)

        # Extrude cut (engrave) text into body
        text_profile = texts.item(0)  # get text-sketch
        extInput = root_comp.features.extrudeFeatures.createInput(profile=text_profile, 
                                                                  operation=adsk.fusion.FeatureOperations.CutFeatureOperation)
        # Create a to-entity extent definition with offset
        extent_to_face = adsk.fusion.ToEntityExtentDefinition.create(selected_face.body, 
                                                                     True,
                                                                     adsk.core.ValueInput.createByReal(-0.02))
        # Set the one side extent with the to-entity-extent-definition
        extInput.setOneSideExtent(extent_to_face, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        root_comp.features.extrudeFeatures.add(extInput)


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
