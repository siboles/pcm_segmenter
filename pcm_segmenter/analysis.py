from typing import List, Tuple

import numpy as np
import vtk


def _label_cell_contours(cell_contour: vtk.vtkPolyData):
    connected_components = vtk.vtkPolyDataConnectivityFilter()
    connected_components.SetExtractionModeToAllRegions()
    connected_components.ScalarConnectivityOff()
    connected_components.ColorRegionsOn()
    connected_components.SetInputData(cell_contour)
    connected_components.Update()
    return connected_components.GetOutput()


def _get_normals(polydata: vtk.vtkPolyData, flip: bool = False) -> vtk.vtkPolyData:
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(polydata)
    normals.SetFlipNormals(flip)
    normals.ConsistencyOn()
    normals.Update()
    return normals.GetOutput()


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

    extrusion = _get_normals(triangle.GetOutput())
    return extrusion


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


def _create_extrusion_lists(isocontours: vtk.vtkPolyData,
                            spacing: List[float]) -> Tuple[List[vtk.vtkPolyData], List[vtk.vtkPolyData]]:
    """For each unique isocontour id create an extrusion of the original contour and its convex hull."""
    convex_hull_spline_spacing = np.min(spacing) / 2.0
    extrusion_length = np.mean(spacing)
    cell_extrusions = []
    cell_convex_hulls = []
    isolate_cell_contour = vtk.vtkThreshold()
    isolate_cell_contour.SetInputData(isocontours)
    for contour_id in range(cell_contours.GetNumberOfExtractedRegions()):
        isolate_cell_contour.ThresholdBetween(contour_id, contour_id + 0.5)
        geo_filter = vtk.vtkGeometryFilter()
        geo_filter.SetInputConnection(isolate_cell_contour.GetOutputPort())
        geo_filter.Update()
        cell_extrusions.append(_extrude_contour(geo_filter.GetOutput(), extrusion_length))
        cell_convex_hulls.append(_extrude_contour(_convex_hull_2d(cell_isocontour, convex_hull_spline_spacing),
                                                  extrusion_length))
    return cell_extrusions, cell_convex_hulls


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


def _get_distance(polydata_1: vtk.vtkPolyData, polydata_2: vtk.vtkPolyData) -> Tuple[List[float], List[List[float]]]:
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


def _get_rotation_matrix(surface_angle: float) -> np.ndarray:
    angle = np.deg2rad(surface_angle)
    return np.array([[np.cos(-angle), -np.sin(-angle), 0.0],
                     [np.sin(-angle), np.cos(-angle), 0.0],
                     [0.0, 0.0, 0.0]], dtype=float)


def calculate_thicknesses(cell_isocontour: vtk.vtkPolyData, ecm_isocontour: vtk.vtkPolyData,
                          spacing: List[float]) -> np.ndarray:
    ecm_extrusion = _extrude_contour(ecm_isocontour, np.mean(spacing))
    cell_contours = _label_cell_contours(cell_isocontour)
    cell_extrusions, cell_convex_hulls = _create_extrusion_lists(cell_contours, spacing)
