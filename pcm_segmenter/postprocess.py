from typing import List
import pandas
import pathlib
import numpy as np
import vtk
from vtk.util import numpy_support


def create_pandas_dataframe_from_polydata(polydata: vtk.vtkPolyData, cell_id: int) -> pandas.DataFrame:
    dataframe = pandas.DataFrame()
    for array_id in range(polydata.GetPointData().GetNumberOfArrays()):
        array = polydata.GetPointData().GetArray(array_id)
        if array.GetNumberOfComponents() == 1:
            column_name = array.GetName()
            data = numpy_support.vtk_to_numpy(polydata.GetPointData().GetArray(array_id))
            dataframe[column_name] = data
    dataframe.insert(loc=0, column="Cell", value=np.ones(data.size, dtype=int) * cell_id)
    return dataframe


def concatenate_pandas_dataframes(dataframes: List[pandas.DataFrame]):
    max_cell_id = 0
    new_dataframe = pandas.DataFrame()
    for dataframe in dataframes:
        dataframe["Cell"] += max_cell_id
        new_dataframe = pandas.concat([new_dataframe, dataframe])
        max_cell_id = new_dataframe["Cell"].max() + 1
    return new_dataframe


def get_median_thickness_for_regions(dataframe: pandas.DataFrame):
    return dataframe.groupby(["Cell", "Region"], as_index=False)["Thickness"].median()


def get_mean_thickness_for_regions(dataframe: pandas.DataFrame):
    return dataframe.groupby(["Cell", "Region"], as_index=False)["Thickness"].mean()
