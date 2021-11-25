import sys
import pyCellAnalyst as pycell
sys.path.append("..")
from pcm_segmenter import config, segment, io, analysis

c = config.parse_config(configuration_file="../configs/test.yaml")
io.set_base_directory("results")

for i, ecm_image_directory in enumerate(c.ecm_image_directories):
    ecm = io.read_image_stack(ecm_image_directory, spacing=c.image_spacing[i])
    cell = io.read_image_stack(c.cell_image_directories[i], spacing=c.image_spacing[i])

    ecm_roi = pycell.RegionsOfInterest(ecm, regions_of_interest=c.regions_of_interest[i], start_col=0, slice2d=True)
    cell_roi = pycell.RegionsOfInterest(cell, regions_of_interest=c.regions_of_interest[i], start_col=0, slice2d=True)

    ecm_smooth = segment.process_ecm(ecm_roi.images[0], conf=c)
    cell_smooth = segment.process_cell(cell_roi.images[0], conf=c)

    ecm_smooth.writeAsVTK(name=f"ecm_{i:02d}")
    cell_smooth.writeAsVTK(name=f"cell_{i:02d}")

    ecm_segmentation = segment.segment_ecm(ecm_smooth)
    cell_segmentation = segment.segment_cell(cell_smooth)

    io.write_isocontour(ecm_segmentation.isocontour, name=f"ecm_{i:02d}")

    thickness_polydatas = analysis.calculate_thicknesses(cell_segmentation.isocontour, ecm_segmentation.isocontour,
                                                         c.image_spacing, c.surface_angles[0])

    io.write_isocontour(thickness_polydatas[0], name=f"thickness_{i:02d}")
    dataframe = analysis.create_pandas_dataframe(thickness_polydatas[0])
    io.write_results_to_excel(dataframe, name=f"thicknesses_{i:02d}")