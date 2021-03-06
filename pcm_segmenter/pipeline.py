import argparse
import datetime
from typing import Dict, Optional

import pandas
from pyCellAnalyst import RegionsOfInterest
from pydantic import BaseModel

from . import config, segment, analysis, io, postprocess


class PipelineResult(BaseModel):
    image_level_dataframes: Dict[str, pandas.DataFrame]
    aggregated_dataframe: pandas.DataFrame

    class Config:
        arbitrary_types_allowed = True


def config_from_file(config_file: str):
    return config.parse_config(config_file)


def run(c: config.Config,
        save_image_level_thicknesses: bool = False,
        save_aggregated_dataframes: bool = True,
        save_contours: bool = False,
        save_thickness_polydata: bool = False,
        aggregate_filename: Optional[str] = None):
    if aggregate_filename:
        aggregate_filename = f"pipeline_{aggregate_filename}"
    else:
        now = datetime.datetime.now()
        aggregate_filename = now.strftime('pipeline_run_%m_%d_%H_%M')

    image_level_dataframes = {}
    for i, ecm_image_directory in enumerate(c.ecm_image_directories):
        ecm = io.read_image_stack(ecm_image_directory, spacing=c.image_spacing[i])
        cell = io.read_image_stack(c.cell_image_directories[i], spacing=c.image_spacing[i])

        ecm_roi = RegionsOfInterest(ecm, regions_of_interest=c.regions_of_interest[i], start_col=0, slice2d=True)
        cell_roi = RegionsOfInterest(cell, regions_of_interest=c.regions_of_interest[i], start_col=0, slice2d=True)

        image_level_dataframe = []
        total_cell_count = 0
        for chondron_id, (ecm_roi_image, cell_roi_image) in enumerate(zip(ecm_roi.images, cell_roi.images)):
            ecm_smooth = segment.process_ecm(ecm_roi_image, conf=c)
            cell_smooth = segment.process_cell(cell_roi_image, conf=c)

            ecm_segmentation = segment.segment_ecm(ecm_smooth)
            cell_segmentation = segment.segment_cell(cell_smooth)

            if save_contours:
                io.write_polydata(ecm_segmentation.isocontour, name=f"ecm_chondron{chondron_id:02d}",
                                  directory=c.output_directories[i])
                io.write_polydata(cell_segmentation.isocontour, name=f"cell_chondron{chondron_id:02d}",
                                  directory=c.output_directories[i])

            thickness_polydatas = analysis.calculate_thicknesses(cell_segmentation.isocontour,
                                                                 ecm_segmentation.isocontour,
                                                                 c.image_spacing[i], c.surface_angles[i])

            for cell_id, thickness_polydata in enumerate(thickness_polydatas):
                if save_thickness_polydata:
                    io.write_polydata(thickness_polydata,
                                      name=f"thickness_chondron{chondron_id:02d}_cell{cell_id}",
                                      directory=c.output_directories[i])
                image_level_dataframe.append(
                    postprocess.create_pandas_dataframe_from_polydata(thickness_polydata,
                                                                      cell_id=cell_id + total_cell_count))

        image_level_dataframes[c.output_directories[i]] = postprocess.concatenate_pandas_dataframes(
            image_level_dataframe)
        if save_image_level_thicknesses:
            io.write_results_to_excel(image_level_dataframes[c.output_directories[i]],
                                      name=f"thicknesses",
                                      directory=c.output_directories[i])
    aggregated_dataframe = postprocess.concatenate_pandas_dataframes(image_level_dataframes.values())
    if save_aggregated_dataframes:
        io.write_results_to_excel(aggregated_dataframe, name=aggregate_filename, directory=".")

    results = PipelineResult(image_level_dataframes=image_level_dataframes,
                             aggregated_dataframe=aggregated_dataframe)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a segmentation and analysis pipeline for supplied configuration file.")
    parser.add_argument("configuration_file", type=str, nargs=1, help="Path to configuration file.")
    parser.add_argument("--aggregate_filename", type=str, nargs=1, default=None, help="Filename for aggregate data.")
    parser.add_argument("--save_thicknesses", action="store_true",
                        help="Write dataframe to excel file for each image directory")
    parser.add_argument("--save_contours", action="store_true",
                        help="Write polydata to disk for all PCM isocontours")
    parser.add_argument("--save_polydata", action="store_true",
                        help="Write polydata to disk for all PCM thickness calculations")

    args = parser.parse_args()

    configuration = config_from_file(args.configuration_file[0])

    run(configuration,
        aggregate_filename=args.aggregate_filename[0],
        save_image_level_thicknesses=args.save_thicknesses,
        save_contours=args.save_contours,
        save_thickness_polydata=args.save_polydata)
