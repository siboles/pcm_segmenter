import numpy as np
import vtk
from typing import List, Tuple


def _extrude_contour(c: vtk.vtkPolyData, length: float) -> vtk.vtkPolyData:
    extrusion = vtk.vtkLinearExtrusionFilter()
    extrusion.SetExtrusionTypeToNormalExtrusion()
    extrusion.CappingOff()
    extrusion.SetVector([0.0, 0.0, 1.0])
    extrusion.SetScaleFactor(length)
    extrusion.SetInputData(c)
    extrusion.Update()

    triangle = vtk.vtkTriangleFilter()
    triangle.SetInputConnection(extrusion.GetOutputPort())
    triangle.PassVertsOff()
    triangle.PassLinesOff()
    triangle.Update()
    return triangle.GetOutput()


def _convex_hull_2d(c: vtk.vtkPolyData, spacing: List[float]) -> vtk.vtkPolyData:
    convex_hull = vtk.vtkConvexHull2D()
    convex_hull.SetInputData(c)
    convex_hull.OutlineOn()
    convex_hull.SetScaleFactor(1.05)
    convex_hull.Update()

    spline = vtk.vtkSplineFilter()
    spline.SetInputConnection(convex_hull.GetOutputPort(1))
    spline.SetSubdivideToLength()
    spline.SetLength(spacing)
    spline.Update()
    return spline.GetOutput()


def _get_ray_intersection(tree: vtk.vtkOBBTree, origin: List[float],
                          direction: List[float], length: float) -> float:
    p2 = origin + direction * length
    points = vtk.vtkPoints()
    tree.IntersectWithLine(origin, p2, points, None)
    if points.GetData().GetNumberOfTuples() == 0:
        return origin, 0.0
    else:
        intersection = np.array(points.GetData().GetTuple3(0))
        return intersection, np.linalg.norm(intersection - origin)


def get_distance(polydata_1: vtk.vtkPolyData, polydata_2: vtk.vtkPolyData) -> Tuple[List[float], List[List[float]]]:
    distance_filter = vtk.vtkImplicitPolyDataDistance()
    distance_filter.SetInput(polydata_2)
    distances = []
    directions = []
    for i in range(polydata_1.GetNumberOfPoints()):
        point = [0.0, 0.0, 0.0]
        gradient = [0.0, 0.0, 0.0]
        p1.GetPoint(i, point)
        distances.append(distance_filter.EvaluateFunction(point))
        distance_filter.EvaluateGradient(point, gradient)
        directions.append(gradient)
    return distance, direction


def calculate_thicknesses(cell_isocontour: vtk.vtkPolyData, ecm_isocontour: vtk.vtkPolyData,
                          spacing: List[float]) -> np.adarray:
    cell_extrusion = _extrude_contour(cell_isocontour, np.mean(spacing))
    ecm_extrusion = _extrude_contour(ecm_isocontour, np.mean(spacing))
