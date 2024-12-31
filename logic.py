import bpy
import time
from datetime import datetime

def update_timer():
    global start_time
    scene = bpy.data.scenes.get("Scene") 
    if scene and start_time is not None:
        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        scene.timer_props.elapsed_time = f"{hours:02}:{minutes:02}:{seconds:02}"


        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'UI':
                        area.tag_redraw()

        return 1.0  # Update every second
    return None

class TimerProperties(bpy.types.PropertyGroup):
    elapsed_time: bpy.props.StringProperty(name="Elapsed Time", default="00:00:00.000")

class StartTimerOperator(bpy.types.Operator):
    bl_idname = "timer.start"
    bl_label = "Start Timer"

    def execute(self, context):
        global start_time
        start_time = time.time()
        bpy.app.timers.register(update_timer, first_interval=1.0)
        return {'FINISHED'}

class StopTimerOperator(bpy.types.Operator):
    bl_idname = "timer.stop"
    bl_label = "Stop Timer"

    def execute(self, context):
        global start_time
        start_time = None
        bpy.app.timers.unregister(update_timer)
        return {'FINISHED'}