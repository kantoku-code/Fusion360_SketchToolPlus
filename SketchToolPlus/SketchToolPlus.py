
#FusionAPI_python Addin
#Author-kantoku
#Description-

#using Fusion360AddinSkeleton
#https://github.com/tapnair/Fusion360AddinSkeleton
#Special thanks:Patrick Rainsberry

from .DividerCore import DividerCore
from .PointsDistanceOnCurveCore import PointsDistanceOnCurveCore

commands = []
command_definitions = []

# Set to True to display various useful messages when debugging your app
debug = False

def run(context):

    cmd = {
        'cmd_name': 'ディバイダ',
        'cmd_description': '指定したスケッチ線に等間隔の点を作成します',
        'cmd_id': 'divider',
        'cmd_resources': 'resources/Divider',
        'workspace': 'FusionSolidEnvironment',
        'toolbar_panel_id': 'SketchPanel',
        'class': DividerCore
    }

    command_definitions.append(cmd)

    cmd = {
        'cmd_name': '2点間の線上距離',
        'cmd_description': '指定した2点間の線上の距離を測定します',
        'cmd_id': 'pointsDistanceOnCurve',
        'cmd_resources': 'resources/PointsDistanceOnCurve',
        'workspace': 'FusionSolidEnvironment',
        'toolbar_panel_id': 'InspectPanel',
        'class': PointsDistanceOnCurveCore
    }

    command_definitions.append(cmd)



    # Don't change anything below here:
    for cmd_def in command_definitions:
        command = cmd_def['class'](cmd_def, debug)
        commands.append(command)

        for run_command in commands:
            run_command.on_run()

def stop(context):
    for stop_command in commands:
        stop_command.on_stop()