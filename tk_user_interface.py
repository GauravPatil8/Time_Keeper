import bpy
from db_logic import DatabaseOperations

class TimerPanel(bpy.types.Panel):
    bl_label = "Time Keeper"
    bl_idname = "VIEW3D_PT_timer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Timer'

    db_instance = None

    def draw(self, context):
        timer_props = context.scene.timer_props
        layout = self.layout

        self.db_instance = DatabaseOperations()

        project_list = self.db_instance.get_project_list()

        if not project_list:
            layout.operator("timer.create_project_modal", text="create project", icon="ADD")
        else:
            project_row = layout.row()
            project_row.prop(context.scene.timer_props, "selected_project", text="Select Project")
            project_row.operator("timer.create_project_modal", icon="ADD")

            
            col = layout.column()
            box = col.box()
            row_box = box.row()
            row_box.label(text=f"Time Spent: {context.scene.timer_props.elapsed_time}")
            if timer_props.timer_running:
                row_box.operator("timer.stop", text="", icon="PAUSE")
            else:
                row_box.operator("timer.start", text="", icon="PLAY")

    def __del__(self):
        if self.db_instance:
            del self.db_instance