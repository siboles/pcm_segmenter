import sys
sys.path.append("..")
from pcm_segmenter import config, segment, io
import pyCellAnalyst as pycell

c = config.parse_config(configuration_file="../configs/test.yaml")

ecm = io.read_image_stack(c.ecm_image_directories[0], spacing=c.image_spacing[0])
cell = io.read_image_stack(c.cell_image_directories[0], spacing=c.image_spacing[0])

ecm_roi = pycell.RegionsOfInterest(ecm, regions_of_interest=c.regions_of_interest[0], start_col=0, slice2d=True)
cell_roi = pycell.RegionsOfInterest(cell, regions_of_interest=c.regions_of_interest[0], start_col=0, slice2d=True)

ecm_smooth = segment.process_ecm(ecm_roi.images[0], config=c)
cell_smooth = segment.process_cell(cell_roi.images[0], config=c)

ecm_smooth.writeAsVTK(name="ecm")
cell_smooth.writeAsVTK(name="cell")

ecm_segmentation = segment.segment_ecm(ecm_smooth)
cell_segmentation = segment.segment_cell(cell_smooth)

io.write_isocontour(ecm_segmentation.isocontour, name=f"ecm")

contours = segment.combine_segmented_isocontours([ecm_segmentation.isocontour, cell_segmentation.isocontour])
io.write_isocontour(contours, name="test")