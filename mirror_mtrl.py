import dialog
import dialog.checkbox
import dialog.dialog
import FloatComparison
import Locator
import model
import param
import Point3D
import MemberBase
import member
import Transform3D
from macrolib.helper import add_cc

def PromptForMirrorPlane(locator):
    orig_point, pt_on_plane, new_point, plane_normal = Point3D.Point3D(), Point3D.Point3D(), Point3D.Point3D(), Point3D.Point3D()
    ok = False
    locator.SetPrompt('Locate first point')
    ok = locator.AcquireGlobalPoint(orig_point)
    if ok:
        locator.SetPrompt('Locate point to define plane:')
        locator.SetAnchorGlobal(orig_point)
        ok = locator.AcquireGlobalPoint(pt_on_plane)
        if ok:
            locator.SetPrompt('Locate second point:')
            locator.SetAnchorGlobal(pt_on_plane)
            ok = locator.AcquireGlobalPoint(new_point)
            if ok:
                plane_normal = (pt_on_plane - orig_point).Unit()
                ok = FloatComparison.fne(plane_normal.Length(), 0., .0001)
    return orig_point, new_point, pt_on_plane, plane_normal, ok


def PromptAndMirrorMaterials():
    param.Units('inch')
    ok, selected_mtrl = model.PreOrPostSelection('Locate materials to mirror:',model.LocateSingle,
                                                 lambda o: model.IsMaterial(o) and not model.IsPartOfFrozenMember(o))
    if ok:
        to_mem = member.MemberLocate('Locate member to copy material to.')
        param.ClearSelection()
        locator = Locator.Locator3D()
        locator.SetDefaults()
        orig_point, new_point, pt_on_plane, plane_normal,ok = PromptForMirrorPlane(locator)
        if ok:
            mem = model.member(selected_mtrl[0]._as_tuple[0])
            mt_idx = selected_mtrl[0]._as_tuple[2]
            mirror_mtrl = model.MirrorMaterialCopyToMember(selected_mtrl[0], model.member(to_mem.number), pt_on_plane, plane_normal)
            mirror_offset = (orig_point - pt_on_plane) * 2
            mirror_point = orig_point - mirror_offset

            mirror_mtrl_idx = mirror_mtrl._as_tuple[2]
            mirror_xform = Transform3D.Transform3D(to_mem.number, mirror_mtrl_idx)
            ref_offset = mirror_xform.t - mirror_point
            mirror_xform.SetTranslation(new_point + ref_offset)


            MemberBase.GetMemberLink(to_mem.number, True, True)  # only used to lock the member
            MemberBase.GetMemberLink(mem.number, True, True)
            MemberBase.SetMaterialXform(to_mem.number, mirror_mtrl_idx, mirror_xform )
            param.RedrawScreen()
        #return mirror_mtrl



if __name__ == '__main__':
    mtrl = PromptAndMirrorMaterials()
#    if not param.yes_or_no('yes?'):
#        mtrl.erase()


