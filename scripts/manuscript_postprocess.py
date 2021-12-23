import sys
sys.path.append("..")
from pcm_segmenter import postprocess, io
import pandas

EXCEL_FILES = ("pipeline_2018-06-13.xlsx",
               "pipeline_2018-07-26.xlsx",
               "pipeline_2018-08-08.xlsx",
               "pipeline_2018-09-07.xlsx",
               "pipeline_2018-09-21.xlsx",
               "pipeline_2018-10-04.xlsx")

OUTPUT_FILE = "manuscript_analyses_aggregated"

combined_dataframe = io.read_dataframe_from_excel(name=EXCEL_FILES[0], directory=".")
for file in EXCEL_FILES[1:]:
    dataframe = io.read_dataframe_from_excel(name=file, directory=".")
    combined_dataframe = postprocess.concatenate_pandas_dataframes([combined_dataframe, dataframe])

io.write_results_to_excel(combined_dataframe, name=OUTPUT_FILE, directory=".")
