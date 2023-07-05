import adsk.core as core
import adsk.fusion as fusion
import pathlib
from ...lib import fusion360utils as futil
from ... import config
from .LanguageMessage import LanguageMessage
from .ktkCmdInputHelper import TextBoxCommandInputHelper
from .ktkCmdInputHelper import TableCommandInputHelper
from .SketchAnalysisFactry import SketchAnalysisFactry
from .SketchAnalysisFactry import CustomGraphicsFactry

THIS_DIR = pathlib.Path(__file__).resolve().parent

app = core.Application.get()
ui = app.userInterface

# lang msg
_lm = LanguageMessage()

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_sketchAnalysis"
CMD_NAME = _lm.s("Sketch Analysis")
CMD_Description = _lm.s(
    "Look for elements of lack of restraint in the sketch.")

IS_PROMOTED = False

WORKSPACE_ID = "FusionSolidEnvironment"
PANEL_ID = "SketchConstraintsPanel"
COMMAND_BESIDE_ID = ""
ICON_FOLDER = str(THIS_DIR / "resources")

local_handlers = []

_infoIpt: "TextBoxCommandInputHelper" = None
_entsIpt: "TableCommandInputHelper" = None
_cg: "CustomGraphicsFactry" = None
_native = []
_colorRGB = [255, 0, 0]


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
    # inputs
    inputs: core.CommandInputs = args.command.commandInputs

    global _infoIpt
    _infoIpt = TextBoxCommandInputHelper(
        "_infoIptId",
        _lm.s("Result"),
        "",
        2,
        True,
    )
    _infoIpt.register(inputs)

    global _entsIpt
    _entsIpt = TableCommandInputHelper(
        "_entsIptId",
        _lm.s("insufficient restraints"),
        "1",
    )
    _entsIpt.register(inputs)

    # event
    futil.add_handler(
        args.command.inputChanged,
        command_input_changed,
        local_handlers=local_handlers
    )

    futil.add_handler(
        args.command.executePreview,
        command_preview,
        local_handlers=local_handlers
    )

    futil.add_handler(
        args.command.destroy,
        command_destroy,
        local_handlers=local_handlers
    )

    # other
    args.command.isOKButtonVisible = False

    global _cg, _colorRGB
    _cg = CustomGraphicsFactry("SketchAnalysis", _colorRGB)


def command_preview(args: core.CommandEventArgs) -> None:
    skt: fusion.Sketch = fusion.Sketch.cast(
        futil.app.activeEditObject
    )
    if not skt:
        return

    global _native
    entLst, _native = SketchAnalysisFactry.findLackConstraints(skt)

    global _infoIpt, _cg, _entsIpt
    if len(entLst) > 0:
        _cg.updateCurves(entLst)
        _infoIpt.obj.text = _lm.s(
            f"Number of elements with missing restraints") + f" : {len(entLst)}"

        for ent in entLst:
            shortType = ent.objectType.split("::")[-1]
            if hasattr(ent, "fromPoint"):
                if ent.fromPoint:
                    shortType = "Point3D"

            _entsIpt.add(
                _lm.s(shortType)
            )

    else:
        _cg.removeCG()
        _infoIpt.obj.text = _lm.s("All are restrained")


def command_input_changed(args: core.InputChangedEventArgs):
    changed_input = args.input
    if changed_input.objectType != "adsk::core::StringValueCommandInput":
        return

    idx = int(changed_input.id.split("_")[-1])
    global _native
    move_camera(_native[idx])


def command_destroy(args: core.CommandEventArgs):
    global local_handlers
    local_handlers = []


def move_camera(ent):
    pnt: core.Point3D = get_target_point(ent)
    if not pnt:
        return

    vp: core.Viewport = core.Application.get().activeViewport
    cam: core.Camera = vp.camera
    tgt: core.Point3D = cam.target
    vec: core.Vector3D = tgt.vectorTo(pnt)
    eye: core.Point3D = cam.eye.copy()
    eye.translateBy(vec)
    cam.target = pnt
    cam.eye = eye
    vp.camera = cam


def get_target_point(ent) -> core.Point3D:
    pnt: core.Point3D = None

    try:
        if hasattr(ent, "center"):
            pnt = ent.center
        else:
            nbs: core.NurbsCurve3D = None
            if hasattr(ent, "asNurbsCurve"):
                nbs = ent.asNurbsCurve
            else:
                nbs = ent

            eva: core.CurveEvaluator3D = nbs.evaluator
            _, sPrm, ePrm = eva.getParameterExtents()
            prm = (sPrm + ePrm) * 0.5
            _, pnt = eva.getPointAtParameter(prm)

        return pnt

    except:
        return None
