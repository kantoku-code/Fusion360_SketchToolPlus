# Here you define the commands that will be added to your add-in.

# TODO Import the modules corresponding to the commands you created.
# If you want to add an additional command, duplicate one of the existing directories and import it here.
# You need to use aliases (import "entry" as "my_module") assuming you have the default module named "entry".
from .SketchAnalysis import entry as SketchAnalysis
from .HighlightingEntities import entry as HighlightingEntities
from .SketchPlane import entry as SketchPlane
from .PointsDistanceOnCurve import entry as PointsDistanceOnCurve
from .Divider import entry as Divider

# TODO add your imported modules to this list.
# Fusion will automatically call the start() and stop() functions.
commands = [
    SketchAnalysis,
    HighlightingEntities,
    PointsDistanceOnCurve,
    SketchPlane,
    Divider,
]


# Assumes you defined a "start" function in each of your modules.
# The start function will be run when the add-in is started.
def start():
    for command in commands:
        command.start()


# Assumes you defined a "stop" function in each of your modules.
# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()
