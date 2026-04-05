import os
import shutil
import sys
import traceback
from datetime import datetime

import addon_utils
import bpy


MODULE_NAME = "blender2pmxemn"
SCRIPT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SAMPLE_DIR = os.path.join(REPO_ROOT, "sample")
FOR_LOCAL_DIR = os.path.join(REPO_ROOT, "forLocal")


def log(message):
    print(message)
    sys.stdout.flush()


def describe_context(label, armature=None, bone_name=None):
    selected_pose_bones = getattr(bpy.context, "selected_pose_bones", None)
    active_pose_bone = getattr(bpy.context, "active_pose_bone", None)
    selected_names = []
    if selected_pose_bones:
        selected_names = [bone.name for bone in selected_pose_bones]

    pose_lock = None
    if armature is not None and bone_name is not None and bone_name in armature.pose.bones:
        pose_lock = list(armature.pose.bones[bone_name].lock_rotation)

    info = {
        "mode": bpy.context.mode,
        "active_object": getattr(bpy.context.active_object, "name", None),
        "object": getattr(bpy.context.object, "name", None),
        "active_pose_bone": getattr(active_pose_bone, "name", None),
        "selected_pose_bones": selected_names,
        "pose_lock": pose_lock,
    }
    log(f"[STATE] {label}: {info}")


def ensure_module_loaded():
    if MODULE_NAME in sys.modules:
        addon_utils.disable(MODULE_NAME, default_set=False)
        del sys.modules[MODULE_NAME]

    addon_utils.modules_refresh()
    try:
        bpy.ops.preferences.addon_enable(module=MODULE_NAME)
    except RuntimeError:
        addon_utils.enable(MODULE_NAME, default_set=False, persistent=False)


def make_work_dir():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = os.path.join(FOR_LOCAL_DIR, f"tmp_pose_view3d_{timestamp}")
    os.makedirs(work_dir, exist_ok=True)
    return work_dir


def find_view3d_override():
    window = bpy.context.window
    screen = window.screen if window else None
    if not screen:
        return None

    for area in screen.areas:
        if area.type != "VIEW_3D":
            continue
        for region in area.regions:
            if region.type == "WINDOW":
                return {
                    "window": window,
                    "screen": screen,
                    "area": area,
                    "region": region,
                }
    return None


def first_pose_bone_object():
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and obj.pose and obj.pose.bones:
            return obj
    return None


def prepare_pose_mode(armature):
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="POSE")
    bpy.context.view_layer.update()


def reset_bone_selection(armature):
    for bone in armature.data.bones:
        for attr in ("select", "select_head", "select_tail"):
            if hasattr(bone, attr):
                setattr(bone, attr, False)


def run_case(case_name, armature, bone_name, setup_fn, override=None):
    prepare_pose_mode(armature)
    bpy.ops.pose.select_all(action="DESELECT")
    reset_bone_selection(armature)
    bpy.context.view_layer.update()

    describe_context(f"{case_name}/before", armature, bone_name)
    setup_fn(armature, bone_name, override)
    bpy.context.view_layer.update()
    describe_context(f"{case_name}/after_setup", armature, bone_name)

    result = bpy.ops.b2pmxem.lock_rotation(flag=True)
    bpy.context.view_layer.update()
    describe_context(f"{case_name}/after_operator", armature, bone_name)
    log(f"[RESULT] {case_name}: {result}")


def run():
    work_dir = make_work_dir()
    log(f"[INFO] work_dir={work_dir}")

    blend_path = os.path.join(work_dir, "pose_selection_view3d.blend")
    shutil.copyfile(os.path.join(SAMPLE_DIR, "sample.blend"), blend_path)
    bpy.ops.wm.open_mainfile(filepath=blend_path, load_ui=False)

    ensure_module_loaded()
    override = find_view3d_override()
    log(f"[INFO] view3d_override={'found' if override else 'missing'}")

    append_result = bpy.ops.b2pmxem.append_template(type="Type1")
    log(f"[RESULT] append_template: {append_result}")

    armature = first_pose_bone_object()
    if armature is None:
        raise RuntimeError("No armature found after append_template")

    bone_name = armature.pose.bones[0].name
    log(f"[INFO] target_bone={bone_name}")

    def case_pose_select_all_then_active(arm, target, _override):
        bpy.ops.pose.select_all(action="SELECT")
        arm.data.bones.active = arm.data.bones[target]

    def case_temp_override_pose_select_all(arm, target, _override):
        if not _override:
            log("[INFO] temp_override skipped: no VIEW_3D available")
            return
        with bpy.context.temp_override(**_override):
            bpy.ops.pose.select_all(action="SELECT")
            bpy.ops.pose.select_all(action="DESELECT")
        bone = arm.data.bones[target]
        arm.data.bones.active = bone
        if hasattr(bone, "select"):
            bone.select = True

    def case_temp_override_select_hierarchy(arm, target, _override):
        if not _override:
            log("[INFO] temp_override skipped: no VIEW_3D available")
            return
        bone = arm.data.bones[target]
        arm.data.bones.active = bone
        if hasattr(bone, "select"):
            bone.select = True
        if hasattr(bone, "select_head"):
            bone.select_head = True
        if hasattr(bone, "select_tail"):
            bone.select_tail = True
        with bpy.context.temp_override(**_override):
            try:
                bpy.ops.pose.select_hierarchy(direction="CHILD", extend=False)
            except RuntimeError as exc:
                log(f"[INFO] select_hierarchy failed: {exc}")

    def case_select_all_then_reduce(arm, target, _override):
        bpy.ops.pose.select_all(action="SELECT")
        for bone in arm.data.bones:
            if bone.name == target:
                continue
            if hasattr(bone, "select"):
                bone.select = False
            if hasattr(bone, "select_head"):
                bone.select_head = False
            if hasattr(bone, "select_tail"):
                bone.select_tail = False
        bone = arm.data.bones[target]
        arm.data.bones.active = bone
        if hasattr(bone, "select"):
            bone.select = True

    run_case("pose_select_all_then_active", armature, bone_name, case_pose_select_all_then_active, override)
    run_case("temp_override_pose_select_all", armature, bone_name, case_temp_override_pose_select_all, override)
    run_case("temp_override_select_hierarchy", armature, bone_name, case_temp_override_select_hierarchy, override)
    run_case("select_all_then_reduce", armature, bone_name, case_select_all_then_reduce, override)


if __name__ == "__main__":
    try:
        run()
    except Exception:
        traceback.print_exc()
        raise
