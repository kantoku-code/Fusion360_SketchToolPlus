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

_cg = None

class SketchAnalysisView(Fusion360CommandBase):
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        skt = adsk.fusion.Sketch.cast(ao.design.activeEditObject)
        if not skt:
            return

        lst = SketchAnalysisFactry.findLackConstraints(skt)

        global _info, _cg, _ents
        if len(lst) > 0:
            _cg.updateCurves(lst)
            _info.obj.text = f'{len(lst)}個の拘束不足の要素があります!'

            for ent in lst:
                txt = ent.objectType.split('::')[-1]
                if hasattr(ent, 'fromPoint'):
                    if ent.fromPoint:
                        txt = 'Point3D'
                _ents.add(txt)

        else:
            _cg.removeCG()
            _info.obj.text = '拘束不足の要素は見つかりませんでした'

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        pass

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        command.isOKButtonVisible = False

        global _info, _test
        _info.register(inputs)
        _ents.register(inputs)

        global _cg, _colorRGB
        _cg = CustomGraphicsFactry('SketchAnalysis', _colorRGB)