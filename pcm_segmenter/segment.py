from typing import List
import pyCellAnalyst as pycell
import vtk
from . import config


def process_ecm(image: pycell.FloatImage, conf: config.Config) -> pycell.FloatImage:
    """
    Apply image processing to regions of interest in ECM image sequence
    :param image: region of interest in ECM image
    :param conf: Configuration object
    :return:
    """
    image_filter = pycell.FilteringPipeline(inputImage=image)
    image_filter.addFilter(pycell.Bilateral(domainSigma=conf.bilateral_domain_sigma,
                                            rangeSigma=conf.bilateral_range_sigma))
    image_filter.addFilter(pycell.Equalize(window_fraction=conf.equalization_window))
    image_filter.execute()
    image_filter.outputImages[-1].invert()
    image_filter.outputImages[-1].image = image_filter.outputImages[-1].image ** conf.exponent
    return image_filter.outputImages[-1]


def process_cell(image: pycell.FloatImage, conf: config.Config) -> pycell.FloatImage:
    """
    Apply image processing to regions of interest in Cell image sequence
    :param image: region of interest in Cell image
    :param conf: Configuration object
    :return:
    """
    image_filter = pycell.CurvatureAnisotropicDiffusion(inputImage=image,
                                                        conductance=conf.diffusion_conductance,
                                                        iterations=conf.diffusion_iterations)
    image_filter.execute()
    return image_filter.outputImage


def segment_ecm(image: pycell.FloatImage) -> pycell.Segmentation:
    """
    Segment ECM with Otsu thresholding
    :param image: Processed region of interest in ECM image.
    :return:
    """
    segmentation = pycell.Otsu(inputImage=image, objectID=1)
    segmentation.execute()
    return segmentation


def segment_cell(image: pycell.FloatImage) -> pycell.Segmentation:
    """
    Segment cell with Otsu thresholding
    :param image: Processed region of interest in Cell image.
    :return:
    """
    segmentation = pycell.Otsu(inputImage=image, objectID=2)
    segmentation.execute()
    return segmentation


def generate_segmentation_difference_image(cell_segmentation: pycell.Segmentation,
                                           ecm_segmentation: pycell.Segmentation) -> pycell.EightBitImage:
    """
    Take the boolean exclusion of cell and ecm segmentations. This corresponds to the binary PCM image.
    :param cell_segmentation: Binary (8-bit) image of cell segmentation
    :param ecm_segmentation: Binary (8-bit) image of ecm segmentation
    :return:
    """
    difference = sitk.Xor(cell_segmentation.outputImage.image, ecm_segmentation.outputImage.image)
    return pycell.EightBitImage(data=difference)


def combine_segmented_isocontours(isocontours: List[vtk.vtkPolyData]) -> vtk.vtkPolyData:
    """
    Combines a list of 2D isoncontour vtkPolyData objects into a single vtkPolyData.
    :param isocontours: List of isocontours
    :return:
    """
    append_polydata = vtk.vtkAppendPolyData()
    for contour in isocontours:
        append_polydata.AddInputData(contour)
        append_polydata.Update()
    return append_polydata.GetOutput()
