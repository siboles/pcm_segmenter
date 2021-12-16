from typing import List
import pathlib
import vtk
import pyCellAnalyst as pycell
import pandas
from . import config


def read_image_stack(directory: str, spacing: List[float]) -> pycell.FloatImage:
    return pycell.FloatImage(directory, spacing=spacing)


def read_polydata(name: str, directory: str):
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(pathlib.Path(directory).joinpath(name))
    reader.Update()
    return reader.GetOutput()


def read_dataframe_from_excel(name: str, directory: str):
    dataframe = pandas.read_excel(pathlib.Path(directory).joinpath(name), engine="openpyxl")
    return dataframe


def write_image(image: pycell.Image, name: str, directory: str):
    image.writeAsVTK(name=pathlib.Path(directory).joinpath(name))


def write_polydata(isocontour: vtk.vtkPolyData, name: str, directory: str):
    filepath = pathlib.Path(directory).joinpath(f"{name}.vtp")
    print(f"... Saving polydata to {filepath}")
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(str(filepath))
    writer.SetInputData(isocontour)
    writer.Write()


def write_results_to_excel(dataframe: pandas.DataFrame, name: str, directory: str):
    filepath = pathlib.Path(directory).joinpath(f"{name}.xlsx")
    print(f"... Saving data to {filepath}")
    dataframe.to_excel(filepath, index=False)
