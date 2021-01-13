# FusionAPI_python 
# Author-kantoku

import adsk.core, adsk.fusion, traceback
import dataclasses
from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase
from .DividerFactry import DividerFactry
from .CustomGraphicsFactry import CustomGraphicsFactry


@dataclasses.dataclass
class SelIptInfo:
    obj : adsk.core.SelectionCommandInput
    id : str
    name : str
    commandPrompt : str
    filter : list

@dataclasses.dataclass
class TxtIptInfo:
    obj : adsk.core.TextBoxCommandInput
    id : str
    name : str
    text : str
    numRows : int
    isReadOnly : bool

@dataclasses.dataclass
class IntSpinInfo:
    obj : adsk.core.IntegerSpinnerCommandInput
    id : str
    name : str
    min : int
    max : int
    spinStep : int
    initialValue : int


# dialog
# preview
_previewIconPath = 'resources/Divider/preview.png'

# curve
_selCrvInfo = SelIptInfo(
    None,
    'dlgSelCrv',
    'スケッチ線',
    '等間隔の点作成するスケッチの線を選択',
    ['SketchCurves'])

_txtCrvInfo = TxtIptInfo(
    None,
    'dlgTxtCrv',
    '長さ',
    '-',
    1,
    True)


# count
_splitInfo = IntSpinInfo(
    None,
    'dlgSplit',
    '分割数',
    1,
    30,
    1,
    3)

_txtSplitInfo = TxtIptInfo(
    None,
    'dlgTxtSplit',
    'ピッチ',
    '-',
    1,
    True)

# 単位
_covUnit = [
    0.0,
    'cm']


class DividerCore(Fusion360CommandBase):
    _handlers = []
    _cgFactry = None

    def __init__(self, cmd_def, debug):
        super().__init__(cmd_def, debug)
        pass

    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        try:
            global _selCrvInfo, _splitInfo

            if _selCrvInfo.obj.selectionCount < 1:
                return

            pnts = DividerFactry.getPreviewPoints(
                    _selCrvInfo.obj.selection(0).entity,
                    _splitInfo.obj.value)

            if len(pnts) < 1:
                return

            self._cgFactry.updatePoints(pnts)

        except:
            ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        del self._cgFactry

    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        ao = AppObjects()
        try:
            global _covUnit
            global _selCrvInfo, _txtCrvInfo
            global _splitInfo, _txtSplitInfo

            decimal = ao.app.preferences.unitAndValuePreferences.generalPrecision

            if _selCrvInfo.obj.selectionCount < 1:
                # crv non select
                _txtCrvInfo.obj.text = _txtCrvInfo.text
                _txtSplitInfo.obj.text = _txtSplitInfo.text
            else:
                # crv select
                crv = _selCrvInfo.obj.selection(0).entity
                length = round(crv.length * _covUnit[0], decimal)
                step = round(length / (_splitInfo.obj.value + 1), decimal)
                _txtCrvInfo.obj.text = f'{length} {_covUnit[1]}'
                _txtSplitInfo.obj.text = f'{step} {_covUnit[1]}'

        except:
            ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        try:
            global _selCrvInfo, _splitInfo

            DividerFactry.createDivider(
                _selCrvInfo.obj.selection(0).entity,
                _splitInfo.obj.value)

            _splitInfo.initialValue = _splitInfo.obj.value

        except:
            ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = AppObjects()
        command.isPositionDependent = True #効果無い・・・

        # -- event --
        onPreSelect = self.PreSelectHandler()
        command.preSelect.add(onPreSelect)
        self._handlers.append(onPreSelect)

        onValid = self.ValidateInputHandler()
        command.validateInputs.add(onValid)
        self._handlers.append(onValid)

        # -- Dialog --
        global _selCrvInfo
        # curve
        _selCrvInfo.obj = inputs.addSelectionInput(
            _selCrvInfo.id,
            _selCrvInfo.name,
            _selCrvInfo.commandPrompt)
        [_selCrvInfo.obj.addSelectionFilter(s) for s in _selCrvInfo.filter]

        global _txtCrvInfo
        _txtCrvInfo.obj = inputs.addTextBoxCommandInput(
            _txtCrvInfo.id,
            _txtCrvInfo.name,
            _txtCrvInfo.text,
            _txtCrvInfo.numRows,
            _txtCrvInfo.isReadOnly)


        # split count
        _splitInfo.obj = inputs.addIntegerSpinnerCommandInput(
            _splitInfo.id,
            _splitInfo.name,
            _splitInfo.min,
            _splitInfo.max,
            _splitInfo.spinStep,
            _splitInfo.initialValue)

        global _txtSplitInfo
        _txtSplitInfo.obj = inputs.addTextBoxCommandInput(
            _txtSplitInfo.id,
            _txtSplitInfo.name,
            _txtSplitInfo.text,
            _txtSplitInfo.numRows,
            _txtSplitInfo.isReadOnly)


        # init cg
        global _previewIconPath
        self._cgFactry = CustomGraphicsFactry(
            _selCrvInfo.id,
            _previewIconPath)

        # unit
        global _covUnit
        unitsMgr = ao.units_manager
        defLenUnit = unitsMgr.defaultLengthUnits
        tmp = unitsMgr.convert(1, unitsMgr.internalUnits, defLenUnit)
        _covUnit = [tmp, defLenUnit]


    # -- Support fanction --

    # -- Support class --
    class PreSelectHandler(adsk.core.SelectionEventHandler):
        def __init__(self):
            super().__init__()

        def notify(self, args):
            try:
                args = adsk.core.SelectionEventArgs.cast(args)
                args.isSelectable = False

                # unSelection
                actIpt = adsk.core.SelectionCommandInput.cast(args.activeInput)
                if not actIpt:
                    return

                # check Sketch Match
                if not DividerFactry.isSketchMatch(args.selection.entity):
                    return

                args.isSelectable = True

            except:
                ao = AppObjects()
                ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


    class ValidateInputHandler(adsk.core.ValidateInputsEventHandler):
        def __init__(self):
            super().__init__()
        def notify(self, args):
            global _selCrvInfo
            if _selCrvInfo.obj.selectionCount > 0:
                args.areInputsValid = True
            else:
                args.areInputsValid = False