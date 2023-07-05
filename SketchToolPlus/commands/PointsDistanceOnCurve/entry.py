import adsk.core as core
import adsk.fusion as fusion
import pathlib
from ...lib import fusion360utils as futil
from ... import config
from .LanguageMessage import LanguageMessage
from .ktkCmdInputHelper import SelectionCommandInputHelper
from .ktkCmdInputHelper import TextBoxCommandInputHelper
from .PointsDistanceOnCurveFactry import PointsDistanceOnCurveFactry as Fact
from .CustomGraphicsFactry import CustomGraphicsFactry

THIS_DIR = pathlib.Path(__file__).resolve().parent

app = core.Application.get()
ui = app.userInterface

# lang msg
_lm = LanguageMessage()

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_PointsDistanceOnCurve"
CMD_NAME = _lm.s("Distance between 2 points on curve")
CMD_Description = _lm.s(
    "Measures the distance on a curve between two specified points.")

IS_PROMOTED = False

WORKSPACE_ID = "FusionSolidEnvironment"
PANEL_ID = "InspectPanel"
COMMAND_BESIDE_ID = ""
ICON_FOLDER = str(THIS_DIR / "resources")

local_handlers = []

_crvIpt: "SelectionCommandInputHelper" = None
_pntIpt: "SelectionCommandInputHelper" = None
_txtResIpt: "TextBoxCommandInputHelper" = None
_unitsMgr: core.UnitsManager = None
_cgFact: "CustomGraphicsFactry" = None
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

    des: fusion.Design = fusion.Design.cast(futil.app.activeProduct)
    if not des:
        return

    if not fusion.Sketch.cast(futil.app.activeEditObject):
        futil.ui.messageBox(_lm.s("Available only in sketch edit mode."))
        return

    # inputs
    inputs: core.CommandInputs = args.command.commandInputs

    global _crvIpt
    _crvIpt = SelectionCommandInputHelper(
        "_crvIptId",
        _lm.s("Sketch Curve"),
        _lm.s(
            "Select sketch curve of support."),
        ['SketchCurves',],
    )
    _crvIpt.register(inputs)

    global _pntIpt
    _pntIpt = SelectionCommandInputHelper(
        "_pntIptId",
        _lm.s("Sketch Points"),
        _lm.s(
            "Select two points on the curve to be measured."),
        ['SketchPoints',],
    )
    _pntIpt.register(inputs)
    _pntIpt.obj.setSelectionLimits(2, 2)

    global _txtResIpt
    _txtResIpt = TextBoxCommandInputHelper(
        "_txtResIptId",
        _lm.s("Result"),
        "-",
        2,
        True,
    )
    _txtResIpt.register(inputs)

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
        args.command.validateInputs,
        command_validateInputs,
        local_handlers=local_handlers
    )

    futil.add_handler(
        args.command.destroy,
        command_destroy,
        local_handlers=local_handlers
    )

    # other
    args.command.isOKButtonVisible = False

    global _unitsMgr
    _unitsMgr = futil.app.activeProduct.unitsManager

    global _cgFact, _previewIconPath
    _cgFact = CustomGraphicsFactry(
        CMD_ID,
        _previewIconPath)


def command_preview(args: core.CommandEventArgs) -> None:
    global _crvIpt, _pntIpt

    crv: fusion.SketchEntity = _crvIpt.obj.selection(0).entity
    pnt1: fusion.SketchPoint = _pntIpt.obj.selection(0).entity
    pnt2: fusion.SketchPoint = _pntIpt.obj.selection(1).entity

    length, _ = Fact.getPoint2PointLengthOnCurve(crv, pnt1, pnt2)

    global _unitsMgr
    ratio = _unitsMgr.convert(
        1,
        _unitsMgr.internalUnits,
        _unitsMgr.defaultLengthUnits
    )

    decimal = futil.app.preferences.unitAndValuePreferences.generalPrecision

    msgLst = [
        _lm.s("Support length") +
        f": {round(crv.length * ratio, decimal)} {_unitsMgr.defaultLengthUnits}",
        _lm.s("Distance") +
        f": {round(length * ratio, decimal)} {_unitsMgr.defaultLengthUnits}",
    ]
    global _txtResIpt
    _txtResIpt.obj.text = "\n".join(msgLst)

    # show point
    crvs = getExtractCurves(crv, pnt1, pnt2)
    pntLst = []
    pntLst.extend(getStrokesPoints(crvs, 0.1))
    _cgFact.updatePoints(pntLst)


def command_inputChanged(args: core.InputChangedEventArgs):
    global _crvIpt, _pntIpt
    if _crvIpt.obj.selectionCount < 1:
        _pntIpt.obj.clearSelection()
        _crvIpt.obj.hasFocus = True
    else:
        _pntIpt.obj.hasFocus = True

    global _txtResIpt
    if _crvIpt.obj.selectionCount > 0 and _pntIpt.obj.selectionCount == 2:
        pass
    else:
        _txtResIpt.obj.text = "-"
    pass


def command_preSelect(args: core.SelectionEventArgs):
    global _crvIpt, _pntIpt
    if args.activeInput == _crvIpt.obj:
        if not Fact.isSketchMatch(args.selection.entity):
            args.isSelectable = False
    elif args.activeInput == _pntIpt.obj:
        try:
            crv = _crvIpt.obj.selection(0).entity
            pnt = args.selection.entity
            if not Fact.isCurveOnPoint(crv, pnt):
                args.isSelectable = False
        except:
            pass


def command_validateInputs(args: core.ValidateInputsEventArgs):
    global _crvIpt, _pntIpt
    if _crvIpt.obj.selectionCount > 0 and _pntIpt.obj.selectionCount == 2:
        args.areInputsValid = True
    else:
        args.areInputsValid = False
    pass


def command_destroy(args: core.CommandEventArgs):
    global local_handlers
    local_handlers = []


def getExtractCurves(
    crv: fusion.SketchEntity,
    pnt1: fusion.SketchPoint,
    pnt2: fusion.SketchPoint,
) -> list:

    mat: core.Matrix3D = None
    try:
        # occ
        occ: fusion.Occurrence = crv.assemblyContext
        mat = occ.transform
    except:
        # root
        mat = core.Matrix3D.create()
    mat.invert()

    geo = crv.worldGeometry
    nurbs: core.NurbsCurve3D = None
    if hasattr(geo, 'asNurbsCurve'):
        nurbs = geo.asNurbsCurve
    else:
        nurbs = geo

    _, prmLst = Fact.getPoint2PointLengthOnCurve(crv, pnt1, pnt2)

    extractLst = []
    for prms in prmLst:
        if abs(prms[0] - prms[1]) < 0.01:
            continue

        tmp: core.NurbsCurve3D = nurbs.extract(prms[0], prms[1])
        tmp.transformBy(mat)
        extractLst.append(tmp)

    return extractLst


def getStrokesPoints(
    crvs: list,
    tolerance: float = 1
) -> list:

    pntLst = []
    for crv in crvs:
        eva: core.CurveEvaluator3D = crv.evaluator
        _, startPnt, endPnt = eva.getEndPoints()
        _, sPrmEnd = eva.getParameterAtPoint(startPnt)
        _, ePrmEnd = eva.getParameterAtPoint(endPnt)
        _, pnts = eva.getStrokes(sPrmEnd, ePrmEnd, tolerance)
        pntLst.extend(pnts)

    return pntLst
