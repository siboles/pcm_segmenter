from typing import List, Tuple

import numpy as np
import pandas
import vtk
from vtk.util import numpy_support


def _label_cell_contours(cell_contour: vtk.vtkPolyData) -> vtk.vtkPolyDataConnectivityFilter:
    connected_components = vtk.vtkPolyDataConnectivityFilter()
    connected_components.SetExtractionModeToAllRegions()
    connected_components.ScalarConnectivityOff()
    connected_components.ColorRegionsOn()
    connected_components.SetInputData(cell_contour)
    connected_components.Update()
    return connected_components


def _get_normals(polydata: vtk.vtkPolyData, flip: bool = False) -> vtk.vtkPolyData:
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(polydata)
    normals.SetFlipNormals(flip)
    normals.ConsistencyOn()
    normals.Update()
    return normals.GetOutput()


def _extrude_contour(c: vtk.vtkPolyData, length: float, flip: bool = False) -> vtk.vtkPolyData:
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

    extrusion = _get_normals(triangle.GetOutput(), flip=flip)
    return extrusion


def _convex_hull_2d(c: vtk.vtkPolyData, spacing: float) -> vtk.vtkPolyData:
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


def _create_extrusion_lists(isocontours: vtk.vtkPolyDataConnectivityFilter,
                            spacing: List[float]) -> Tuple[List[vtk.vtkPolyData], List[vtk.vtkPolyData]]:
    """For each unique isocontour id create an extrusion of the original contour and its convex hull."""
    convex_hull_spline_spacing = np.min(spacing) / 2.0
    extrusion_length = np.mean(spacing)
    cell_extrusions = []
    cell_convex_hulls = []
    isolate_cell_contour = vtk.vtkThreshold()
    isolate_cell_contour.SetInputData(isocontours.GetOutput())
    for contour_id in range(isocontours.GetNumberOfExtractedRegions()):
        isolate_cell_contour.ThresholdBetween(contour_id, contour_id + 0.5)
        geo_filter = vtk.vtkGeometryFilter()
        geo_filter.SetInputConnection(isolate_cell_contour.GetOutputPort())
        geo_filter.Update()
        cell_extrusions.append(_extrude_contour(geo_filter.GetOutput(), extrusion_length, flip=True))
        cell_convex_hulls.append(_extrude_contour(_convex_hull_2d(geo_filter.GetOutput(), convex_hull_spline_spacing),
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


def _build_obb_tree(polydata: vtk.vtkPolyData) -> vtk.vtkOBBTree:
    tree = vtk.vtkOBBTree()
    tree.SetDataSet(polydata)
    tree.BuildLocator()
    return tree


def _get_rotation_matrix(surface_angle: float) -> np.ndarray:
    angle = np.deg2rad(surface_angle)
    return np.array([[np.cos(-angle), -np.sin(-angle), 0.0],
                     [np.sin(-angle), np.cos(-angle), 0.0],
                     [0.0, 0.0, 0.0]], dtype=float)


def _initialize_float_array(number_of_tuples: int, number_of_components: int, name: str):
    array = vtk.vtkFloatArray()
    array.SetNumberOfComponents(number_of_components)
    array.SetNumberOfTuples(number_of_tuples)
    array.SetName(name)
    return array


def _initialize_int_array(number_of_tuples: int, number_of_components: int, name: str):
    array = vtk.vtkIntArray()
    array.SetNumberOfComponents(number_of_components)
    array.SetNumberOfTuples(number_of_tuples)
    array.SetName(name)
    return array


def _make_thickness_polydata(coordinates: vtk.vtkFloatArray, thicknesses: vtk.vtkFloatArray,
                             directions: vtk.vtkFloatArray, region_ids: vtk.vtkIntArray,
                             angular_directions: vtk.vtkFloatArray) -> vtk.vtkPolyData:
    points = vtk.vtkPoints()
    points.SetData(coordinates)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.GetPointData().AddArray(thicknesses)
    polydata.GetPointData().AddArray(directions)
    polydata.GetPointData().AddArray(region_ids)
    polydata.GetPointData().AddArray(angular_directions)
    return polydata


def calculate_thicknesses(cell_isocontour: vtk.vtkPolyData, ecm_isocontour: vtk.vtkPolyData,
                          spacing: List[float], surface_angle: float) -> List[vtk.vtkPolyData]:
    ecm_extrusion = _extrude_contour(ecm_isocontour, np.mean(spacing))
    cell_contours = _label_cell_contours(cell_isocontour)
    cell_extrusions, cell_convex_hulls = _create_extrusion_lists(cell_contours, spacing)

    rotation_matrix = _get_rotation_matrix(surface_angle)
    region_angle_bounds = np.linspace(0.0, 2.0 * np.pi, num=5, endpoint=True) - np.pi / 4.0

    thickness_polydatas = []
    for cell_id, (cell, convex_hull) in enumerate(zip(cell_extrusions, cell_convex_hulls)):
        append_filter = vtk.vtkAppendPolyData()
        append_filter.AddInputData(ecm_extrusion)
        for cell_id2, cell2 in enumerate(cell_extrusions):
            if cell_id == cell_id2:
                continue
            else:
                append_filter.AddInputData(cell2)
        append_filter.Update()
        cell_tree = _build_obb_tree(cell)
        other_tree = _build_obb_tree(append_filter.GetOutput())

        points = numpy_support.vtk_to_numpy(convex_hull.GetPoints().GetData())
        normals = numpy_support.vtk_to_numpy(convex_hull.GetPointData().GetArray("Normals"))
        idx = points[:, 2] < 1e-7
        points = points[idx, :]
        normals = normals[idx, :]

        number_of_points = points.shape[0]
        coordinates = _initialize_float_array(number_of_points, 3, "Coordinates")
        thicknesses = _initialize_float_array(number_of_points, 1, "Thickness")
        directions = _initialize_float_array(number_of_points, 3, "Direction")
        angular_directions = _initialize_float_array(number_of_points, 1, "Angle")

        region_ids = _initialize_int_array(number_of_points, 1, "Region")

        for row in range(number_of_points):
            # Get point on cell boundary that intersects the local normal of its convex hull
            intersection_1, thickness_1 = _get_ray_intersection(cell_tree, points[row, :], -normals[row, :], 20.0)
            # from this intersection point find intersection with PCM boundary along same direction
            intersection_2, thickness_2 = _get_ray_intersection(other_tree, intersection_1, normals[row, :], 20.0)

            coordinates.SetTuple3(row, *intersection_1)
            if thickness_2 < 1.0e-7:
                thicknesses.SetTuple1(row, 0.0)
            else:
                thicknesses.SetTuple1(row, thickness_2)

            directions.SetTuple3(row, *normals[row, :])

            rotated_direction = np.dot(rotation_matrix, normals[row, :])
            relative_to_surface_angle = np.arctan2(rotated_direction[1], rotated_direction[0])
            if relative_to_surface_angle > region_angle_bounds[-1]:
                relative_to_surface_angle -= 2.0 * np.pi
            region = np.digitize([relative_to_surface_angle], region_angle_bounds)[0]
            region_ids.SetTuple1(row, region)
            angular_directions.SetTuple1(row, np.rad2deg(relative_to_surface_angle))

        thickness_polydatas.append(_make_thickness_polydata(coordinates,
                                                            thicknesses,
                                                            directions,
                                                            region_ids,
                                                            angular_directions))
    return thickness_polydatas


def create_pandas_dataframe(polydata: vtk.vtkPolyData) -> pandas.DataFrame:
    dataframe = pandas.DataFrame()
    for array_id in range(polydata.GetPointData().GetNumberOfArrays()):
        array = polydata.GetPointData().GetArray(array_id)
        if array.GetNumberOfComponents() == 1:
            column_name = array.GetName()
            data = numpy_support.vtk_to_numpy(polydata.GetPointData().GetArray(array_id))
            dataframe[column_name] = data
    return dataframe

