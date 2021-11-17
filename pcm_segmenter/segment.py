from typing import List
import pyCellAnalyst as pycell
import vtk
from . import config


def process_ecm(image: pycell.FloatImage, config: config.Config) -> pycell.FloatImage:
    image_filter = pycell.FilteringPipeline(inputImage=image)
    image_filter.addFilter(pycell.Bilateral(domainSigma=config.bilateral_range_sigma,
                                            rangeSigma=config.bilateral_range_sigma))
    image_filter.addFilter(pycell.Equalize(window_fraction=config.equalization_window))
    image_filter.execute()
    image_filter.outputImages[-1].invert()
    image_filter.outputImages[-1].image = image_filter.outputImages[-1].image ** config.exponent
    return image_filter.outputImages[-1]


def process_cell(image: pycell.FloatImage, config: config.Config) -> pycell.FloatImage:
    image_filter = pycell.CurvatureAnisotropicDiffusion(inputImage=image,
                                                        conductance=config.diffusion_conductance,
                                                        iterations=config.diffusion_iterations)
    image_filter.execute()
    return image_filter.outputImage


def segment_ecm(image: pycell.FloatImage):
    segmentation = pycell.Otsu(inputImage=image, objectID=1)
    segmentation.execute()
    return segmentation


def segment_cell(image: pycell.FloatImage) -> pycell.EightBitImage:
    segmentation = pycell.Otsu(inputImage=image, objectID=2)
    segmentation.execute()
    return segmentation


def combine_segmented_images():
    pass


def combine_segmented_isocontours(isocontours: List[vtk.vtkPolyData]) -> vtk.vtkPolyData:
    append_polydata = vtk.vtkAppendPolyData()
    for contour in isocontours:
        append_polydata.AddInputData(contour)
        append_polydata.Update()
    return append_polydata.GetOutput()
