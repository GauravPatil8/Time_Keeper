import bpy
import sys
import os

script_path = os.path.abspath(__file__)
package_path = os.path.dirname(script_path)
sys.path.append(package_path)


from logic import *
from ui import *

def register():
    global start_time
    start_time = None
    bpy.utils.register_class(TimerProperties)
    bpy.types.Scene.timer_props = bpy.props.PointerProperty(type=TimerProperties)
    bpy.utils.register_class(StartTimerOperator)
    bpy.utils.register_class(StopTimerOperator)
    bpy.utils.register_class(TimerPanel)

def unregister():
    global start_time
    start_time = None
    bpy.utils.unregister_class(TimerProperties)
    del bpy.types.Scene.timer_props
    bpy.utils.unregister_class(StartTimerOperator)
    bpy.utils.unregister_class(StopTimerOperator)
    bpy.utils.unregister_class(TimerPanel)

register()