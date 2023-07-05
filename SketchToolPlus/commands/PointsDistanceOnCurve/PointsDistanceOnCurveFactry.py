# FusionAPI_python
# Author-kantoku

import traceback
import adsk.core as core
import adsk.fusion as fusion
from typing import Tuple

_debug = False


class PointsDistanceOnCurveFactry():
    _tolerance = 0.001

    @staticmethod
    def getDividerPoint3D(
        crv: fusion.SketchEntity,
        count: int
    ) -> list:

        # check sketch
        if not PointsDistanceOnCurveFactry.isSketchMatch(crv):
            return []

        # get Evaluator
        eva: core.CurveEvaluator3D = crv.geometry.evaluator

        # get start parameter
        sPrm, ePrm = PointsDistanceOnCurveFactry.getStartEndPrm(crv)

        # get step
        step = crv.length / (count + 1)

        # get parameter
        prms = []
        for idx in range(1, count+1):
            _, prm = eva.getParameterAtLength(sPrm, step * idx)
            prms.append(prm)

        if PointsDistanceOnCurveFactry.isClose(crv):
            # _, prm = eva.getParameterAtLength(sPrm, ePrm)
            # prms.append(prm)
            prms.append(ePrm)

        # get point3d
        _, pnts = eva.getPointsAtParameters(prms)

        return [p for p in pnts]

    @staticmethod
    def createDivider(
        crv: fusion.SketchEntity,
        count: int
    ):

        # get Divider points
        pnts = PointsDistanceOnCurveFactry.getDividerPoint3D(crv, count)

        if len(pnts) < 1:
            return

        # get target sketch
        skt: fusion.Sketch = crv.parentSketch
        skt.isComputeDeferred = True

        # init sktPoint
        sktPnts = skt.sketchPoints
        pntLst = [sktPnts.add(p) for p in pnts]

        # init Coincident
        [skt.geometricConstraints.addCoincident(p, crv) for p in pntLst]

        skt.isComputeDeferred = False

    @staticmethod
    def getPreviewPoints(
        crv: fusion.SketchEntity,
        count: int
    ) -> list:

        def transformPnt(
            pnt: core.Point3D,
            mat: core.Matrix3D
        ):

            clone: core.Point3D = pnt.copy()
            clone.transformBy(mat)
            return clone

        def getOccMat(
            skt: fusion.Sketch
        ) -> core.Matrix3D:

            try:
                # occ
                occ: fusion.Occurrence = skt.assemblyContext
                return occ.transform
            except:
                # root
                return core.Matrix3D.create()

        # get Divider points
        pnts = PointsDistanceOnCurveFactry.getDividerPoint3D(crv, count)

        # get skt
        skt: fusion.Sketch = crv.parentSketch

        # get Sketch matrix3d
        sktMat: core.Matrix3D = skt.transform

        # get Root or Occurrence matrix3d
        occMat: core.Matrix3D = getOccMat(skt)

        if occMat.isEqualTo(sktMat):
            return pnts

        mat = sktMat.copy()
        occMat.invert()
        mat.transformBy(occMat)

        pntLst = [transformPnt(p, mat) for p in pnts]

        return pntLst

    @staticmethod
    def isSketchMatch(
        crv: fusion.SketchEntity
    ) -> bool:

        # check active sketch
        app = core.Application.get()
        des: fusion.Design = app.activeProduct
        skt: fusion.Sketch = fusion.Sketch.cast(des.activeEditObject)
        if not skt:
            return False

        # get parentSketch
        crvSkt: fusion.Sketch = crv.parentSketch

        # include
        if skt != crvSkt:
            return False

        return True

    @staticmethod
    def getStartEndPrm(
        crv: fusion.SketchEntity
    ) -> Tuple[float, float]:

        eva: core.CurveEvaluator3D = crv.geometry.evaluator
        # eva :core.CurveEvaluator3D = crv.worldGeometry.evaluator

        objType = crv.objectType.split('::')[-1]
        if objType in ('SketchCircle', 'SketchEllipse'):
            _, sPrm, ePrm = eva.getParameterExtents()
        else:
            # get start end point
            _, startPnt, endPnt = eva.getEndPoints()

            # get start parameter
            _, sPrm = eva.getParameterAtPoint(startPnt)
            _, ePrm = eva.getParameterAtPoint(endPnt)

        if _debug:
            _, startPnt, endPnt = eva.getEndPoints()
            _, sPrmEnd = eva.getParameterAtPoint(startPnt)
            _, ePrmEnd = eva.getParameterAtPoint(endPnt)
            dumpMsg(f'sPrmEnd {sPrmEnd} : ePrmEnd {ePrmEnd}')
            _, sPrmEx, ePrmEx = eva.getParameterExtents()
            dumpMsg(f'sPrmEx {sPrmEx} : ePrmEx {ePrmEx}')

        return sPrm, ePrm

    @staticmethod
    def isClose(
        crv: fusion.SketchEntity
    ) -> bool:

        # SketchFittedSpline
        if hasattr(crv, 'isClosed'):
            return crv.isClosed

        # other
        sPrm, ePrm = PointsDistanceOnCurveFactry.getStartEndPrm(crv)
        eva: core.CurveEvaluator3D = crv.geometry.evaluator

        _, pnts = eva.getPointsAtParameters([sPrm, ePrm])
        if pnts[0].distanceTo(pnts[1]) < PointsDistanceOnCurveFactry._tolerance:
            return True

        return False

    @staticmethod
    def isCurveOnPoint(
        crv: fusion.SketchEntity,
        pnt: fusion.SketchPoint
    ) -> bool:

        # get Evaluator
        eva: core.CurveEvaluator3D = crv.geometry.evaluator

        # get parameter
        geo: core.Point3D = pnt.geometry
        _, prm = eva.getParameterAtPoint(geo)

        # get prmAtPoint
        _, revPnt = eva.getPointAtParameter(prm)

        if revPnt.distanceTo(geo) < PointsDistanceOnCurveFactry._tolerance:
            return True

        return False

    # return unit Cm!
    @staticmethod
    def getPoint2PointLengthOnCurve(
        crv: fusion.SketchEntity,
        pnt1: fusion.SketchPoint,
        pnt2: fusion.SketchPoint
    ) -> tuple:

        # get Evaluator
        eva: core.CurveEvaluator3D = crv.geometry.evaluator

        # # get parameter
        prms = PointsDistanceOnCurveFactry.getPrmAtSktPoints(crv, [pnt1, pnt2])

        if PointsDistanceOnCurveFactry.isClose(crv):
            # close
            sPrm, ePrm = PointsDistanceOnCurveFactry.getStartEndPrm(crv)
            midPrm = (prms[0] + prms[1]) * 0.5
            prmLst = [
                [(prms[0], midPrm), (midPrm, prms[1])]
            ]
            if abs(prms[0] - sPrm) > 0.001:
                # 始点と1点目が不一致
                prmLst.append([(sPrm, prms[0]), (prms[1], ePrm)])
            else:
                # 始点と1点目が一致
                prmLst.append([(prms[1], ePrm)])
        else:
            # open
            prmLst = [
                [(prms[0], prms[1])]
            ]

        # get min
        lengthLst = []
        try:
            for prmSet in prmLst:
                sumLength = 0

                if _debug:
                    dumpMsg('--')

                for ps in prmSet:
                    if abs(ps[0] - ps[1]) < 0.001:
                        continue

                    _, length = eva.getLengthAtParameter(ps[0], ps[1])
                    sumLength += abs(length)

                    if _debug:
                        dumpMsg(
                            f'prm[{ps[0]},{ps[1]}] - {length} - {sumLength}')

                lengthLst.append(sumLength)

        except:
            dumpMsg('Failed:\n{}'.format(traceback.format_exc()))

        if _debug:
            xx = list(zip(lengthLst, prmLst))
            pass

        res = min(zip(lengthLst, prmLst), key=(lambda x: x[0]))

        return res

    @staticmethod
    def getPrmAtSktPoints(
        crv: fusion.SketchEntity,
        pnts: list
    ) -> list:

        # get Evaluator
        eva: core.CurveEvaluator3D = crv.geometry.evaluator

        geos = [p.geometry for p in pnts]

        # get parameter
        _, prms = eva.getParametersAtPoints(geos)

        # sort
        tmp = list(prms)
        tmp.sort()
        prms = tmp

        return prms


# --debug --
def dumpMsg(msg: str):
    core.Application.get().userInterface.palettes.itemById(
        'TextCommands').writeText(str(msg))
