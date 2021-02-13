#Author-kantoku
#Description-拘束不足の要素を強調して表示させます。
#Fusion360API Python

import adsk.core
import adsk.fusion

class SketchAnalysisFactry:

    @staticmethod
    def findLackConstraints(
        skt :adsk.fusion.Sketch
        ) -> list:

        # point
        pntLst = [p.geometry for p in skt.sketchPoints if not p.isFullyConstrained]
        Cir3D = adsk.core.Circle3D
        zDir :adsk.core.Vector3D = skt.xDirection.crossProduct(skt.yDirection)
        pntLst = [Cir3D.createByCenter(p, zDir, 0.1) for p in pntLst]

        # curve
        sktCrvs :adsk.fusion.SketchCurves = skt.sketchCurves
        crvLst = [c.geometry for c in sktCrvs if not c.isFullyConstrained]

        lst = crvLst
        lst.extend(pntLst)

        return lst


class CustomGraphicsFactry:

    def __init__(self, id :str, rgb :list):
        self.app :adsk.core.Application = adsk.core.Application.get()
        self.id = id
        self.cgGroup :adsk.fusion.CustomGraphicsGroup = None

        color = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
        self.solidcolor = adsk.fusion.CustomGraphicsSolidColorEffect.create(color)


    def __del__(self):
        self.removeCG()

    def removeCG(self):
        des :adsk.fusion.Design = self.app.activeProduct
        cgs = [cmp.customGraphicsGroups for cmp in des.allComponents]
        cgs = [cg for cg in cgs if cg.count > 0]
        
        if len(cgs) < 1: return

        for cg in cgs:
            gps = [c for c in cg]
            gps.reverse()
            for gp in gps:
                if gp.id != self.id: continue
                gp.deleteMe()

    def refreshCG(self):
        self.removeCG()
        des :adsk.fusion.Design = self.app.activeProduct
        comp :adsk.fusion.Component = des.activeComponent
        self.cgGroup = comp.customGraphicsGroups.add()
        self.cgGroup.id = self.id

    def updateCurves(self, crvs :list, isRefresh :bool = True):
        if isRefresh:
            self.refreshCG()
        
        for crv in crvs:
            crvCg = self.cgGroup.addCurve(crv)
            crvCg.color = self.solidcolor
            crvCg.weight = 5
        
        self.app.activeViewport.refresh()