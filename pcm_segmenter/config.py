import pathlib
from pydantic import BaseModel, validator
from typing import List
import yaml


class Config(BaseModel):
    regions_of_interest: List[str]
    ecm_image_directories: List[str]
    cell_image_directories: List[str]
    output_directories: List[str]
    image_spacing: List[List[float]]
    bilateral_domain_sigma: float = 0.5
    bilateral_range_sigma: float = 5.0
    equalization_window: List[float] = (0.5, 0.5)
    exponent: float = 1.1
    diffusion_conductance: float = 9.0
    diffusion_iterations: int = 20
    surface_angles: List[float]


    @validator("ecm_image_directories", "cell_image_directories",
               "output_directories", "image_spacing", "surface_angles")
    def check_list_lengths(cls, v, values, **kwargs):
        if len(v) != len(values["regions_of_interest"]):
            raise ValueError("Must match list length of regions_of_interest.")
        return v

    @validator("output_directories")
    def create_output_directories(cls, v):
        for directory in v:
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        return v


def parse_config(configuration_file: str = "") -> Config:
    with open(pathlib.Path(configuration_file), "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return Config(**data)
