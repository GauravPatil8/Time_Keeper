# Copyright (c) 2025 Gaurav 
bl_info = {
    "name": "Time Keeper",
    "author": "Gaurav",
    "version": (0, 1, 0),
    "blender": (4, 3, 2),
    "location": "View3D > Sidebar > Timer",
    "description": "Track and manage time spent on projects in Blender.",
    "tracker_url": "https://github.com/GauravPatil8/Time_Keeper/issues",
    "category": "System"
}

import bpy
import sys
import os

script_path = os.path.abspath(__file__)
package_path = os.path.dirname(script_path)
sys.path.append(package_path)

from tk_operations import *
from tk_user_interface import *

def register():
    bpy.utils.register_class(TimerProperties)
    bpy.types.Scene.timer_props = bpy.props.PointerProperty(type=TimerProperties)
    bpy.types.VIEW3D_HT_header.append(draw_timer_header)
    bpy.utils.register_class(StopTimerOperator)
    bpy.utils.register_class(StartTimerOperator)
    bpy.utils.register_class(createProject)
    bpy.utils.register_class(deleteProjectEntry)
    bpy.utils.register_class(TimerPanel)

def unregister():
    global start_time
    start_time = None
    bpy.utils.unregister_class(TimerProperties)
    del bpy.types.Scene.timer_props
    bpy.utils.unregister_class(StartTimerOperator)
    bpy.utils.unregister_class(StopTimerOperator)
    bpy.utils.unregister_class(createProject)
    bpy.utils.unregister_class(deleteProjectEntry)
    bpy.utils.unregister_class(TimerPanel)
    bpy.types.VIEW3D_HT_header.remove(draw_timer_header)

