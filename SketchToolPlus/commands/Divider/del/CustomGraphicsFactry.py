# FusionAPI_python 
# Author-kantoku

import adsk.core, adsk.fusion, traceback

class CustomGraphicsFactry():

    _app = adsk.core.Application.cast(None)
    _cgGroup = adsk.fusion.CustomGraphicsGroup.cast(None)
    _iconPath = ''

    red = adsk.core.Color.create(255,0,0,255)
    _solidRed = adsk.fusion.CustomGraphicsSolidColorEffect.create(red)
    # blue = adsk.core.Color.create(0,0,255,255)
    # _solidBlue = adsk.fusion.CustomGraphicsSolidColorEffect.create(blue)

    _id =''

    def __init__(
        self,
        id :str,
        iconPath :str,
        ):

        self._app = adsk.core.Application.get()
        self._iconPath = iconPath
        # self.refreshCG()

    def __del__(
        self
        ):

        self.removeCG()

    def removeCG(
        self
        ):

        des :adsk.fusion.Design = self._app.activeProduct
        cgs = [cmp.customGraphicsGroups for cmp in des.allComponents]
        cgs = [cg for cg in cgs if cg.count > 0]
        
        if len(cgs) < 1: return

        for cg in cgs:
            gps = [c for c in cg]
            gps.reverse()
            for gp in gps:
                if gp.id != self._id:
                    continue

                gp.deleteMe()

    def refreshCG(
        self
        ):

        self.removeCG()
        des :adsk.fusion.Design = self._app.activeProduct
        comp :adsk.fusion.Component = des.activeComponent
        self._cgGroup = comp.customGraphicsGroups.add()

    def updatePoints(
        self, 
        pnts :list,
        isRefresh :bool = True
        ):

        if isRefresh:
            self.refreshCG()

        cGCoords = adsk.fusion.CustomGraphicsCoordinates
        coords = [cGCoords.create(p.asArray()) for p in pnts]

        pType = adsk.fusion.CustomGraphicsPointTypes.UserDefinedCustomGraphicsPointType

        for coord in coords:
            self._cgGroup.addPointSet(coord, [], pType, self._iconPath)

    # 基本未使用
    def updateCurves(
        self,
        crvs :list,
        isRefresh :bool = True
        ):

        if isRefresh:
            self.refreshCG()
        
        for crv in crvs:
            crvCg = self._cgGroup.addCurve(crv)
            crvCg.color = self._solidRed
            crvCg.weight = 5