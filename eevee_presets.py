import inspect
from pathlib import Path

import bpy
from bl_operators.presets import AddPresetBase
from bpy.props import StringProperty
from bpy.types import Menu, Operator, Panel
from mathutils import Color

PRESET_SUBDIR = "eevee_presets"
EXCLUDE_LIST = ["__", "bl_rna", "gi_cache_info", "rna_type"]
EEVEE_KEY_PREFIX = "eevee"
RENDER_KEY_PREFIX = "render"
PRESET_HEAD = """import bpy
eevee = bpy.context.scene.eevee
render = bpy.context.scene.render

"""


def get_eevee_values():
    pre_vals = {}
    eevee_settings_list = inspect.getmembers(bpy.context.scene.eevee)
    for elem in eevee_settings_list:
        key, value = elem
        if all(item not in key for item in EXCLUDE_LIST):
            if isinstance(value, Color):
                val = (value.r, value.g, value.b)
            elif isinstance(value, str):
                val = f"'{value}'"
            else:
                val = value
            pre_vals[f"{EEVEE_KEY_PREFIX}.{key}"] = val
    return pre_vals


def get_render_values():
    return {f"{RENDER_KEY_PREFIX}.film_transparent": bpy.context.scene.render.film_transparent}


class EEVEEPRESETS_MT_DisplayPresets(Menu):
    bl_label = "Eevee Presets"
    preset_subdir = PRESET_SUBDIR
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class EEVEEPRESETS_OT_AddPreset(AddPresetBase, Operator):
    bl_idname = "eeveepresets.preset_add_old"
    bl_label = "Add Eevee Preset OLD"
    preset_menu = "EEVEEPRESETS_MT_DisplayPresets"

    preset_defines = ["eevee = bpy.context.scene.eevee",
                      "render = bpy.context.scene.render"]

    preset_values = [
        # "render.film_transparent",
        # "eevee.bloom_clamp",
        # "eevee.bloom_color",
        # "eevee.bloom_intensity",
        # "eevee.bloom_knee",
        # "eevee.bloom_radius",
        # "eevee.bloom_threshold",
        # "eevee.bokeh_max_size",
        # "eevee.bokeh_threshold",
        # "eevee.gi_auto_bake",
        # # "eevee.gi_cache_info", # read only!
        # "eevee.gi_cubemap_display_size",
        # "eevee.gi_cubemap_resolution",
        # "eevee.gi_diffuse_bounces",
        # "eevee.gi_filter_quality",
        # "eevee.gi_glossy_clamp",
        # "eevee.gi_irradiance_display_size",
        # "eevee.gi_irradiance_smoothing",
        # "eevee.gi_show_cubemaps",
        # "eevee.gi_show_irradiance",
        # "eevee.gi_visibility_resolution",
        # "eevee.gtao_distance",
        # "eevee.gtao_factor",
        # "eevee.gtao_quality",
        # "eevee.light_threshold",
        # "eevee.motion_blur_samples",
        # "eevee.motion_blur_shutter",
        # "eevee.overscan_size",
        # "eevee.shadow_cascade_size",
        # "eevee.shadow_cube_size",
        # # "eevee.shadow_method", # removed
        # "eevee.ssr_border_fade",
        # "eevee.ssr_firefly_fac",
        # "eevee.ssr_max_roughness",
        # "eevee.ssr_quality",
        # "eevee.ssr_thickness",
        # "eevee.sss_jitter_threshold",
        # "eevee.sss_samples",
        # "eevee.taa_render_samples",
        # "eevee.taa_samples",
        # "eevee.use_bloom",
        # "eevee.use_gtao",
        # "eevee.use_gtao_bent_normals",
        # "eevee.use_gtao_bounce",
        # "eevee.use_motion_blur",
        # "eevee.use_overscan",
        # "eevee.use_shadow_high_bitdepth",
        # "eevee.use_soft_shadows",
        # "eevee.use_ssr",
        # "eevee.use_ssr_halfres",
        # "eevee.use_ssr_refraction",
        # # "eevee.use_sss_separate_albedo", # removed
        # "eevee.use_taa_reprojection",
        # "eevee.use_volumetric_lights",
        # "eevee.use_volumetric_shadows",
        # "eevee.volumetric_end",
        # "eevee.volumetric_light_clamp",
        # "eevee.volumetric_sample_distribution",
        # "eevee.volumetric_samples",
        # "eevee.volumetric_shadow_samples",
        # "eevee.volumetric_start",
        # "eevee.volumetric_tile_size"
    ]

    preset_subdir = PRESET_SUBDIR


class EEVEEPRESETS_OT_AddEeveePreset(bpy.types.Operator):
    bl_idname = "eeveepresets.add_eevee_preset"
    bl_label = "Add Eevee Preset"

    preset_name: StringProperty(name="Name",
                                description="",
                                default="")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")

    def execute(self, context):
        if self.preset_name == "":
            self.report({'INFO'}, "Preset needs a name!")
            return {'CANCELLED'}

        preset_path = Path(
            bpy.utils.resource_path('USER')) / Path(
                f"scripts/presets/{PRESET_SUBDIR}/{self.preset_name}.py")

        preset_lines = [PRESET_HEAD]

        # bpy.context.scene.render.film_transparent
        render_values = get_render_values()
        for key, value in render_values.items():
            line = f"{key} = {value}\n"
            preset_lines.append(line)

        eevee_values = get_eevee_values()
        for key, value in eevee_values.items():
            line = f"{key} = {value}\n"
            preset_lines.append(line)

        with open(preset_path, 'w') as preset_file:
            preset_file.writelines(preset_lines)

        return {'FINISHED'}


class EEVEEPRESETS_PT_panel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Eevee Presets"
    bl_category = "Eevee Presets"

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine == 'BLENDER_EEVEE':
            return True

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.menu(EEVEEPRESETS_MT_DisplayPresets.__name__,
                 text=EEVEEPRESETS_MT_DisplayPresets.bl_label)
        row.operator("eeveepresets.add_eevee_preset",
                     text="", icon='ADD')
        row.operator(EEVEEPRESETS_OT_AddPreset.bl_idname,
                     text="", icon='REMOVE').remove_active = True
