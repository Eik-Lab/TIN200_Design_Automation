# Author - Sindre E. Hinderaker
# Description - Script that exports every document in the current folder to an STEP-format, at a desired file-location.


import os, adsk.core, adsk.fusion, traceback

# Folder path can be modified to alter location of saved
folder_path = 'C:/Users/HP/Desktop/'

# To change file type the associated export manager must also be used
file_type = '.step'

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        data = app.data
        #data.activeProject
        #data.activeFolder

        export_folder(data.activeFolder)
            
        ui.messageBox(f'Finished exporting folder to "{folder_path}"')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Recursive function to process the contents of the folder.
def export_folder(folder: adsk.core.DataFolder):
    ui = None
    try:        
        app = adsk.core.Application.get()
        documents = app.documents
        ui  = app.userInterface

        # ui.messageBox('Processing folder: ' + folder.name)

        # Create directory/folder with folder name from Fusion 360
        file_path = os.path.join(folder_path, folder.name + '/')
        os.mkdir(file_path)

        # Create progress bar
        export_progress = ui.createProgressDialog()
        export_progress.show(title=f'Exporting: {folder.name}', 
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
            export_progress.progressValue = i + 1

            # Try opening the document but gracefully fail and 
            # assume the document isn't a Fusion document.            
            try:
                document = documents.open(file, True)
            except:
                document = None

            if document:            
                # Find the Design product in the document.
                for prod in document.products:
                    if prod.objectType == adsk.fusion.Design.classType():
                        des = prod
                        break
                    
                if des:
                    # Get the ExportManager from the active design.
                    exp_manager = des.exportManager

                    # Create a export options object and specify file type
                    exp_options = exp_manager.createSTEPexp_options(file_path + document.name + file_type)

                    # Execute export
                    res = exp_manager.execute(exp_options)
                                
                    document.close(False)
                    
        for subFolder in folder.dataFolders:
            export_folder(subFolder)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

