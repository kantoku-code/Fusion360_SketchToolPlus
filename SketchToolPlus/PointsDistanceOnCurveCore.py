# FusionAPI_python 
# Author-kantoku

import adsk.core, adsk.fusion, traceback
from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase
from .DividerFactry import DividerFactry
from .CustomGraphicsFactry import CustomGraphicsFactry
import dataclasses

_debug = False

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


# dialog
# preview
_previewIconPath = 'resources/PointsDistanceOnCurve/preview.png'

# curve
_selCrvInfo = SelIptInfo(
    None,
    'dlgSelCrv',
    'スケッチ線',
    'サポートのスケッチの線を選択',
    ['SketchCurves'])

# point
_selPntInfo = SelIptInfo(
    None,
    'dlgSelPnt',
    'スケッチ点',
    '測定するスケッチの点を選択',
    ['SketchPoints'])

# result
_txtResInfo = TxtIptInfo(
    None,
    'dlgTxtRes',
    '結果',
    '-',
    2,
    True)

# 単位
_covUnit = [
    0.0,
    'cm']



class PointsDistanceOnCurveCore(Fusion360CommandBase):
    _handlers = []
    _cgFactry = None

    def __init__(self, cmd_def, debug):
        super().__init__(cmd_def, debug)
        pass

    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass
        ao = AppObjects()
        try:
            global _selCrvInfo, _selPntInfo

            crv = _selCrvInfo.obj.selection(0).entity
            pnt1 = _selPntInfo.obj.selection(0).entity
            pnt2 = _selPntInfo.obj.selection(1).entity

            if _debug:
                self.getExtractCurves(crv, pnt1, pnt2)

            global _covUnit, _txtResInfo
            msg = ''
            decimal = ao.app.preferences.unitAndValuePreferences.generalPrecision

            # ok
            length, _ = DividerFactry.getPoint2PointLengthOnCurve(crv, pnt1, pnt2)
            msg = f'サポート長さ{round(crv.length * _covUnit[0], decimal)} {_covUnit[1]}\n'
            msg += f'距離：{round(length * _covUnit[0], decimal)} {_covUnit[1]}'
            _txtResInfo.obj.text = msg

            # show point
            crvs = self.getExtractCurves(crv, pnt1, pnt2)
            pntLst = []
            pntLst.extend(self.getStrokesPoints(crvs, 0.1))
            self._cgFactry.updatePoints(pntLst)

            # # show crv -　おかしい表示の時あり中止
            # self._cgFactry.updateCurves(
            #     self.getExtractCurves(crv, pnt1, pnt2),
            #     True
            #     )

        except:
            ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        try:
            del self._cgFactry
        except:
            pass

    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        ao = AppObjects()
        try:
            global _selCrvInfo, _selPntInfo

            # focus
            if _selCrvInfo.obj.selectionCount < 1:
                _selPntInfo.obj.clearSelection()
                _selCrvInfo.obj.hasFocus = True
            else:
                _selPntInfo.obj.hasFocus = True

        except:
            ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = AppObjects()

        if not adsk.fusion.Sketch.cast(ao.design.activeEditObject):
            ao.ui.messageBox('スケッチのみ使用できます')
            return

        # -- event --
        onPreSelect = self.PreSelectHandler()
        command.preSelect.add(onPreSelect)
        self._handlers.append(onPreSelect)

        onValid = self.ValidateInputHandler()
        command.validateInputs.add(onValid)
        self._handlers.append(onValid)

        # -- Dialog --
        command.isOKButtonVisible =False

        # curve
        global _selCrvInfo
        _selCrvInfo.obj = inputs.addSelectionInput(
            _selCrvInfo.id,
            _selCrvInfo.name,
            _selCrvInfo.commandPrompt)
        [_selCrvInfo.obj.addSelectionFilter(s) for s in _selCrvInfo.filter]

        # point
        global _selPntInfo
        _selPntInfo.obj = inputs.addSelectionInput(
            _selPntInfo.id,
            _selPntInfo.name,
            _selPntInfo.commandPrompt)
        [_selPntInfo.obj.addSelectionFilter(s) for s in _selPntInfo.filter]
        _selPntInfo.obj.setSelectionLimits(2, 2)

        global _txtResInfo
        _txtResInfo.obj = inputs.addTextBoxCommandInput(
            _txtResInfo.id,
            _txtResInfo.name,
            _txtResInfo.text,
            _txtResInfo.numRows,
            _txtResInfo.isReadOnly)

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
    def getExtractCurves(
        self,
        crv : adsk.fusion.SketchEntity,
        pnt1 :adsk.fusion.SketchPoint,
        pnt2 :adsk.fusion.SketchPoint
        ) -> list:

        # def getMatrix3D(
        #     crv : adsk.fusion.SketchEntity
        #     ) -> adsk.core.Matrix3D:

        #     ao = AppObjects()

        #     actObj = ao.design.activeEditObject()
        #     actType = actObj.objectType.split('::')[-1]

        #     if actType == 'Component':
        #         pass
        #         # ここから

        #     mat = adsk.core.Matrix3D.cast(None)
        #     try:
        #         # occ
        #         occ :adsk.fusion.Occurrence = crv.assemblyContext
        #         mat = occ.transform
        #     except:
        #         # root
        #         mat = adsk.core.Matrix3D.create()
        #     mat.invert()

        # get Matrix3D
        # スケッチ内のみ対応
        mat = adsk.core.Matrix3D.cast(None)
        try:
            # occ
            occ :adsk.fusion.Occurrence = crv.assemblyContext
            mat = occ.transform
        except:
            # root
            mat = adsk.core.Matrix3D.create()
        mat.invert()


        geo = crv.worldGeometry
        nurbs = adsk.core.NurbsCurve3D.cast(None)
        if hasattr(geo, 'asNurbsCurve'):
            nurbs = geo.asNurbsCurve
        else:
            nurbs = geo

        _, prmLst = DividerFactry.getPoint2PointLengthOnCurve(crv, pnt1, pnt2)

        extractLst = []
        for prms in prmLst:
            if abs(prms[0] - prms[1]) < 0.01:
                continue

            tmp :adsk.core.NurbsCurve3D = nurbs.extract(prms[0],prms[1])
            tmp.transformBy(mat)
            extractLst.append(tmp)

            # debug
            if _debug:
                dumpMsg(f'getExtractCurves prm : {prms[0]} : {prms[1]}')

        return extractLst

    def getStrokesPoints(
        self,
        crvs : list,
        tolerance :float = 1
        ) -> list:

        pntLst = []
        for crv in crvs:
            eva :adsk.core.CurveEvaluator3D = crv.evaluator
            _, startPnt, endPnt = eva.getEndPoints()
            _, sPrmEnd = eva.getParameterAtPoint(startPnt)
            _, ePrmEnd = eva.getParameterAtPoint(endPnt)
            _, pnts = eva.getStrokes(sPrmEnd, ePrmEnd, tolerance)
            pntLst.extend(pnts)

        return pntLst

    # 未使用
    def getRangePoints(
        self,
        crv : adsk.fusion.SketchEntity,
        pnt1 :adsk.fusion.SketchPoint,
        pnt2 :adsk.fusion.SketchPoint,
        count :int
        ) -> list:

        geo = crv.worldGeometry

        _, prmLst = DividerFactry.getPoint2PointLengthOnCurve(crv, pnt1, pnt2)
        list(prmLst)

        pich = (prmLst[0] + prmLst[1]) / count
        prms = [pich * idx for idx in range(count + 1)]
        eva :adsk.core.CurveEvaluator3D = geo.evaluator
        _, pnts = eva.getPointsAtParameters(prms)

        # debugs
        if _debug:
            dumpMsg(f'getRangePoints prm : {prms}')

        return pnts

    # -- Support class --
    class PreSelectHandler(adsk.core.SelectionEventHandler):
        def __init__(self):
            super().__init__()

        def notify(self, args):
            try:
                args = adsk.core.SelectionEventArgs.cast(args)
                args.isSelectable = False

                global _selCrvInfo
                if args.activeInput == _selCrvInfo.obj:
                    if not DividerFactry.isSketchMatch(args.selection.entity):
                        return

                    args.isSelectable = True
                    return

                global _selPntInfo
                if args.activeInput == _selPntInfo.obj:
                    try:
                        crv = _selCrvInfo.obj.selection(0).entity
                        pnt = args.selection.entity
                        if DividerFactry.isCurveOnPoint(crv, pnt):
                            args.isSelectable = True
                            return
                    except:
                        pass
            except:
                ao = AppObjects()
                ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


    class ValidateInputHandler(adsk.core.ValidateInputsEventHandler):
        def __init__(self):
            super().__init__()
        def notify(self, args):
            global _selCrvInfo, _selPntInfo

            if _selCrvInfo.obj.selectionCount > 0 and _selPntInfo.obj.selectionCount == 2:
                args.areInputsValid = True
            else:
                args.areInputsValid = False
            pass


# --debug --
def dumpMsg(msg :str):
    adsk.core.Application.get().userInterface.palettes.itemById('TextCommands').writeText(str(msg))