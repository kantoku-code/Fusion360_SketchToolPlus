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
        adsk.fusion.SketchCircle.fromPoint = False

        pntLst = [p.worldGeometry for p in skt.sketchPoints if not p.isFullyConstrained]
        Cir3D = adsk.core.Circle3D
        zDir :adsk.core.Vector3D = skt.xDirection.crossProduct(skt.yDirection)
        pntLst = [Cir3D.createByCenter(p, zDir, 0.1) for p in pntLst]
        for c in pntLst:
            c.fromPoint = True

        # curve
        sktCrvs :adsk.fusion.SketchCurves = skt.sketchCurves
        crvLst = [c.worldGeometry for c in sktCrvs if not c.isFullyConstrained]

        # all
        lst = crvLst
        lst.extend(pntLst)

        # get Matrix
        matZero :adsk.core.Matrix3D = adsk.core.Matrix3D.create()
        mat = SketchAnalysisFactry.getOccMatrixFromSketch(skt)
        mat.invert()

        # transform
        if not mat.isEqualTo(matZero):
            tmp = lst
            lst = []
            for c in tmp:
                c.transformBy(mat)
                lst.append(c)

        return lst

    @staticmethod
    def getOccMatrixFromSketch(
        skt :adsk.fusion.Sketch
        ) -> adsk.core.Matrix3D:

        try:
            # occ
            occ :adsk.fusion.Occurrence = skt.assemblyContext
            des = adsk.fusion.Design.cast(occ.component.parentDesign)
            root = des.rootComponent

            mat = adsk.core.Matrix3D.create()
            occ_names = occ.fullPathName.split('+')
            occs = [root.allOccurrences.itemByName(name) 
                        for name in occ_names]
            mat3ds = [occ.transform for occ in occs]
            mat3ds.reverse() #important!!
            for mat3d in mat3ds:
                mat.transformBy(mat3d)

            return mat
        except:
            # root
            return adsk.core.Matrix3D.create()


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