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


def mark(results, key, ok, detail=""):
    results[key] = (ok, detail)
    status = "PASS" if ok else "FAIL"
    suffix = f" :: {detail}" if detail else ""
    log(f"[{status}] {key}{suffix}")


def ensure_module_loaded():
    if MODULE_NAME in sys.modules:
        addon_utils.disable(MODULE_NAME, default_set=False)
        del sys.modules[MODULE_NAME]

    addon_utils.modules_refresh()
    default_before, loaded_before = addon_utils.check(MODULE_NAME)
    try:
        bpy.ops.preferences.addon_enable(module=MODULE_NAME)
        enabled = True
    except RuntimeError:
        enabled = addon_utils.enable(MODULE_NAME, default_set=False, persistent=False)
    default_after, loaded_after = addon_utils.check(MODULE_NAME)
    module = sys.modules.get(MODULE_NAME)
    addon_keys = list(getattr(bpy.context.preferences, "addons", {}).keys())
    return enabled, module, {
        "default_before": default_before,
        "loaded_before": loaded_before,
        "default_after": default_after,
        "loaded_after": loaded_after,
        "addon_keys": addon_keys,
    }


def find_active_armature():
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def describe_pose_selection():
    selected = getattr(bpy.context, "selected_pose_bones", None)
    active = getattr(bpy.context, "active_pose_bone", None)
    selected_names = []
    if selected:
        selected_names = [bone.name for bone in selected]
    active_name = getattr(active, "name", None)
    return {
        "selected_pose_bones": selected_names,
        "active_pose_bone": active_name,
    }


def make_work_dir():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = os.path.join(FOR_LOCAL_DIR, f"tmp_issue13_{timestamp}")
    os.makedirs(work_dir, exist_ok=True)
    return work_dir


def run():
    results = {}
    work_dir = make_work_dir()
    log(f"[INFO] work_dir={work_dir}")

    default_pmx = os.path.join(SAMPLE_DIR, "default.pmx")
    working_pmx = os.path.join(work_dir, "default.pmx")
    shutil.copyfile(default_pmx, working_pmx)

    blend_path = os.path.join(work_dir, "issue13_check.blend")
    shutil.copyfile(os.path.join(SAMPLE_DIR, "sample.blend"), blend_path)

    bpy.ops.wm.open_mainfile(filepath=blend_path, load_ui=False)

    enabled, module, addon_debug = ensure_module_loaded()
    addon_path = getattr(module, "__file__", "<not loaded>") if module else "<not loaded>"
    mark(results, "addon_enable", bool(enabled and module), f"{addon_path} / {addon_debug}")

    if not module:
        return results

    import_ops = getattr(bpy.ops, "import")
    imported = import_ops.pmx_data_em(filepath=working_pmx, adjust_bone_position=False)
    armature = find_active_armature()
    mark(results, "pmx_import", imported == {"FINISHED"} and armature is not None, str(imported))

    if armature is not None:
        select_only(armature)

    xml_result = bpy.ops.b2pmxem.save_as_xml(filename="default.pmx")
    xml_path = os.path.join(work_dir, "default.xml")
    mark(results, "xml_make", xml_result == {"FINISHED"} and os.path.isfile(xml_path), str(xml_result))

    export_path = os.path.join(work_dir, "issue13_exported.pmx")
    export_result = bpy.ops.export.pmx_data_em(
        filepath=export_path,
        encode_type="OPT_Utf-16",
        use_mesh_modifiers=False,
        use_custom_normals=False,
    )
    mark(results, "pmx_export", export_result == {"FINISHED"} and os.path.isfile(export_path), str(export_result))

    bpy.ops.object.select_all(action="DESELECT")
    append_result = bpy.ops.b2pmxem.append_template(type="Type1")
    appended_armature = bpy.context.view_layer.objects.active
    append_ok = (
        append_result == {"FINISHED"}
        and appended_armature is not None
        and appended_armature.type == "ARMATURE"
    )
    mark(results, "template_append", append_ok, str(append_result))

    bone_tool_ok = False
    bone_tool_detail = "append failed"
    if append_ok and appended_armature.pose.bones:
        bpy.ops.object.mode_set(mode="POSE")
        for bone in appended_armature.data.bones:
            for attr in ("select", "select_head", "select_tail"):
                if hasattr(bone, attr):
                    setattr(bone, attr, False)
            if hasattr(bone, "hide_select"):
                bone.hide_select = False
        first_bone = appended_armature.data.bones[0]
        for attr in ("select", "select_head", "select_tail"):
            if hasattr(first_bone, attr):
                setattr(first_bone, attr, True)
        appended_armature.data.bones.active = first_bone
        selection_state = describe_pose_selection()
        lock_result = bpy.ops.b2pmxem.lock_rotation(flag=True)
        lock_state = list(appended_armature.pose.bones[first_bone.name].lock_rotation)
        bone_tool_ok = lock_result == {"FINISHED"} and all(lock_state)
        bone_tool_detail = (
            f"{lock_result} / bone={first_bone.name} / "
            f"selection={selection_state} / lock_rotation={lock_state}"
        )
        bpy.ops.object.mode_set(mode="OBJECT")
    mark(results, "bone_tool", bone_tool_ok, bone_tool_detail)

    xml_linkage_ok = results["xml_make"][0] and results["pmx_export"][0]
    mark(results, "xml_linkage", xml_linkage_ok, "save_as_xml -> export path")

    return results


if __name__ == "__main__":
    try:
        outcome = run()
        passed = sum(1 for ok, _ in outcome.values() if ok)
        total = len(outcome)
        log(f"[SUMMARY] {passed}/{total} checks passed")
    except Exception:  # pragma: no cover - debug helper for Blender runs
        traceback.print_exc()
        raise
