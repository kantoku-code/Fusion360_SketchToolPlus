# Fusion360API Python

import adsk.core as core
import adsk.fusion as fusion
import itertools


class SketchPlaneFactry():
    def __init__(self) -> None:
        self.app: core.Application = core.Application.get()
        self.des: fusion.Design = self.app.activeProduct
        self.root: fusion.Component = self.des.rootComponent
        self.color: fusion.CustomGraphicsSolidColorEffect = fusion.CustomGraphicsSolidColorEffect.create(
            core.Color.create(255, 0, 0, 255)
        )

    def exec_preview(self, skt: fusion.Sketch) -> None:
        if self.des.designType == fusion.DesignTypes.DirectDesignType:
            return

        refPlane = self.get_ref_plane(skt)
        if not refPlane:
            return None

        if refPlane.objectType == fusion.BRepFace.classType():
            self._preview_brepface(refPlane)
        elif refPlane.objectType == fusion.ConstructionPlane.classType():
            self._preview_constructionPlane(refPlane)
        else:
            return None

    def get_ref_plane(self, skt: fusion.Sketch) -> core.Base:
        try:
            return skt.referencePlane
        except:
            return None

    def _preview_brepface(self, face: fusion.BRepFace) -> None:

        tmpMgr: fusion.TemporaryBRepManager = fusion.TemporaryBRepManager.get()
        faceBody: fusion.BRepBody = tmpMgr.copy(face)

        cgGroup: fusion.CustomGraphicsGroup = self.root.customGraphicsGroups.add()
        cgGroup.depthPriority = 1
        cgBody = cgGroup.addBRepBody(faceBody)

        cgBody.color = self.color

    def _preview_constructionPlane(self, constPlane: fusion.ConstructionPlane) -> None:

        def get_plane_points(
            plane: fusion.ConstructionPlane,
        ) -> list[core.Point3D]:

            geo: core.Plane = plane.geometry

            uVec: core.Vector3D = geo.uDirection
            uVec.normalize()

            vVec: core.Vector3D = geo.vDirection
            vVec.normalize()

            bBox: core.BoundingBox2D = plane.displayBounds
            xLst = [
                bBox.maxPoint.x,
                bBox.minPoint.x,
                bBox.minPoint.x,
                bBox.maxPoint.x,
            ]
            yLst = [
                bBox.maxPoint.y,
                bBox.maxPoint.y,
                bBox.minPoint.y,
                bBox.minPoint.y,
            ]

            vecLst = [uVec.copy() for _ in range(4)]
            [v.scaleBy(x) for v, x in zip(vecLst, xLst)]

            vVecLst = [vVec.copy() for _ in range(4)]
            [v.scaleBy(y) for v, y in zip(vVecLst, yLst)]

            [u.add(v) for u, v in zip(vecLst, vVecLst)]

            points = [geo.origin.copy() for _ in range(4)]

            [p.translateBy(v) for p, v in zip(points, vecLst)]

            return points
        # ************

        points = get_plane_points(constPlane)

        coordArray = list(
            itertools.chain.from_iterable(
                [p.asArray() for p in points]
            )
        )
        coords = fusion.CustomGraphicsCoordinates.create(coordArray)

        vertexIndices = [0, 1, 2, 0, 2, 3]

        normal = constPlane.geometry.normal.asArray()
        normalIndices = [0, 0, 0, 0, 0, 0]

        cgGroup: fusion.CustomGraphicsGroup = self.root.customGraphicsGroups.add()
        cgGroup.depthPriority = 1
        meshPlane = cgGroup.addMesh(
            coords, vertexIndices, normal, normalIndices)

        meshPlane.color = self.color
