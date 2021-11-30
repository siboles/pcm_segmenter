import pandas
import pathlib


def get_median_thickness_for_regions(dataframe: pandas.DataFrame):
    return dataframe.groupby(["Cell", "Region"], as_index=False)["Thickness"].median()


def get_mean_thickness_for_regions(dataframe: pandas.DataFrame):
    return dataframe.groupby(["Cell", "Region"], as_index=False)["Thickness"].mean()
