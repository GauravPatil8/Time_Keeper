import bpy
import time
import functools
from tk_database_operations import DatabaseOperations

def update_enum_items():
    db_instance = DatabaseOperations()
    projects = db_instance.get_project_list()
    return [(proj[0], proj[0], "") for proj in projects]  # Format for EnumProperty

def update_project_list(self, context):
        projects = self.db_instance.get_project_list()
        context.scene.timer_props.selected_project = ""
        context.scene.timer_props.project_name = ""
        context.scene.timer_props.update(
            "selected_project", projects
        )
def redraw_interface():
    for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'UI':  
                        area.tag_redraw()

def draw_timer_header(self, context):
    layout = self.layout
    layout.separator() 
    layout.label(text=f"Time Spent: {context.scene.timer_props.elapsed_time}")

def get_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    _seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{_seconds:02}"

def convert_time_to_seconds(elapsed_time):
    hours, minutes, seconds = map(int, elapsed_time.split(':'))
    total_seconds = int(hours * 3600 + minutes * 60 + seconds)
    return total_seconds

def update_timer(start_time, time_spent):
    scene = bpy.data.scenes.get("Scene")
    
    if scene and start_time is not None:
        elapsed = time.time() - start_time + time_spent
        
        if (int(elapsed)%5 == 0):
           db_instance =  DatabaseOperations()
           
           db_instance.update_project_time(bpy.context.scene.timer_props.selected_project, elapsed)
          

        scene.timer_props.elapsed_time = get_time(elapsed)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'HEADER' or region.type == 'UI':  
                        area.tag_redraw()
        return 1.0  
    return None


class TimerProperties(bpy.types.PropertyGroup):
    db_instance: DatabaseOperations = DatabaseOperations()
    timer_reference = None
    def get_project_list(self, context):

        projects = self.db_instance.get_project_list()
        
        project_items = [('None', 'None', 'No project selected')] 
        project_items.extend([(proj[0], proj[0], "") for proj in projects])  
        return project_items

    def update_elapsed_time(self, context):
        """Update elapsed_time based on the selected project."""
        selected_project = self.selected_project
        
        if bpy.context.scene.timer_props.timer_running:
            context.scene.timer_props.timer_running = False
            bpy.app.timers.unregister(self.timer_reference)
        if selected_project and selected_project != 'None':
            time_in_seconds = self.db_instance.get_project_time(selected_project)
            self.elapsed_time = get_time(time_in_seconds)
            update_timer(time.time(), time_in_seconds)
        else:
            self.elapsed_time = "00:00:00"


    selected_project: bpy.props.EnumProperty(
        items=get_project_list, 
        name="Select Project", 
        update=update_elapsed_time,
        default=None  # Default value set to 'None'
    )

    elapsed_time: bpy.props.StringProperty(name="Elapsed Time", default='00:00:00')
    project_name: bpy.props.StringProperty(name="Project Name", default="")
    timer_running: bpy.props.BoolProperty(name="Timer Running", default=False)



class createProject(bpy.types.Operator):
    """Create a new project entry in the database."""
    bl_idname = "timer.create_project_modal"
    bl_label = ""
    bl_description = "Create a new project."

    project_name: bpy.props.StringProperty(name="Project Name")
    db_instance = None

    def execute(self, context):
        if self.project_name:
            self.db_instance = DatabaseOperations()
            if self.db_instance.check_project_name_availability(project_name= self.project_name):
                self.db_instance.create_project_entry(self.project_name)
                self.report({'INFO'}, f"Project '{self.project_name}' created successfully.")
                bpy.context.scene.timer_props.selected_project = self.project_name
                self.project_name = ""
            else:
                self.report({'WARNING'}, "Project with similar name already exists.")
        else:
            self.report({'WARNING'}, "Project name cannot be empty.")
        redraw_interface()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter Project Name:")
        layout.prop(self, "project_name", text="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class StartTimerOperator(bpy.types.Operator):
    """Start the timer for the selected project."""
    bl_idname = "timer.start"
    bl_label = ""
    bl_description = "Start tracking time for the selected project."

    db_instance = None

    def execute(self, context):
        context.scene.timer_props.timer_running = True

        self.db_instance = DatabaseOperations()

        start_time = time.time()

        time_spent = self.db_instance.get_project_time(bpy.context.scene.timer_props.selected_project)
        timer_function = functools.partial(update_timer, start_time, time_spent)
        StopTimerOperator.timer_reference = timer_function
        TimerProperties.timer_reference = timer_function

        bpy.app.timers.register(timer_function, first_interval=1.0)
        self.report({'INFO'}, "Timer started successfully.")
        return {'FINISHED'}

    def __del__(self):
        if self.db_instance:
            del self.db_instance


class StopTimerOperator(bpy.types.Operator):
    """Stop the timer and update the time in the database."""
    bl_idname = "timer.stop"
    bl_label = ""
    bl_description = "Stop tracking time and save the elapsed time for the selected project."

    db_instance = None
    timer_reference = None

    def execute(self, context):
        context.scene.timer_props.timer_running = False
        elapsed_time = context.scene.timer_props.elapsed_time  # Get the time spent from the timer
        selected_project = context.scene.timer_props.selected_project
        self.db_instance = DatabaseOperations()
        self.db_instance.update_project_time(selected_project, convert_time_to_seconds(elapsed_time))
        bpy.app.timers.unregister(self.timer_reference)
        self.report({'INFO'}, "Timer stopped successfully.")
        return {'FINISHED'}

    def __del__(self):
        if self.db_instance:
            del self.db_instance


class deleteProjectEntry(bpy.types.Operator):
    """Delete the selected project from the database."""
    bl_idname = "timer.delete"
    bl_label = ""
    bl_description = "Delete the currently selected project."

    db_instance = DatabaseOperations()
    delete: bpy.props.StringProperty(name="Type 'delete'", description="Type 'delete' to confirm the deletion")

    def execute(self, context):
        if self.delete.lower() == 'delete' and bpy.context.scene.timer_props.selected_project:
            self.db_instance.delete_project_entry(bpy.context.scene.timer_props.selected_project)
            self.report({'INFO'}, f"Project '{bpy.context.scene.timer_props.selected_project}' deleted successfully.")
            bpy.context.scene.timer_props.selected_project = 'None'
            self.delete = ''
        else:
            self.report({'ERROR'}, "Deletion failed. Please type 'delete' to confirm.")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Type 'delete' to Delete {bpy.context.scene.timer_props.selected_project}:")
        layout.prop(self, "delete", text="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
