# Extension ideas

## Lesson 1

- Extend to be able to export from Project level.

```python
processFolder(data.activeProject)
```

- Extend to export design documents in sub-folders and create them in file system. Hint: Recursion.

```python
for subFolder in folder.dataFolders:
    processFolder(subFolder)
```

- Let user decide folder for exportation by file-explorer. Hint: folder-dialogue.

```python
folderDlg = ui.createFolderDialog()
folderDlg.title = 'Select folder for exportation' 

# Show folder dialog
dlgResult = folderDlg.showDialog()
if dlgResult == adsk.core.DialogResults.DialogOK:
    selFolder = folderDlg.folder
    ui.messageBox(selFolder)
else:
    ui.messageBox('Export cancelled')
    return
```

- Let user decide exportation format. Hint: input-box, command-dialogue, etc.

```python
# File-type specification
fileType = '.step'
(returnValue, cancelled) = ui.inputBox('Specify export file-format', 'Export file-format', 'step')

if not cancelled:
    fileType = returnValue.replace('.','').strip().lower() # string cleanup
    fileType = f'.{fileType}' # add . to filetype

# Get root component of the opened file (needed for stl-export)
root_comp = adsk.fusion.Design.cast(app.activeProduct).rootComponent
exportMgr = des.exportManager
        if fileType == '.step':
            fusionArchiveOptions = exportMgr.createSTEPExportOptions(filePath + doc.name + fileType)
        elif fileType == '.stl':
            fusionArchiveOptions = exportMgr.createSTLExportOptions(filePath + doc.name + fileType)       
        elif fileType == '.iges':
            fusionArchiveOptions = exportMgr.createSTEPExportOptions(filePath + doc.name + fileType)
        else:
            ui.messageBox(f'Unsupported file-type: "{fileType}"')
            return
        res = exportMgr.execute(fusionArchiveOptions)
```

## Lesson 2

- Extend to function with curved faces (cylinders, etc.).

```python
# Create tangent plane
const_plane_input.setByTangent(tangentFace, angle, planarEntity)
# Create a to-entity extent definition with offset
extent_to_face = adsk.fusion.ToEntityExtentDefinition.create(selected_face.body, True, adsk.core.ValueInput.createByReal(-0.02))
# Set the one side extent with the to-entity-extent-definition
extInput.setOneSideExtent(extent_to_face, adsk.fusion.ExtentDirections.PositiveExtentDirection)
```

- Change text-font through UI. Hint: input-box, command-dialogue, etc.
- Change text-style through UI (bold, italic, underline). Hint: input-box, command-dialogue, etc.
- Change text-angle through UI. Hint: input-box, command-dialogue, etc.

```python
# Text customization
from math import radians

(returnValue, cancelled) = ui.inputBox('Specify text rotation', 'Text rotation', '180')

engrave_input.fontName = 'Harlow Solid Italic'
engrave_input.fontName = 'Times New Roman'
engrave_input.textStyle = adsk.fusion.TextStyles.TextStyleBold
engrave_input.textStyle = adsk.fusion.TextStyles.TextStyleUnderline
engrave_input.angle = radians(float(returnValue))/2
```

## Lesson 3

- Make flanges on the ends of both pipes / pipe (with holes for bolts)
 - Useful objects: [MirrorFeatures](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-GUID-e2fa227a-3c3c-4375-aeac-8557d4013178), [HoleFeature](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-GUID-3315b7ea-f85d-417c-ad31-2d328b72f6a5) 
 - Useful operations: [FeatureOperations](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-GUID-GUID-d7074f3d-95d5-408b-904f-91eb8cddc095)
