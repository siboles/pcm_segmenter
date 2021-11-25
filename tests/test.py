import sys
import pyCellAnalyst as pycell
sys.path.append("..")
from pcm_segmenter import config, segment, io, analysis

c = config.parse_config(configuration_file="../configs/test.yaml")
io.set_base_directory("results")

for i, ecm_image_directory in enumerate(c.ecm_image_directories):
    cell_total = 0
    ecm = io.read_image_stack(ecm_image_directory, spacing=c.image_spacing[i])
    cell = io.read_image_stack(c.cell_image_directories[i], spacing=c.image_spacing[i])

    ecm_roi = pycell.RegionsOfInterest(ecm, regions_of_interest=c.regions_of_interest[i], start_col=0, slice2d=True)
    cell_roi = pycell.RegionsOfInterest(cell, regions_of_interest=c.regions_of_interest[i], start_col=0, slice2d=True)

    for chondron_id, (ecm_roi_image, cell_roi_image) in enumerate(zip(ecm_roi.images, cell_roi.images)):
        ecm_smooth = segment.process_ecm(ecm_roi_image, conf=c)
        cell_smooth = segment.process_cell(cell_roi_image, conf=c)

        ecm_segmentation = segment.segment_ecm(ecm_smooth)
        cell_segmentation = segment.segment_cell(cell_smooth)

        io.write_polydata(ecm_segmentation.isocontour, name=f"ecm_region{i:02d}_chondron{chondron_id:02d}")
        io.write_polydata(cell_segmentation.isocontour, name=f"cell_region{i:02d}_chondron{chondron_id:02d}")

        thickness_polydatas = analysis.calculate_thicknesses(cell_segmentation.isocontour, ecm_segmentation.isocontour,
                                                             c.image_spacing[i], c.surface_angles[i])

        for cell_id, thickness_polydata in enumerate(thickness_polydatas):
            io.write_polydata(thickness_polydata, name=f"thickness_region{i:02d}_chondron{chondron_id:02d}_cell{cell_id + cell_total}")
            dataframe = analysis.create_pandas_dataframe(thickness_polydata, cell_id=cell_id + cell_total)
            cell_total += 1