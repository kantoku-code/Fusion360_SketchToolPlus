import adsk.core as core
import adsk.fusion as fusion
import pathlib
from ...lib import fusion360utils as futil
from ... import config
from .LanguageMessage import LanguageMessage
from .ktkCmdInputHelper import SelectionCommandInputHelper
from .ktkCmdInputHelper import TextBoxCommandInputHelper
from .ktkCmdInputHelper import IntegerSpinnerCommandInputHelper
from .DividerFactry import DividerFactry as Fact
from .CustomGraphicsFactry import CustomGraphicsFactry

THIS_DIR = pathlib.Path(__file__).resolve().parent

app = core.Application.get()
ui = app.userInterface

# lang msg
_lm = LanguageMessage()

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_Divider"
CMD_NAME = _lm.s("Divider")
CMD_Description = _lm.s(
    "Creates equally spaced points on the specified sketch curve.")

IS_PROMOTED = False

WORKSPACE_ID = "FusionSolidEnvironment"
PANEL_ID = "SketchPanel"
COMMAND_BESIDE_ID = ""
ICON_FOLDER = str(THIS_DIR / "resources")

local_handlers = []

_crvIpt: "SelectionCommandInputHelper" = None
_txtCrvIpt: "TextBoxCommandInputHelper" = None
_splitIpt: "IntegerSpinnerCommandInputHelper" = None
_pitchIpt: "TextBoxCommandInputHelper" = None
_unitsMgr: core.UnitsManager = None
_cgFact: "CustomGraphicsFactry " = None
_previewIconPath = str(THIS_DIR / "resources/preview.png")


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

    global _crvIpt
    _crvIpt = SelectionCommandInputHelper(
        "_crvIptId",
        _lm.s("Sketch Curve"),
        _lm.s(
            "Please select a sketch curve to create evenly spaced points."),
        ['SketchCurves',],
    )
    _crvIpt.register(inputs)

    global _txtCrvIpt
    _txtCrvIpt = TextBoxCommandInputHelper(
        "_txtCrvIptId",
        _lm.s("Length"),
        "-",
        1,
        True,
    )
    _txtCrvIpt.register(inputs)

    global _splitIpt
    _splitIpt = IntegerSpinnerCommandInputHelper(
        "_splitIptId",
        _lm.s("Division Count"),
        2,
        30,
        1,
        3,
    )
    _splitIpt.register(inputs)

    global _pitchIpt
    _pitchIpt = TextBoxCommandInputHelper(
        "_pitchIptId",
        _lm.s("Interval"),
        "-",
        1,
        True,
    )
    _pitchIpt.register(inputs)

    # event
    futil.add_handler(
        args.command.executePreview,
        command_preview,
        local_handlers=local_handlers
    )

    futil.add_handler(
        args.command.inputChanged,
        command_inputChanged,
        local_handlers=local_handlers
    )

    futil.add_handler(
        args.command.preSelect,
        command_preSelect,
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

    # other
    global _unitsMgr
    _unitsMgr = futil.app.activeProduct.unitsManager

    global _cgFact, _previewIconPath
    _cgFact = CustomGraphicsFactry(
        CMD_ID,
        _previewIconPath)


def command_preview(args: core.CommandEventArgs) -> None:
    global _crvIpt, _splitIpt

    pnts = Fact.getPreviewPoints(
        _crvIpt.obj.selection(0).entity,
        _splitIpt.obj.value)

    if len(pnts) < 1:
        return

    global _cgFact
    _cgFact.updatePoints(pnts)


def command_execute(args: core.ValidateInputsEventArgs):
    global _crvIpt, _splitIpt

    Fact.createDivider(
        _crvIpt.obj.selection(0).entity,
        _splitIpt.obj.value)

    _splitIpt.initialValue = _splitIpt.obj.value


def command_inputChanged(args: core.InputChangedEventArgs):
    decimal = futil.app.preferences.unitAndValuePreferences.generalPrecision

    global _crvIpt, _txtCrvIpt, _splitIpt, _pitchIpt
    if _crvIpt.obj.selectionCount < 1:
        # crv non select
        _txtCrvIpt.obj.text = _txtCrvIpt.text
        _pitchIpt.obj.text = _pitchIpt.text
    else:
        # crv select
        global _unitsMgr
        ratio = _unitsMgr.convert(
            1,
            _unitsMgr.internalUnits,
            _unitsMgr.defaultLengthUnits
        )

        crv = _crvIpt.obj.selection(0).entity
        length = round(crv.length * ratio, decimal)
        pitch = round(crv.length * ratio / (_splitIpt.obj.value + 1), decimal)
        _txtCrvIpt.obj.text = f"{length} {_unitsMgr.defaultLengthUnits}"
        _pitchIpt.obj.text = f'{pitch} {_unitsMgr.defaultLengthUnits}'


def command_preSelect(args: core.SelectionEventArgs):
    global _crvIpt
    if args.activeInput != _crvIpt.obj:
        return

    # check Sketch Match
    if not Fact.isSketchMatch(args.selection.entity):
        args.isSelectable = False


def command_destroy(args: core.CommandEventArgs):
    global local_handlers
    local_handlers = []
