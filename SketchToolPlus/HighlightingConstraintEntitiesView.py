#Author-kantoku
#Description-
#Fusion360API Python

# ハイライトさせる色のRGB
_colorRGB = [0,0,255]

import adsk
import adsk.core as core
import adsk.fusion as fusion

from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase
from .HighlightingConstraintEntitiesFactry import HighlightingConstraintEntitiesFactry

_infoIpt: core.TextBoxCommandInput = None
_selIpt: core.SelectionCommandInput = None

_fact:'HighlightingConstraintEntitiesFactry' = None

_handlers = []

class HighlightingConstraintEntitiesView(Fusion360CommandBase):
    def on_preview(self, command: core.Command, inputs: core.CommandInputs, args, input_values):
        global _fact, _selIpt
        _fact.highlight_constraint_entities(
            _selIpt.selection(0).entity
        )

    def on_destroy(self, command: core.Command, inputs: core.CommandInputs, reason, input_values):
        pass

    def on_input_changed(self, command: core.Command, inputs: core.CommandInputs, changed_input, input_values):
        pass

    def on_execute(self, command: core.Command, inputs: core.CommandInputs, args, input_values):
        pass

    def on_create(self, command: core.Command, inputs: core.CommandInputs):
        command.isOKButtonVisible = False

        # event
        global _handlers
        onPreSelect = MyPreSelectHandler()
        command.preSelect.add(onPreSelect)
        _handlers.append(onPreSelect)

        # inputs
        global _infoIpt
        _infoIpt = inputs.addTextBoxCommandInput(
            '_infoIptId',
            '幾何拘束に関連するスケッチ要素をハイライトします',
            '',
            1,
            True,
        )

        global _selIpt
        _selIpt = inputs.addSelectionInput(
            '_selIptId',
            '幾何拘束を選択',
            '幾何拘束を選択してください',
        )
        _selIpt.isVisible = False

        # other
        global _fact
        _fact = HighlightingConstraintEntitiesFactry()


class MyPreSelectHandler(core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args: core.SelectionEventArgs):
        pass
        entity = args.selection.entity

        global _fact
        if not _fact.is_geometric_constraint(entity):
            args.isSelectable = False