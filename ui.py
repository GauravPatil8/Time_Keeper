import bpy

class TimerPanel(bpy.types.Panel):
    bl_label = "Real-Time Timer"
    bl_idname = "VIEW3D_PT_timer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Timer'

    def draw(self, context):
        layout = self.layout
        layout.operator("timer.start", text="Start Timer")
        layout.operator("timer.stop", text="Stop Timer")

        # Add a visually distinct large elapsed time display centered in the box
        row = layout.row()
        row.scale_y = 2.0  # Increase the height of the row
        box = row.box()
        col = box.column()
        col.alignment = 'CENTER'
        col.label(text=context.scene.timer_props.elapsed_time, icon='TIME')