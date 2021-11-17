def _extrude_contour(c, length):
    extrusionFilter = vtk.vtkLinearExtrusionFilter()
    extrusionFilter.SetExtrusionTypeToNormalExtrusion()
    extrusionFilter.CappingOff()
    extrusionFilter.SetVector([0.0, 0.0, 1.0])
    extrusionFilter.SetScaleFactor(length)
    extrusionFilter.SetInputData(c)
    extrusionFilter.Update()

    triangleFilter = vtk.vtkTriangleFilter()
    triangleFilter.SetInputConnection(extrusionFilter.GetOutputPort())
    triangleFilter.PassVertsOff()
    triangleFilter.PassLinesOff()
    triangleFilter.Update()
    return triangleFilter.GetOutput()

def _convex_hull_2d(c, spacing):
    chull = vtk.vtkConvexHull2D()
    chull.SetInputData(c)
    chull.OutlineOn()
    chull.SetScaleFactor(1.05)
    chull.Update()

    spline = vtk.vtkSplineFilter()
    spline.SetInputConnection(chull.GetOutputPort(1))
    spline.SetSubdivideToLength()
    spline.SetLength(spacing)
    spline.Update()
    return spline.GetOutput()
