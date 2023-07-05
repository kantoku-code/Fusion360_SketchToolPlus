# Fusion360API Python

import adsk
import adsk.core as core
import adsk.fusion as fusion


class HighlightingEntitiesFactry:
    def __init__(self) -> None:
        self.cgFact = CustomGraphicsManager()

    def __del__(self) -> None:
        pass

    def is_geometric_constraint(
        self,
        entity
    ) -> bool:
        '''
        GeometricConstraintチェック
        '''

        return True if fusion.GeometricConstraint.cast(entity) else False

    def highlight_constraint_entities(
        self,
        constraint: fusion.GeometricConstraint
    ) -> list:
        '''
        拘束要素のハイライト
        '''

        entities = self._get_constraint_entities(constraint)
        if len(entities) < 1:
            return

        geometries = [sktEnt.worldGeometry for sktEnt in entities]

        self.cgFact.update(
            geometries,
            constraint.parentSketch.parentComponent,
        )

    def _get_constraint_entities(
        self,
        constraint: fusion.GeometricConstraint
    ) -> list:
        '''
        拘束要素の取得 - 対象外：一致,固定
        '''

        if not self.is_geometric_constraint(constraint):
            return

        sktEntities = []

        propNames = [
            'line',
            'curveOne',
            'curveTwo',
            'lineOne',
            'lineTwo',
            'entityOne',
            'entityTwo',
            'midPointCurve'
        ]

        for prop in propNames:
            if hasattr(constraint, prop):
                sktEntities.append(
                    getattr(constraint, prop)
                )

        return sktEntities


class CustomGraphicsManager():

    def __init__(
        self
    ) -> None:
        '''
        コンストラクタ
        '''

        self.app: core.Application = core.Application.get()
        self.des: fusion.Design = self.app.activeProduct

        self.cgGroup: fusion.CustomGraphicsGroup = None

        self.solidBlue = fusion.CustomGraphicsSolidColorEffect.create(
            core.Color.create(0, 0, 255, 255)
        )

        self.removeCG()

    def __del__(
        self
    ) -> None:
        '''
        デストラクタ
        '''

        self.removeCG()

    def removeCG(
        self
    ) -> None:
        '''
        カスタムグラフィックの削除
        '''

        cgs = [cmp.customGraphicsGroups for cmp in self.des.allComponents]
        cgs = [cg for cg in cgs if cg.count > 0]

        if len(cgs) < 1:
            return

        for cg in cgs:
            gps = [c for c in cg]
            gps.reverse()
            for gp in gps:
                gp.deleteMe()

    def update(
        self,
        curves: list,
        comp: fusion.Component,
    ) -> None:
        '''
        ボディの表示アップデート
        '''

        self.removeCG()
        self.cgGroup = comp.customGraphicsGroups.add()
        self.cgGroup.depthPriority = 1

        for crv in curves:
            crvCg = self.cgGroup.addCurve(crv)
            crvCg.color = self.solidBlue
            crvCg.weight = 3

        self.app.activeViewport.refresh()
