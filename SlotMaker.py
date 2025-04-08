import adsk.core
import adsk.fusion
import traceback
import math
import os

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(current_dir, 'resources')
        
        # Create a button command definition.
        buttonDef = cmdDefs.addButtonDefinition(
            'SlotMakerButton',
            'Create Slots',
            'Creates evenly spaced slots along selected lines on a face.',
            resources_dir,
            'slot_icon.png'  # Name of your icon file
        )
        
        # Connect to the command created event.
        onCommandCreated = CommandCreatedEventHandler()
        buttonDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        # Get the ADD-INS panel in the model workspace.
        addInsPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        
        # Add the button to the panel.
        buttonControl = addInsPanel.controls.addCommand(buttonDef)
        
        # Make the button visible in the panel.
        buttonControl.isVisible = True
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('SlotMakerButton')
        if cmdDef:
            cmdDef.deleteMe()
            
        addinsPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        cntrl = addinsPanel.controls.itemById('SlotMakerButton')
        if cntrl:
            cntrl.deleteMe()
            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            # Get the CommandInputs collection to create new inputs.
            inputs = cmd.commandInputs
            
            # Create selection input for the face
            faceSelInput = inputs.addSelectionInput(
                'faceSelection', 
                'Select Face', 
                'Select the face to create slots on'
            )
            faceSelInput.addSelectionFilter('Faces')
            faceSelInput.setSelectionLimits(1, 1)
            
            # Create selection input for the lines
            lineSelInput = inputs.addSelectionInput(
                'lineSelection', 
                'Select Lines', 
                'Select the lines to create slots along'
            )
            lineSelInput.addSelectionFilter('SketchLines')
            lineSelInput.setSelectionLimits(1, 0)  # Min 1, max unlimited
            
            # Create value input for number of slots
            inputs.addIntegerSpinnerCommandInput(
                'numSlots', 
                'Number of Slots', 
                1, 
                100, 
                1, 
                1
            )
            
            # Create value inputs for slot parameters
            inputs.addValueInput(
                'slotLength', 
                'Slot Length', 
                'mm', 
                adsk.core.ValueInput.createByReal(22.0)
            )
            inputs.addValueInput(
                'slotWidth', 
                'Slot Width', 
                'mm', 
                adsk.core.ValueInput.createByReal(5.0)
            )
            inputs.addValueInput(
                'slotDepth', 
                'Slot Depth', 
                'mm', 
                adsk.core.ValueInput.createByReal(15.0)
            )
            
            # Connect to the execute event.
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
        except:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            
            cmd = args.command
            inputs = cmd.commandInputs
            
            # Get the values from the command inputs
            face:adsk.fusion.BRepFace = inputs.itemById('faceSelection').selection(0).entity
            selectedLines = []
            lineSelection = inputs.itemById('lineSelection')
            for i in range(lineSelection.selectionCount):
                selectedLines.append(lineSelection.selection(i).entity)
            
            numSlots = inputs.itemById('numSlots').value
            slotLength = inputs.itemById('slotLength').value
            slotWidth = inputs.itemById('slotWidth').value
            slotDepth = inputs.itemById('slotDepth').value
            
            # Get the active design
            design = app.activeProduct
            if not design:
                ui.messageBox('No active Fusion design')
                return
                
            
            # Create a new sketch on the selected face
            design = adsk.fusion.Design.cast(design)
            sketches = face.body.parentComponent.sketches
            sketch: adsk.fusion.Sketch = sketches.add(face)


            
            # Process each selected line
            for line in selectedLines:

                # Project the line onto the sketch
                sketchLine: adsk.fusion.SketchLine = sketch.project(line)[0]
                sketchLine.isConstruction = True
                
                # Get line start and end points in sketch coordinates
                startPoint = sketchLine.startSketchPoint.geometry
                endPoint = sketchLine.endSketchPoint.geometry
                
                # Get line length
                lineLength = sketchLine.length
                lineVector = adsk.core.Vector3D.create(endPoint.x - startPoint.x, endPoint.y - startPoint.y, endPoint.z - startPoint.z)
                lineVector.normalize()

                # Create circles for numSlots
                for i in range(numSlots):
                    # Calculate slot center position
                    parameter = (i + 0.5) / (numSlots)

                    # Use sketch points directly
                    centerPoint = adsk.core.Point3D.create(
                        startPoint.x + lineVector.x * parameter * lineLength,
                        startPoint.y + lineVector.y * parameter * lineLength,
                        startPoint.z)
                    

                    # Create an offset vector that is perpendicular to the line vector
                    offsetVector = adsk.core.Vector3D.create(-lineVector.y, lineVector.x, 0)
                    offsetVector.normalize()
                    offsetVector.scaleBy(slotWidth / 2)

                    # Create a small circle at the center point
                    # circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(centerPoint, slotWidth / 2)
                     
                    # Calculate the left offset point
                    offsetLeft = adsk.core.Point3D.create(centerPoint.x + offsetVector.x, centerPoint.y + offsetVector.y, centerPoint.z)

                    # Calculate the right offset point
                    offsetRight = adsk.core.Point3D.create(centerPoint.x - offsetVector.x, centerPoint.y - offsetVector.y, centerPoint.z)

                    # Create start and end points for the Left and Right lines, they should be offset in the direction  by half the slot length from the offsetPoints and parallel to the line vector
                    startLeft = adsk.core.Point3D.create(offsetLeft.x + lineVector.x * slotLength / 2, offsetLeft.y + lineVector.y * slotLength / 2, offsetLeft.z)
                    endLeft = adsk.core.Point3D.create(offsetLeft.x - lineVector.x * slotLength / 2, offsetLeft.y - lineVector.y * slotLength / 2, offsetLeft.z)

                    startRight = adsk.core.Point3D.create(offsetRight.x + lineVector.x * slotLength / 2, offsetRight.y + lineVector.y * slotLength / 2, offsetRight.z)
                    endRight = adsk.core.Point3D.create(offsetRight.x - lineVector.x * slotLength / 2, offsetRight.y - lineVector.y * slotLength / 2, offsetRight.z)

                    # Create the Left and Right lines
                    lineLeft = sketch.sketchCurves.sketchLines.addByTwoPoints(startLeft, endLeft)
                    lineRight = sketch.sketchCurves.sketchLines.addByTwoPoints(startRight, endRight)

                    # Calculate the midpointStart (between startLeft and startRight) and midpointEnd (between endLeft and endRight)
                    midpointStart = adsk.core.Point3D.create((startLeft.x + startRight.x) / 2, (startLeft.y + startRight.y) / 2, (startLeft.z + startRight.z) / 2)
                    midpointEnd = adsk.core.Point3D.create((endLeft.x + endRight.x) / 2, (endLeft.y + endRight.y) / 2, (endLeft.z + endRight.z) / 2)

                    # Create the Left and Right arcs
                    arcLeftToRight = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(midpointStart, startLeft, - math.pi)
                    arcRightToLeft = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(midpointEnd, endRight, - math.pi)
                    

                    
            # Create the profile

            # show an ui message box with the number of profiles in the sketch
            ui.messageBox('Number of profiles in sketch: {}'.format(sketch.profiles.count))

            # If there are more than 1 profiles, we need to create a collection of all but the one that is actually the face
            if sketch.profiles.count > 1:
                profs = adsk.core.ObjectCollection.create()

                # Use area to guess the outer one
                largest_area = 0
                largest_profile = None

                for i in range(sketch.profiles.count):
                    profile = sketch.profiles.item(i)
                    area = profile.areaProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy).area
                    if area > largest_area:
                        largest_area = area
                        largest_profile = profile
                
                # loop through all profiles in the sketch, if the profile is not the largest one, add it to the collection
                for i in range(sketch.profiles.count):
                    profile = sketch.profiles.item(i)
                    if profile != largest_profile:
                        profs.add(profile)

            else:
                profs = sketch.profiles
            
            # Create extrusion input
            extrudes = face.body.parentComponent.features.extrudeFeatures
            extInput = extrudes.createInput(profs, adsk.fusion.FeatureOperations.CutFeatureOperation)
            
            # Set the extrusion distance
            distance = adsk.core.ValueInput.createByReal(slotDepth)
            
            # Create the extent definition
            extent = adsk.fusion.DistanceExtentDefinition.create(distance)
            extInput.setOneSideExtent(extent, adsk.fusion.ExtentDirections.NegativeExtentDirection)
            
            # # Get the body to cut from the face
            body = face.body
            
            # Set the direction to cut into the body
            extInput.participantBodies = [body]
            
            # Create the extrusion
            extrudes.add(extInput)

            
        except:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

handlers = [] 