# Author - Sindre E. Hinderaker
# Description - Script that exports every design-document in the current active folder to an STEP-format, at a desired file-location.


import os, adsk.core, adsk.fusion, traceback

# Folder path can be modified to alter location of saved
folderPath = 'C:/Users/HP/Downloads/'

# To change file type the associated export manager must also be used
fileType = '.step'

def run(context):
    ui = None
    try:
        # Get the fusion 360 application
        app = adsk.core.Application.get()
        # Get user interface
        ui  = app.userInterface
        
        # Get application data
        data = app.data
        
        # Pass the active folder to the function for processing and exportion
        processFolder(data.activeFolder)
            
        ui.messageBox(f'Finished exporting folder to "{folderPath}"')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# (Recursive) function to process the design-documents of the folder.
def processFolder(folder):
    ui = None
    try:
        # Get the Fusion 360 application, documents and user interface
        app = adsk.core.Application.get()
        docs = app.documents
        ui  = app.userInterface
        
        # ui.messageBox('Processing folder: ' + folder.name)

        # Create directory/folder (on computer) with current-folder name from Fusion 360
        filePath = os.path.join(folderPath, folder.name + '/')
        os.mkdir(filePath)

        # Create progress bar
        exportProgress = ui.createProgressDialog()
        exportProgress.show(title=f'Exporting: {folder.name}', 
                            message='Processing file %v of %m (%p %)',
                            minimumValue=0, 
                            maximumValue=folder.dataFiles.count, 
                            delay=0)
        # %p - percentage completed
        # %v - current value
        # %m - total steps

        # Loop over files in folder
        for i, file in enumerate(folder.dataFiles):
            # ui.messageBox('Processing: ' + file.name)

            # Increment progress bar value
            exportProgress.progressValue = i + 1

            # Try opening the document but gracefully fail and 
            # assume the document isn't a Fusion document.            
            try:
                doc = docs.open(file, True)
            except:
                doc = None

            if doc:            
                # Find the Design product in the document.
                for prod in doc.products:
                    if prod.objectType == adsk.fusion.Design.classType():
                        des = prod
                        break
                    
                if des:
                    # Get the ExportManager from the active design.
                    exportMgr = des.exportManager
        
                    # Create a FusionArchiveExportOptions object and do the export.
                    fusionArchiveOptions = exportMgr.createSTEPExportOptions(filePath + doc.name + fileType)
                    res = exportMgr.execute(fusionArchiveOptions)
                                
                    doc.close(False)
        
        # Recurtion, pass subfolders to the same function
        # for subFolder in folder.dataFolders:
        #     processFolder(subFolder)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

