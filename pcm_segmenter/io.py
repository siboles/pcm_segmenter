from typing import List
import pathlib
import vtk
import pyCellAnalyst as pycell
import pandas
from . import config

BASE_DIRECTORY = pathlib.Path(".")


def set_base_directory(directory: str):
    global BASE_DIRECTORY
    directory = pathlib.Path(directory)
    if not directory.exists():
        directory.mkdir()
    BASE_DIRECTORY = directory


def read_image_stack(directory: str, spacing: List[float]) -> pycell.FloatImage:
    return pycell.FloatImage(directory, spacing=spacing)


def write_isocontour(isocontour: vtk.vtkPolyData, name: str):
    filepath = BASE_DIRECTORY.joinpath(f"{name}.vtp")
    print(f"... Saving isocontour to {filepath}")
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(str(filepath))
    writer.SetInputData(isocontour)
    writer.Write()


def write_results_to_excel(dataframe: pandas.DataFrame, name: str):
    filepath = BASE_DIRECTORY.joinpath(f"{name}.xlsx")
    dataframe.to_excel(filepath)
