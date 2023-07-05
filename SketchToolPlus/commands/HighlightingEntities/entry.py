import adsk.core as core
import adsk.fusion as fusion
import pathlib
from ...lib import fusion360utils as futil
from ... import config
from .LanguageMessage import LanguageMessage
from .ktkCmdInputHelper import TextBoxCommandInputHelper
from .ktkCmdInputHelper import SelectionCommandInputHelper
from .HighlightingEntitiesFactry import HighlightingEntitiesFactry

THIS_DIR = pathlib.Path(__file__).resolve().parent

app = core.Application.get()
ui = app.userInterface

# lang msg
_lm = LanguageMessage()

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_HighlightingEntities"
CMD_NAME = _lm.s("Highlighting Entities")
CMD_Description = _lm.s(
    "Highlight sketch elements related to geometric constraints.")

IS_PROMOTED = False

WORKSPACE_ID = "FusionSolidEnvironment"
PANEL_ID = "SketchConstraintsPanel"
COMMAND_BESIDE_ID = ""
ICON_FOLDER = str(THIS_DIR / "resources")

local_handlers = []

_fact: "HighlightingEntitiesFactry" = None
_infoIpt: "TextBoxCommandInputHelper" = None
_entsIpt: "SelectionCommandInputHelper" = None


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
        _lm.s("Highlight sketch elements related to geometric constraints."),
        "",
        2,
        True,
    )
    _infoIpt.register(inputs)

    global _entsIpt
    _entsIpt = SelectionCommandInputHelper(
        "_entsIptId",
        _lm.s("Select Geometric Constraints"),
        _lm.s("Select Geometric Constraints"),
        [],
    )
    _entsIpt.register(inputs)
    _entsIpt.obj.isVisible = False

    # event
    futil.add_handler(
        args.command.preSelect,
        command_preSelect,
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

    global _fact
    _fact = HighlightingEntitiesFactry()


def command_preview(args: core.CommandEventArgs) -> None:

    global _fact, _entsIpt
    _fact.highlight_constraint_entities(
        _entsIpt.obj.selection(0).entity
    )


def command_destroy(args: core.CommandEventArgs):
    global local_handlers
    local_handlers = []


def command_preSelect(args: core.SelectionEventArgs):
    entity = args.selection.entity

    global _fact
    if not _fact.is_geometric_constraint(entity):
        args.isSelectable = False
