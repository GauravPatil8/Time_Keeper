import bpy
import time
import functools
from db_logic import DatabaseOperations

def update_enum_items():
    # Fetch project list from the database
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
    # db_instance = DatabaseOperations()
    # initiation_time = db_instance.get_project_initiation_time(bpy.context.scene.timer_props.selected_project)
    # time_spent = db_instance.get_project_time_spent(bpy.context.scene.timer_props.selected_project)
    if scene and start_time is not None:
        elapsed = time.time() - start_time + time_spent

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

    def get_project_list(self, context):
        # Fetch project names from the database and format them for EnumProperty
        projects = self.db_instance.get_project_list()
        
        # Add a 'None' option to represent no project selected
        project_items = [('None', 'None', 'No project selected')]  # Default 'None' option
        project_items.extend([(proj[0], proj[0], "") for proj in projects])  # Add actual projects
        return project_items

    def update_elapsed_time(self, context):
        """Update elapsed_time based on the selected project."""
        selected_project = self.selected_project
        if selected_project and selected_project != 'None':  # Ensure it's not 'None'
            time_in_seconds = self.db_instance.get_project_time(selected_project)
            print(f"--------------------seconds:{time_in_seconds}--------------------")
            self.elapsed_time = get_time(time_in_seconds)
            print(f"-----------------elapsed time: {self.elapsed_time}---------------")
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
    bl_label = ""
    bl_idname = "timer.create_project_modal"

    project_name: bpy.props.StringProperty(name="Project Name")
    db_instance = None

    def execute(self,context):
        if self.project_name:
            self.db_instance = DatabaseOperations()
            self.db_instance.create_project_entry(self.project_name)
        redraw_interface()
        return {'FINISHED'}

    def draw(self,context):
        layout = self.layout
        layout.label(text="Enter Project Name:")
        layout.prop(self, "project_name", text="")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def __del__(self):
        if self.db_instance:
            del self.db_instance
class StartTimerOperator(bpy.types.Operator):
    bl_idname = "timer.start"
    bl_label = ""

    db_instance = None

    def execute(self, context):

        context.scene.timer_props.timer_running = True

        self.db_instance = DatabaseOperations()

        start_time = time.time()
        
        time_spent = self.db_instance.get_project_time(bpy.context.scene.timer_props.selected_project)
        timer_function = functools.partial(update_timer, start_time, time_spent)
        StopTimerOperator.timer_reference = timer_function

        bpy.app.timers.register(timer_function, first_interval=1.0)
        return {'FINISHED'}
    
    def __del__(self):
        if self.db_instance:
            del self.db_instance
            

class StopTimerOperator(bpy.types.Operator):
    bl_idname = "timer.stop"
    bl_label = ""

    db_instance = None
    timer_reference = None
    def execute(self, context):
        context.scene.timer_props.timer_running = False
        elapsed_time = context.scene.timer_props.elapsed_time  # Get the time spent from the timer
        selected_project = context.scene.timer_props.selected_project
        self.db_instance = DatabaseOperations()
        self.db_instance.update_project_time(selected_project, convert_time_to_seconds(elapsed_time))
        bpy.app.timers.unregister(self.timer_reference)
        return {'FINISHED'}
    
    def __del__(self):
        if self.db_instance:
            del self.db_instance

class resetTimerOperator(bpy.types.Operator):
    bl_idname = "time.reset"
    bl_label = "reset Timer"

    db_instance = None

    def execute(self, context):
        self.db_instance = DatabaseOperations()
        self.db_instance.reset_project_time(context.scene.timer_props.elapsed_time)