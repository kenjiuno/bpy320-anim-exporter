# Blender exporter plugins, runs great on Blender 3.2.2 with Python 3.10.2 x64

from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper
import bpy
import json

from . import export_model

bl_info = {
    "name": "JSON: animation data used by OpenKh.Command.AnbMaker",
    "author": "kenjiuno",
    "version": (0, 3, 0),
    "blender": (3, 2, 0),
    "location": "File > Export > MMD Tools Panel",
    "description": "Animation JSON exporter plugin for OpenKh.Command.AnbMaker.",
    "warning": "This is an experimental module",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/kenjiuno/bpy320-anim-exporter",
    "tracker_url": "https://github.com/kenjiuno/bpy320-anim-exporter/issues",
    "category": "Import-Export"
}

if "bpy" in locals():
    import imp
    if "export_model" in locals():
        imp.reload(export_model)


# See: https://blender.stackexchange.com/a/110112
def ShowMessageBox(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def write_some_data(context, filepath, use_some_setting):
    f = open(filepath, 'w', encoding='utf-8')
    f.write(
        json.dumps(
            export_model.AnimExporter().export(),
            indent=1
        )
    )
    f.close()

    ShowMessageBox("Exporter finished!", "Exporter result")

    return {'FINISHED'}


class ExportSomeData(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "anim_exporter.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Some Data"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        return write_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname,
                         text=bl_info["name"])


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
