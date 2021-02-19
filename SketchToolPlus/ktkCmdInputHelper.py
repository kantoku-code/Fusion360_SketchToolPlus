#Author-kantoku
#Description-Support class for Command Inputs
#Fusion360API Python

import traceback

import adsk.core
import adsk.fusion

import dataclasses
# https://qiita.com/tag1216/items/13b032348c893667862a
# https://www.mathpython.com/ja/dataclass/


# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-568db63a-0f28-4307-9e02-e29f54820db1
@dataclasses.dataclass
class SelectionCommandInputHelper:
    id : str
    name : str
    commandPrompt : str
    filter : list

    obj : adsk.core.SelectionCommandInput = dataclasses.field(default=None)

    def register(self, targetInputs :adsk.core.CommandInputs):
        self.obj = targetInputs.addSelectionInput(
            self.id,
            self.name,
            self.commandPrompt)
        [self.obj.addSelectionFilter(s) for s in self.filter]


# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-a10df443-c843-4733-9111-6332f9410db2
@dataclasses.dataclass
class TextBoxCommandInputHelper:
    id : str
    name : str
    text : str
    numRows : int
    isReadOnly : bool

    obj : adsk.core.TextBoxCommandInput = dataclasses.field(default=None)

    def register(self, targetInputs :adsk.core.CommandInputs):
        self.obj = targetInputs.addTextBoxCommandInput(
            self.id,
            self.name,
            self.text,
            self.numRows,
            self.isReadOnly)


# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-12aa42ec-0171-42a1-9b12-83ddacc5eb44
@dataclasses.dataclass
class IntegerSpinnerCommandInputHelper:
    id : str
    name : str
    min : int
    max : int
    spinStep : int
    initialValue : int

    obj : adsk.core.IntegerSpinnerCommandInput = dataclasses.field(default=None)

    def register(self, targetInputs :adsk.core.CommandInputs):
        self.obj = targetInputs.addIntegerSpinnerCommandInput(
            self.id,
            self.name,
            self.min,
            self.max,
            self.spinStep,
            self.initialValue)

    def isRange(self) -> bool:
        state = self.obj.value
        minimum = self.obj.minimumValue
        maximum = self.obj.maximumValue

        if minimum <= state <= maximum:
            return True
        else:
            return False

    def isOdd(self) -> bool:
        return True if self.obj.value % 2 != 0 else False


# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-671f0782-efe0-4e33-a744-afa3d5619a01
@dataclasses.dataclass
class ValueCommandInputHelper:
    id : str
    name : str

    unitType : str = ''
    initialValue : adsk.core.ValueInput = dataclasses.field(default=None)

    obj : adsk.core.ValueCommandInput = dataclasses.field(default=None)

    def register(self, targetInputs :adsk.core.CommandInputs):
        app :adsk.core.Application = adsk.core.Application.get()
        des :adsk.fusion.Design = app.activeProduct
        unitMgr :adsk.fusion.FusionUnitsManager = des.unitsManager

        self.unitType : str = unitMgr.defaultLengthUnits
        self.initialValue : adsk.core.ValueInput = adsk.core.ValueInput.createByString(
            f'1{unitMgr.defaultLengthUnits}')

        self.obj = targetInputs.addValueInput(
            self.id,
            self.name,
            self.unitType,
            self.initialValue)


# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-C3F746B3-6488-4B74-A441-31AFDEFD1648
@dataclasses.dataclass
class TableCommandInputHelper:
    id : str
    name : str
    columnRatio : str

    lstCount : int = 0
    ipts : adsk.core.CommandInputs = dataclasses.field(default=None)
    obj : adsk.core.TableCommandInput = dataclasses.field(default=None)

    def register(self, targetInputs :adsk.core.CommandInputs):
        self.obj = targetInputs.addTableCommandInput(
            self.id,
            self.name,
            0,
            self.columnRatio)
        self.ipts = targetInputs
    
    def add(self, txt :str):
        row = self.obj.rowCount
        txtObj = self.ipts.addStringValueInput(
            self.id + f'txt_{row}','txt',txt)
        txtObj.isReadOnly = True
        self.obj.addCommandInput(txtObj, row, 0)