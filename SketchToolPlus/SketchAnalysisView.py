#Author-kantoku
#Description-拘束不足の要素を強調して表示させます。
#Fusion360API Python

# ハイライトさせる色のRGB
_colorRGB = [255,0,0]

import adsk.core
import adsk.fusion

from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase
from .ktkCmdInputHelper import TextBoxCommandInputHelper
from .ktkCmdInputHelper import TableCommandInputHelper
from .SketchAnalysisFactry import SketchAnalysisFactry
from .SketchAnalysisFactry import CustomGraphicsFactry

_info = TextBoxCommandInputHelper(
    'info',
    '結果',
    '',
    5,
    True)

_ents = TableCommandInputHelper(
    'entLst',
    '拘束不足リスト',
    '1')

# エンティティの日本語名
_entityJapaneseMap = {
    'Arc3D' : '円弧',
    'Circle3D' : '円',
    'Curve3D' : '曲線',
    'Ellipse3D' : '楕円',
    'EllipticalArc3D' : '楕円弧',
    'InfiniteLine3D' : '無限直線',
    'Line3D' : '直線',
    'NurbsCurve3D' : '曲線',
    'Point3D' : '点',
    'SketchConicCurve' : '円錐曲線'
}

_cg = None

class SketchAnalysisView(Fusion360CommandBase):
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        skt = adsk.fusion.Sketch.cast(ao.design.activeEditObject)
        if not skt:
            return

        entLst, self.native = SketchAnalysisFactry.findLackConstraints(skt)

        global _info, _cg, _ents
        if len(entLst) > 0:
            _cg.updateCurves(entLst)
            _info.obj.text = f'{len(entLst)}個の拘束不足の要素があります!'

            global _entityJapaneseMap
            for ent in entLst:
                txt = ent.objectType.split('::')[-1]
                if hasattr(ent, 'fromPoint'):
                    if ent.fromPoint:
                        txt = 'Point3D'

                if txt in _entityJapaneseMap:
                    _ents.add(_entityJapaneseMap[txt])
                else:
                    _ents.add(txt)

        else:
            _cg.removeCG()
            _info.obj.text = '拘束不足の要素は見つかりませんでした'

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        if changed_input.objectType != 'adsk::core::StringValueCommandInput':
            return

        idx = int(changed_input.id.split('_')[-1])
        self.moveCamera(self.native[idx])

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        command.isOKButtonVisible = False

        global _info, _ents
        _info.register(inputs)
        _ents.register(inputs)

        self.native = []

        global _cg, _colorRGB
        _cg = CustomGraphicsFactry('SketchAnalysis', _colorRGB)

    # -- helper --
    def moveCamera(self, ent):
        pnt :adsk.core.Point3D = self.getTargetPoint(ent)
        if not pnt:
            return

        app = adsk.core.Application.get()
        vp :adsk.core.Viewport = app.activeViewport
        cam :adsk.core.Camera = vp.camera
        tgt :adsk.core.Point3D = cam.target
        vec :adsk.core.Vector3D = tgt.vectorTo(pnt)
        eye :adsk.core.Point3D = cam.eye.copy()
        eye.translateBy(vec)
        cam.target = pnt
        cam.eye = eye
        vp.camera = cam
    
    def getTargetPoint(self, ent) -> adsk.core.Point3D:
        pnt :adsk.core.Point3D = None

        try:
            if hasattr(ent, 'center'):
                pnt = ent.center
            else:
                nbs :adsk.core.NurbsCurve3D = None
                if hasattr(ent, 'asNurbsCurve'):
                    nbs = ent.asNurbsCurve
                else:
                    nbs = ent

                eva :adsk.core.CurveEvaluator3D = nbs.evaluator
                _, sPrm, ePrm = eva.getParameterExtents()
                prm = (sPrm + ePrm) * 0.5
                _, pnt = eva.getPointAtParameter(prm)

            return pnt
        
        except:
            return None