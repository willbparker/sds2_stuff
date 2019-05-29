from member import Member, MemberLocate, MarkMemberForProcess
from job import Job, ProcessJob, ProcessOneMem
from point import Point, PointLocate
import Point3D
from param import ClearSelection
import param
from macrolib.Geom3D import *



l_r = ['Left', 'Right']
ClearSelection()


def main():
    mem1 = MemberLocate('Select member to extend or trim:')
    mem2 = MemberLocate('Select Member to extend or trim to:')

    ClearSelection()

    mem1_plane = Plane(mem1.left.location, mem1.right.location, mem1.right.location + mem1.translate(0, 1, 0))
    mem2_plane = Plane(mem2.left.location, mem2.right.location, mem2.right.location + mem2.translate(0, 1, 0))
    mem1_line = Line(mem1.left.location, mem1.right.location)
    mem2_line = Line(mem2.left.location, mem2.right.location)

    if mem1_plane.isParallel(mem2_plane):
        param.Warning('Members must have intersection point and cannot be parallel.')
        return None

    inter_point = mem2_plane.intersLinePlane(mem1_line)


    if mem1_line.ptNearSegment(inter_point):
        which_end = param.yes_or_no('Which end?', 'Left', 'Right')
        end_to_extend = [mem1.left, mem1.right][l_r.index(which_end)]
    else:
        end_to_extend = [i for i in [mem1.left, mem1.right] if Point3D.Point3D(i.location).Distance(inter_point) == min(Point3D.Point3D(mem1.left.location).Distance(inter_point),Point3D.Point3D(mem1.right.location).Distance(inter_point))][0]



    end_to_extend.location = Point(inter_point)
    mem1.Update()
    MarkMemberForProcess(mem1.number)
    ProcessOneMem(mem1.number)

if __name__ == "__main__":
    main()
