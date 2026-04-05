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
    work_dir = os.path.join(FOR_LOCAL_DIR, f"tmp_pose_selection_{timestamp}")
    os.makedirs(work_dir, exist_ok=True)
    return work_dir


def first_pose_bone_object():
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and obj.pose and obj.pose.bones:
            return obj
    return None


def deselect_pose_bones(armature):
    for bone in armature.data.bones:
        for attr in ("select", "select_head", "select_tail"):
            if hasattr(bone, attr):
                setattr(bone, attr, False)


def run_case(case_name, armature, bone_name, setup_fn):
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.select_all(action="DESELECT")
    deselect_pose_bones(armature)
    bpy.context.view_layer.update()

    describe_context(f"{case_name}/before", armature, bone_name)
    setup_fn(armature, bone_name)
    bpy.context.view_layer.update()
    describe_context(f"{case_name}/after_setup", armature, bone_name)

    result = bpy.ops.b2pmxem.lock_rotation(flag=True)
    bpy.context.view_layer.update()
    describe_context(f"{case_name}/after_operator", armature, bone_name)
    log(f"[RESULT] {case_name}: {result}")


def run():
    work_dir = make_work_dir()
    log(f"[INFO] work_dir={work_dir}")

    blend_path = os.path.join(work_dir, "pose_selection_check.blend")
    shutil.copyfile(os.path.join(SAMPLE_DIR, "sample.blend"), blend_path)
    bpy.ops.wm.open_mainfile(filepath=blend_path, load_ui=False)

    ensure_module_loaded()

    append_result = bpy.ops.b2pmxem.append_template(type="Type1")
    log(f"[RESULT] append_template: {append_result}")

    armature = first_pose_bone_object()
    if armature is None:
        raise RuntimeError("No armature found after append_template")

    bone_name = armature.pose.bones[0].name
    log(f"[INFO] target_bone={bone_name}")

    def case_active_only(arm, target):
        arm.data.bones.active = arm.data.bones[target]

    def case_data_bone_select(arm, target):
        bone = arm.data.bones[target]
        arm.data.bones.active = bone
        if hasattr(bone, "select"):
            bone.select = True
        if hasattr(bone, "select_head"):
            bone.select_head = True
        if hasattr(bone, "select_tail"):
            bone.select_tail = True

    def case_pose_select(arm, target):
        bone = arm.data.bones[target]
        arm.data.bones.active = bone
        if hasattr(bone, "select"):
            bone.select = True
        bpy.ops.pose.select_all(action="DESELECT")
        arm.data.bones.active = bone
        if hasattr(bone, "select"):
            bone.select = True

    def case_select_pattern(arm, target):
        arm.data.bones.active = arm.data.bones[target]
        bpy.ops.pose.select_all(action="DESELECT")
        bpy.ops.object.select_pattern(pattern=arm.name, extend=False)
        bone = arm.data.bones[target]
        if hasattr(bone, "select"):
            bone.select = True
        if hasattr(bone, "select_head"):
            bone.select_head = True
        if hasattr(bone, "select_tail"):
            bone.select_tail = True

    run_case("active_only", armature, bone_name, case_active_only)
    run_case("data_bone_select", armature, bone_name, case_data_bone_select)
    run_case("pose_select_reset", armature, bone_name, case_pose_select)
    run_case("select_pattern", armature, bone_name, case_select_pattern)


if __name__ == "__main__":
    try:
        run()
    except Exception:
        traceback.print_exc()
        raise
