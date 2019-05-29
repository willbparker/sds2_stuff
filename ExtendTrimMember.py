import model
from member import Member, MemberLocate, MarkMemberForProcess
from job import Job, ProcessJob, ProcessOneMem, ProcessSelection
from point import Point, PointLocate
import Point3D
from param import ClearSelection
import param
from macrolib.Geom3D import *



l_r = ['Left', 'Right']
which_end = None



def extend_members(extend_mem, extend_to_mem):
    extend_mem_plane = Plane(extend_mem.left.location, extend_mem.right.location, extend_mem.right.location + extend_mem.translate(0, 1, 0))
    extend_to_mem_plane = Plane(extend_to_mem.left.location, extend_to_mem.right.location, extend_to_mem.right.location + extend_to_mem.translate(0, 1, 0))
    extend_mem_line = Line(extend_mem.left.location, extend_mem.right.location)
    extend_to_mem_line = Line(extend_to_mem.left.location, extend_to_mem.right.location)

    if extend_mem_plane.isParallel(extend_to_mem_plane):
        extend_to_mem_plane = Plane(extend_to_mem.left.location, extend_to_mem.right.location,
                                    extend_to_mem.right.location + extend_to_mem.translate(0, 0, 1))
        if extend_mem_plane.isParallel(extend_to_mem_plane):
            param.Warning('Members must have intersection point and cannot be parallel.')
            return None

    inter_point = extend_to_mem_plane.intersLinePlane(extend_mem_line)

    if extend_mem_line.ptNearSegment(inter_point):
        global which_end
        if type(which_end) != type(''):
            which_end = param.yes_or_no('Which end?', 'Left', 'Right')
        end_to_extend = [extend_mem.left, extend_mem.right][l_r.index(which_end)]
    else:
        end_to_extend = [i for i in [extend_mem.left, extend_mem.right] if Point3D.Point3D(i.location).Distance(inter_point) == min(Point3D.Point3D(extend_mem.left.location).Distance(inter_point),Point3D.Point3D(extend_mem.right.location).Distance(inter_point))][0]

    end_to_extend.location = Point(inter_point)
    extend_mem.Update()


def main():
    members_to_extend = False
    selection = model.members(2)
    ClearSelection()
    if selection:
        members = [m for m in selection if model.IsMember(m)]
        members_to_extend = [Member(m.number) for m in members]

    else:
        selection = model.LocateMultiple('Select members to extend or trim:', model.IsMember)
        if selection:
            members_to_extend = [Member(m.number) for m in model.GetSelection()]
            ClearSelection()
    if members_to_extend:
        selection = model.LocateSingle('Select Member to extend or trim to:', model.IsMember)
        if selection:
            extend_to_mem = Member(model.GetSelection()[0].number)
            ClearSelection()

            left_ends = [model.member(m.number).ends[0] for m in members_to_extend]
            model.Select(left_ends) # highlights the left end node of the members to be extended
            for m in members_to_extend:
                extend_members(m, extend_to_mem)

            members_to_process =  [m for m in members_to_extend for m in [extend_to_mem]]
            for m in members_to_process:
                MarkMemberForProcess(m)
            ProcessSelection(members_to_process)



if __name__ == "__main__":
    main()