import pathlib
from pydantic import BaseModel, validator
from typing import List
import yaml


class Config(BaseModel):
    """
    Defines configuration for segmentation and thickness analysis of PCM.
    :param regions_of_interest: List of paths to excel files defining user-defined bounding boxes around chondrons
    :param ecm_image_directories: List of paths to directories containing TIFF sequences for ECM channel
    :param cell_image_directories: List of paths to directories containing TIFF sequences for Cell channel
    :param output_directories: List of paths to store output of segmentation and analysis
    :param image_spacing: List of [x, y, z] spacings for corresponding ECM and Cell image sequences
    :param bilateral_domain_sigma: Variance of domain Gaussian for bilateral filter
    :param bilateral_range_sigma: Variance of range Gaussian for bilateral filter
    :param equalization_window: List of window dimensions (x, y) for adaptive contrast equalization
    :param exponent: Exponent to raise ECM image region of interest to. This is to reduce background intensity.
    :param diffusion_conductance: Diffusion coefficient for curvature-based anisotropic diffusion smoothing
    :param diffusion_iterations: Iterations of diffusion smoothing
    :param surface_angles: List of orientation angles of cartilage surface for each image sequence
    """
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
