# Author - Sindre E. Hinderaker
# Description - Generator for creating customized flow-valves

import adsk.core, adsk.fusion, adsk.cam, traceback
from math import radians, pi, cos, degrees

# Global design parameters
defaultTheta = radians(75) # [deg] angle between sensor-pipe and main-pipe
defaultD = 40              # [cm] pipe/valve diameter

# Global set of event _handlers to keep them referenced for the duration of the command
_handlers = []

app = adsk.core.Application.get()
if app:
    ui = app.userInterface

new_comp = None

def createNewComponent():
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    root_comp = design.rootComponent
    all_occs = root_comp.occurrences
    new_occ = all_occs.addNewComponent(adsk.core.Matrix3D.create())
    return new_occ.component


class FlowValveCommandExecuteHandler(adsk.core.CommandEventHandler):
    """Event handler that reacts to any changes the user makes to any of the command inputs."""
    def __init__(self):
        super().__init__()
    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command: adsk.core.Command = args.firingEvent.sender
            inputs = command.commandInputs

            flow_valve = FlowValve()
            for input in inputs:
                if input.id == 'theta':
                    flow_valve.theta = unitsMgr.evaluateExpression(input.expression, "deg")
                elif input.id == 'D':
                    flow_valve.D = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'P':
                    input.formattedText = f'~ {round(flow_valve.P, 2)} cm'
            flow_valve.create_flow_valve()
            args.isValidResult = True

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class FlowValveCommandDestroyHandler(adsk.core.CommandEventHandler):
    """Event handler that reacts to when the command is destroyed. This terminates the script."""
    def __init__(self):
        super().__init__()
    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event _handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class FlowValveCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """
    Event handler that reacts when the command definition is executed which
    results in the command being created and this event being fired.
    """   
    def __init__(self):
        super().__init__()        
    def notify(self, args: adsk.core.CommandEventArgs):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command event handler. 
            onExecute = FlowValveCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute) # keep the handler referenced beyond this function

            # Connect to the command event handler. 
            onExecutePreview = FlowValveCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview) # keep the handler referenced beyond this function

            # Connect to the command destroyed event.
            onDestroy = FlowValveCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy) # keep the handler referenced beyond this function

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Define the command dialog image/illustration
            _imgInput = inputs.addImageCommandInput('FlowValve', 'Flow valve', 'resources/flow_valve_illustration.png')
            _imgInput.isFullWidth = True

            # Define the value inputs for the command
            _initTheta = adsk.core.ValueInput.createByReal(defaultTheta)
            inputs.addValueInput('theta', 'Angle (θ)', 'deg', _initTheta)

            _initD = adsk.core.ValueInput.createByReal(defaultD)
            inputs.addValueInput('D', 'Diameter (D)', 'cm', _initD)
            
            # Define a read-only textbox for the command
            _initP = round(defaultD/cos(pi/2-defaultTheta), 2)
            inputs.addTextBoxCommandInput('P', 'Transducer distance (P)', f'~ {_initP} cm', 1, True)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class FlowValve():
    def __init__(self):
        # Design parameters
        self._theta = defaultTheta           # angle between sensor-pipe and main-pipe
        self._D = defaultD                   # main pipe diameter
        self._d = 15                          # sensor pipe diameter
        # self._P = defaultP                 # distance between transducers
        self._P = self.calculate_P()         # distance between transducers

    # Properties
    @property
    def theta(self) -> float:
        """Angle between sensor-pipe and main-pipe."""
        return self._theta
    @theta.setter
    def theta(self, value: float):
        """Angle between sensor-pipe and main-pipe."""
        self._theta = value
        self.calculate_P()
    @property
    def D(self) -> float:
        """Main-pipe diameter."""
        return self._D
    @D.setter
    def D(self, value: float):
        """Main-pipe diameter."""
        self._D = value
        self.calculate_P()
    @property
    def P(self) -> float:
        """Distance between transducers."""
        return self._P

    # Methods
    def calculate_P(self):
        self._P = self._D/cos(pi/2-self._theta)
        return self._P
    
    def create_flow_valve(self):
        """Creates and builds the flow valve based on specified property values"""

        new_comp = createNewComponent()
        if new_comp is None:
            ui.messageBox('New component failed to create', 'New Component Failed')
            return

        new_comp.name = f'Flow-valve (D{self.D}cm θ{degrees(self.theta)}deg)'
        # Defining a global center point
        center_global = new_comp.originConstructionPoint.geometry

        # SENSOR PIPE ------------------------------------------------------------------
        # Create angled construction plane
        const_plane_sp_input = new_comp.constructionPlanes.createInput()
        const_plane_sp_input.setByAngle(linearEntity=new_comp.xConstructionAxis, angle=adsk.core.ValueInput.createByReal(self.theta), planarEntity=new_comp.xYConstructionPlane)
        const_plane_sp = new_comp.constructionPlanes.add(const_plane_sp_input)

        # Create sketch on angled construction plane and center point for sketch
        sketch_sp = new_comp.sketches.add(const_plane_sp)
        center_sp = sketch_sp.modelToSketchSpace(center_global)
        
        # Draw circles
        circles_sp = sketch_sp.sketchCurves.sketchCircles
        # Draw outer circle
        circle_sp_o = circles_sp.addByCenterRadius(centerPoint=center_sp, radius=self._d/2)
        # Draw inner circle
        circle_sp_i = circles_sp.addByCenterRadius(centerPoint=circle_sp_o.centerSketchPoint, radius=self._d/2-self._d/10)

        # Extrude (new body)
        pipe_sp_profile = sketch_sp.profiles.item(0)  # get the pipe profile (profile between inner and outer circle)
        ext_pipe_sp_input = new_comp.features.extrudeFeatures.createInput(profile=pipe_sp_profile, operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ext_pipe_sp_input.setDistanceExtent(isSymmetric=True, distance=adsk.core.ValueInput.createByReal(self.P/2 + 70))
        new_comp.features.extrudeFeatures.add(ext_pipe_sp_input)
        # ------------------------------------------------------------------------------
        

        # MAIN PIPE --------------------------------------------------------------------
        # Create sketch on xY construction plane and center point for sketch
        sketch_mp = new_comp.sketches.add(new_comp.xYConstructionPlane)
        center_mp = sketch_mp.modelToSketchSpace(center_global)
        
        # Draw circles
        circles_mp = sketch_mp.sketchCurves.sketchCircles
        # Draw outer circle
        circle_mp_o = circles_mp.addByCenterRadius(centerPoint=center_mp, radius=self.D/2)
        # Draw inner circle
        circle_mp_i = circles_mp.addByCenterRadius(centerPoint=circle_mp_o.centerSketchPoint, radius=self.D/2-self.D/10)

        # Create object collection of profiles and extrude cut
        profiles_mp = adsk.core.ObjectCollection.create()
        [profiles_mp.add(profile) for profile in sketch_mp.profiles]
        ext_pipe_mp_cut_input = new_comp.features.extrudeFeatures.createInput(profile=profiles_mp, operation=adsk.fusion.FeatureOperations.CutFeatureOperation)
        # ext_pipe_mp_cut_input.setAllExtent(direction=adsk.fusion.ExtentDirections.SymmetricExtentDirection)  # does not extrude symmetric for some reason...
        ext_pipe_mp_cut_input.setDistanceExtent(isSymmetric=True, distance=adsk.core.ValueInput.createByReal(self.P/2 + 70*3))
        new_comp.features.extrudeFeatures.add(ext_pipe_mp_cut_input)

        # Extrude join pipe profile
        pipe_mp_profile = sketch_mp.profiles.item(0)  # get the pipe profile (profile between inner and outer circle)
        ext_pipe_mp_join_input = new_comp.features.extrudeFeatures.createInput(profile=pipe_mp_profile, operation=adsk.fusion.FeatureOperations.JoinFeatureOperation)
        ext_pipe_mp_join_input.setDistanceExtent(isSymmetric=True, distance=adsk.core.ValueInput.createByReal(self.P/2 + 70*3/2))
        new_comp.features.extrudeFeatures.add(ext_pipe_mp_join_input)
        # ------------------------------------------------------------------------------


        # Extrude center profile of SENSOR PIPE, to "open" MAIN PIPE
        pipe_sp_profile_i = sketch_sp.profiles.item(1)  # get the center profile (profile by inner circle)
        ext_pipe_sp_i_input = new_comp.features.extrudeFeatures.createInput(profile=pipe_sp_profile_i, operation=adsk.fusion.FeatureOperations.CutFeatureOperation)
        # ext_pipe_sp_i_input.setAllExtent(direction=adsk.fusion.ExtentDirections.SymmetricExtentDirection)  # does not extrude symmetric for some reason...
        ext_pipe_sp_i_input.setDistanceExtent(isSymmetric=True, distance=adsk.core.ValueInput.createByReal(self.P/2 + 70*3))
        new_comp.features.extrudeFeatures.add(ext_pipe_sp_i_input)
        

# ------------------------------------------------------------------------------

def run(context):
    try:
        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = ui.commandDefinitions.itemById('FlowValve')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition('FlowValve', 'Create Flow-Valve', 'Create a customized flow-valve.', './resources') # relative resource file path is specified

        # Connect to the command created event.
        onCommandCreated = FlowValveCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()

        # Execute the command definition.
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event _handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
