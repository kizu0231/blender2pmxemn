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
    try:
        bpy.ops.preferences.addon_enable(module=MODULE_NAME)
    except RuntimeError:
        addon_utils.enable(MODULE_NAME, default_set=False, persistent=False)


def make_work_dir():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = os.path.join(FOR_LOCAL_DIR, f"tmp_shape_stance_{timestamp}")
    os.makedirs(work_dir, exist_ok=True)
    return work_dir


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def find_armature():
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def find_meshes_for_armature(armature):
    meshes = []
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.find_armature() == armature:
            meshes.append(obj)
    return meshes


def first_shape_keys(meshes):
    for obj in meshes:
        shape_keys = getattr(obj.data, "shape_keys", None)
        if shape_keys is not None and len(shape_keys.key_blocks) > 1:
            return obj, shape_keys
    return None, None


def pose_signature(pose_bone):
    if pose_bone is None:
        return None
    return {
        "rotation_mode": pose_bone.rotation_mode,
        "rotation_euler": tuple(round(v, 6) for v in pose_bone.rotation_euler),
        "rotation_quaternion": tuple(round(v, 6) for v in pose_bone.rotation_quaternion),
        "matrix_basis": tuple(
            tuple(round(v, 6) for v in row)
            for row in pose_bone.matrix_basis
        ),
    }


def run():
    results = {}
    work_dir = make_work_dir()
    log(f"[INFO] work_dir={work_dir}")

    default_pmx = os.path.join(SAMPLE_DIR, "default.pmx")
    working_pmx = os.path.join(work_dir, "default.pmx")
    shutil.copyfile(default_pmx, working_pmx)

    blend_path = os.path.join(work_dir, "shape_and_stance_check.blend")
    shutil.copyfile(os.path.join(SAMPLE_DIR, "sample.blend"), blend_path)
    bpy.ops.wm.open_mainfile(filepath=blend_path, load_ui=False)

    ensure_module_loaded()
    prefs = bpy.context.preferences.addons[MODULE_NAME].preferences
    prefs.use_japanese_name = False

    import_result = getattr(bpy.ops, "import").pmx_data_em(filepath=working_pmx, adjust_bone_position=False)
    armature = find_armature()
    meshes = find_meshes_for_armature(armature) if armature else []
    mark(results, "pmx_import", import_result == {"FINISHED"} and armature is not None and len(meshes) > 0, str(import_result))

    mesh_obj, shape_keys = first_shape_keys(meshes)
    if shape_keys is None:
        mark(results, "shape_key_defaults", False, "No imported shape keys found")
    else:
        non_basis = list(shape_keys.key_blocks[1:])
        bad_keys = [block.name for block in non_basis if abs(block.value) > 1.0e-6]
        detail = f"mesh={mesh_obj.name} / non_basis={len(non_basis)} / non_zero={bad_keys[:10]}"
        mark(results, "shape_key_defaults", len(bad_keys) == 0, detail)

    bpy.ops.object.select_all(action="DESELECT")
    append_result = bpy.ops.b2pmxem.append_template(type="Type1")
    armature = bpy.context.view_layer.objects.active
    append_ok = append_result == {"FINISHED"} and armature is not None and armature.type == "ARMATURE"
    mark(results, "template_append", append_ok, str(append_result))

    if append_ok:
        select_only(armature)
        bpy.ops.object.mode_set(mode="POSE")
        shoulder = armature.pose.bones.get("shoulder_L")
        arm = armature.pose.bones.get("arm_L")
        before = {"shoulder": pose_signature(shoulder), "arm": pose_signature(arm)}
        try:
            a_pose_result = bpy.ops.b2pmxem.to_stance(to_A_stance=True)
            after_a = {"shoulder": pose_signature(shoulder), "arm": pose_signature(arm)}
            t_pose_result = bpy.ops.b2pmxem.to_stance(to_A_stance=False)
            after_t = {"shoulder": pose_signature(shoulder), "arm": pose_signature(arm)}

            a_changed = before != after_a
            t_roundtrip = after_t != after_a
            detail = (
                f"A={a_pose_result} T={t_pose_result} / "
                f"before={before} / after_a={after_a} / after_t={after_t}"
            )
            mark(results, "stance_tools", a_changed and t_roundtrip, detail)
        except RuntimeError as exc:
            mark(results, "stance_tools", False, f"RuntimeError: {exc}")
        bpy.ops.object.mode_set(mode="OBJECT")

    return results


if __name__ == "__main__":
    try:
        outcome = run()
        passed = sum(1 for ok, _ in outcome.values() if ok)
        total = len(outcome)
        log(f"[SUMMARY] {passed}/{total} checks passed")
    except Exception:
        traceback.print_exc()
        raise
