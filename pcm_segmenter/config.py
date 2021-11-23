import os
from pydantic import BaseModel
from typing import List
import yaml


class Config(BaseModel):
    regions_of_interest: List[str]
    ecm_image_directories: List[str]
    cell_image_directories: List[str]
    image_spacing: List[List[float]]
    bilateral_domain_sigma: float = 0.5
    bilateral_range_sigma: float = 5.0
    equalization_window: List[float] = (0.5, 0.5)
    exponent: float = 1.1
    diffusion_conductance: float = 9.0
    diffusion_iterations: float = 20
    surface_angles: List[float]


def parse_config(configuration_file: str = "") -> Config:
    with open(os.path.abspath(configuration_file), "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return Config(**data)
