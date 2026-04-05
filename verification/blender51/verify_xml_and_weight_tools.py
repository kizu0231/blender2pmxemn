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
WEIGHT_TYPE_NAME = "*WeightType"


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
    work_dir = os.path.join(FOR_LOCAL_DIR, f"tmp_xml_weight_{timestamp}")
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


def has_weight_type_layer(mesh_obj):
    mesh = mesh_obj.data
    color_attributes = getattr(mesh, "color_attributes", None)
    if color_attributes is not None:
        return color_attributes.get(WEIGHT_TYPE_NAME) is not None
    return mesh.vertex_colors.get(WEIGHT_TYPE_NAME) is not None


def run():
    results = {}
    work_dir = make_work_dir()
    log(f"[INFO] work_dir={work_dir}")

    default_pmx = os.path.join(SAMPLE_DIR, "default.pmx")
    working_pmx = os.path.join(work_dir, "default.pmx")
    shutil.copyfile(default_pmx, working_pmx)

    blend_path = os.path.join(work_dir, "xml_weight_check.blend")
    shutil.copyfile(os.path.join(SAMPLE_DIR, "sample.blend"), blend_path)
    bpy.ops.wm.open_mainfile(filepath=blend_path, load_ui=False)

    ensure_module_loaded()

    import_result = getattr(bpy.ops, "import").pmx_data_em(filepath=working_pmx, adjust_bone_position=False)
    armature = find_armature()
    meshes = find_meshes_for_armature(armature) if armature else []
    mark(results, "pmx_import", import_result == {"FINISHED"} and armature is not None and len(meshes) > 0, str(import_result))

    if armature is None:
        return results

    select_only(armature)

    props = bpy.context.scene.b2pmxem_properties
    props.make_xml_option = "TRANSFER"
    xml_transfer_result = bpy.ops.b2pmxem.save_as_xml(filename="default.pmx")
    xml_path = os.path.join(work_dir, "default.xml")
    transfer_ok = xml_transfer_result == {"FINISHED"} and os.path.isfile(xml_path)
    mark(results, "xml_linkage_transfer", transfer_ok, str(xml_transfer_result))

    mesh_obj = meshes[0]
    select_only(mesh_obj)

    create_result = bpy.ops.b2pmxem.create_weight_type()
    created_ok = create_result == {"FINISHED"} and has_weight_type_layer(mesh_obj)
    mark(results, "weight_type_create", created_ok, str(create_result))

    reload_result = bpy.ops.b2pmxem.create_weight_type()
    reloaded_ok = reload_result == {"FINISHED"} and has_weight_type_layer(mesh_obj)
    mark(results, "weight_type_reload", reloaded_ok, str(reload_result))

    delete_result = bpy.ops.b2pmxem.delete_weight_type()
    deleted_ok = delete_result == {"FINISHED"} and not has_weight_type_layer(mesh_obj)
    mark(results, "weight_type_delete", deleted_ok, str(delete_result))

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
