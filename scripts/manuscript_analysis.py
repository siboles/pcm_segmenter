import sys
sys.path.append("..")
from pcm_segmenter import pipeline

CONFIGURATION_FILES = ("../configs/2018-06-13.yaml",
                       "../configs/2018-07-26.yaml",
                       "../configs/2018-08-08.yaml",
                       "../configs/2018-09-07.yaml",
                       "../configs/2018-09-21.yaml",
                       "../configs/2018-10-04.yaml")


for config_file in CONFIGURATION_FILES:
    aggregate_filename = config_file.split("/")[-1].replace(".yaml", "")
    configuration = pipeline.config_from_file(config_file)
    pipeline.run(configuration, aggregate_filename=aggregate_filename,
                 save_contours=True, save_thickness_polydata=True)
