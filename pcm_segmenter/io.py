from typing import List
import vtk
import pyCellAnalyst as pycell
import pandas as pds
from . import config


def read_image_stack(directory: str, spacing: List[float]) -> pycell.FloatImage:
    return pycell.FloatImage(directory, spacing=spacing)


def write_isocontour(isocontour: vtk.vtkPolyData, name: str):
    print(f"... Saving isocontour to {name}.vtp")
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(f"{name}.vtp")
    writer.SetInputData(isocontour)
    writer.Write()


def write_thicknesses_to_excel(thicknesses: pds.DataFrame):
    pass