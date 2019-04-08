import FloatComparison
import Locator
import model
import param
import Point3D
import MemberBase
import member
import Transform3D
import mtrl_list
import Polygon
from macrolib.ModelSelect import mtrlToGenMtrl


param.Units('inch')

def mirror_plane(locator):
    orig_point, pt_on_plane, plane_normal = Point3D.Point3D(), Point3D.Point3D(), Point3D.Point3D()
    locator.SetPrompt('Locate first point')
    locator.SetCurrentSnap('INCL')
    ok = locator.AcquireGlobalPoint(orig_point)
    if ok:
        locator.SetPrompt('Locate point to define plane:')
        locator.SetCurrentSnap('ONLN')
        locator.SetAnchorGlobal(orig_point)
        ok = locator.AcquireGlobalPoint(pt_on_plane)
        if ok:
            plane_normal = (pt_on_plane - orig_point).Unit().\
                Cross(Transform3D.ShowTransform().z) # to achieve same behavior as
                                                     # the build-in function
                                                     # "Copy material about plane perpandicllar to screen".
            pt_on_plane = orig_point + (plane_normal * 2)
            ok = FloatComparison.fne(plane_normal.Length(), 0., .0001)
    return orig_point, pt_on_plane, plane_normal, ok

def move_mtrl(mem, mtrl, orig_point, locator, offset, xform):
    locator.SetPrompt('Locate second point:')
    locator.SetCurrentSnap('INCL')
    locator.SetAnchorGlobal(orig_point)
    new_point = Point3D.Point3D()
    mtrl_idx = mtrl._as_tuple[2]
    ok = locator.AcquireGlobalPoint(new_point)
    if ok:
        xform.SetTranslation(new_point + offset)
        MemberBase.GetMemberLink(mem.number, True, True)
        MemberBase.GetMemberLink(mtrl._as_tuple[0], True, True)
        MemberBase.SetMaterialXform(mem.number, mtrl_idx, xform)
        MemberBase.GetMemberLink(mem.number, False, False)
        MemberBase.GetMemberLink(mtrl._as_tuple[0], False, False)
        mtrl_poly = Polygon.PolyList(mtrl.poly)
        with Polygon.Preview(mtrl_poly) as preview:   # graphicaly shows the new location of the mirrored material
            if not param.yes_or_no('Confirm material location: '):
                mtrlToGenMtrl(mtrl).erase()



        return True
    else: return False

def mirror_materials(selected_mtrl):
    mem = model.member(selected_mtrl[0]._as_tuple[0])
    locator = Locator.Locator3D()
    locator.SetDefaults()
    orig_point, pt_on_plane, plane_normal, ok = mirror_plane(locator)
    if ok:
        try:
            to_mem = member.MemberLocate('Locate member to copy material to or Return to keep on current member: ')
            to_mem.number  # to throw an error if user right clicks and selects 'ok' with no selection
            param.ClearSelection()
        except: to_mem = mem  # if not member is seleced, the material will stay on the original member.

        if ok:
            mirror_mtrl = model.MirrorMaterialCopyToMember(selected_mtrl[0], model.member(to_mem.number), pt_on_plane, plane_normal)
            mirror_offset = (orig_point - pt_on_plane) * 2  # gets the offset that MirrorMaterialCopyToMember gives by default
            mirror_point = orig_point - mirror_offset       # gets the corresponding point of the mirrored material
            mirror_mtrl_idx = mirror_mtrl._as_tuple[2]
            mirror_xform = Transform3D.Transform3D(to_mem.number, mirror_mtrl_idx)
            ref_offset = mirror_xform.t - mirror_point   # negates any offset from MirrorMaterialCopyToMember such that the second point
                                                         # will correspond to the original point releative to the mirrored material.

            if move_mtrl(to_mem, mirror_mtrl, orig_point, locator, ref_offset, mirror_xform):
                param.RedrawScreen()



if __name__ == '__main__':
    ok, selected_mtrl = model.PreOrPostSelection('Locate materials to mirror:', model.LocateSingle,
                                                 lambda o: model.IsMaterial(o) and not model.IsPartOfFrozenMember(o))
    if ok:
        mirror_materials(selected_mtrl)




