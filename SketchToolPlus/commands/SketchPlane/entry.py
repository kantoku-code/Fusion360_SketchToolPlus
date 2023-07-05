import adsk.core as core
import adsk.fusion as fusion
import pathlib
from ...lib import fusion360utils as futil
from ... import config
from .LanguageMessage import LanguageMessage
from .ktkCmdInputHelper import SelectionCommandInputHelper
from .SketchPlaneFactry import SketchPlaneFactry

THIS_DIR = pathlib.Path(__file__).resolve().parent

app = core.Application.get()
ui = app.userInterface

# lang msg
_lm = LanguageMessage()

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_SketchPlane"
CMD_NAME = _lm.s("Sketch Plane")
CMD_Description = _lm.s(
    "Find the plane at which the sketch was created.")

IS_PROMOTED = False

WORKSPACE_ID = "FusionSolidEnvironment"
PANEL_ID = "InspectPanel"
COMMAND_BESIDE_ID = ""
ICON_FOLDER = str(THIS_DIR / "resources")

local_handlers = []

_fact: "SketchPlaneFactry" = None
_sktIpt: "SelectionCommandInputHelper" = None


def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(
        CMD_ID, CMD_NAME,
        CMD_Description,
        ICON_FOLDER
    )
    futil.add_handler(cmd_def.commandCreated, command_created)
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
    control.isPromoted = IS_PROMOTED


def stop():
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    if command_control:
        command_control.deleteMe()

    if command_definition:
        command_definition.deleteMe()


def command_created(args: core.CommandCreatedEventArgs):

    des: fusion.Design = fusion.Design.cast(futil.app.activeProduct)
    if not des:
        return

    if des.designType != fusion.DesignTypes.ParametricDesignType:
        futil.ui.messageBox(
            _lm.s(
                "Only available in parametric mode."
            )
        )
        return

    # inputs
    inputs: core.CommandInputs = args.command.commandInputs

    global _sktIpt
    _sktIpt = SelectionCommandInputHelper(
        "_sktIptId",
        _lm.s("Sketch"),
        _lm.s(
            "Select the sketch element for which you want to examine the reference plane."),
        ['Sketches', 'SketchCurves', 'Profiles',],
    )
    _sktIpt.register(inputs)

    # event
    futil.add_handler(
        args.command.executePreview,
        command_preview,
        local_handlers=local_handlers
    )

    futil.add_handler(
        args.command.execute,
        command_execute,
        local_handlers=local_handlers
    )

    futil.add_handler(
        args.command.destroy,
        command_destroy,
        local_handlers=local_handlers
    )

    global _fact
    _fact = SketchPlaneFactry()


def command_preview(args: core.CommandEventArgs) -> None:
    global _sktIpt
    skt: fusion.Sketch = None
    selEnt = _sktIpt.obj.selection(0).entity
    if selEnt.objectType == fusion.Sketch.classType():
        skt = selEnt
    elif hasattr(selEnt, "parentSketch"):
        skt = selEnt.parentSketch
    else:
        return

    global _fact
    _fact.exec_preview(skt)


def command_execute(args: core.CommandEventArgs) -> None:
    global _sktIpt
    skt: fusion.Sketch = None
    selEnt = _sktIpt.obj.selection(0).entity
    if selEnt.objectType == fusion.Sketch.classType():
        skt = selEnt
    elif hasattr(selEnt, "parentSketch"):
        skt = selEnt.parentSketch
    else:
        return

    refPlane = _fact.get_ref_plane(skt)
    if not refPlane:
        return

    des: fusion.Design = fusion.Design.cast(futil.app.activeProduct)
    if not des:
        return

    selSets: core.SelectionSets = des.selectionSets
    selSets.add(
        [refPlane],
        _lm.s("Sketch Plane") + f" _ {skt.name}"
    )


def command_destroy(args: core.CommandEventArgs):
    global local_handlers
    local_handlers = []
