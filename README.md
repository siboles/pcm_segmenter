Description
-----------
This archive contains the data and custom Python package to reproduce the image processing, segmentation, and
analysis conducted for the publication "The Protective Function of Directed Asymmetry in the Pericellular Matrix 
Enveloping Chondrocytes." Annals of Biomedical Engineering. DOI: 10.1007/s10439-021-02900-1.

Installation
------------
The Python package utilizes the conda package manager for dependency resolution. We recommend 
installing the miniforge3 implementation of conda from <https://conda-forge.org/miniforge/>

After conda installation first add the siboles channel by executing:

```
conda config --add channels siboles
```

If you did not install miniforge3, you may also need to add the conda-forge channel with:

```
conda config --add channels conda-forge
```

One can then create an isolated conda environment with all necessary dependencies with the command:

```
conda create -n NAME_OF_ENVIRONMENT pycellanalyst pydantic pyyaml
```

where, NAME_OF_ENVIRONMENT, is the user's choice. To use the pcm_segmenter Python package
the conda environment must be activated with:

```
conda activate NAME_OF_ENVIRONMENT
```

Optionally, the pcm_segmenter package can be installed for system-wide execution (with the conda environment
activated) by running:

```
python setup.py install
```

Running
-------
The study dataset can be retrieved from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5874143.svg)](https://doi.org/10.5281/zenodo.5874143)

Extract this to the top-level of this repository.

The study can then be reproduced by navigating to the scripts directory:

```
cd scripts
```

and running the segmentation and analysis with

```
python manuscript_analysis.py
```

and the post-processing with

```
python manuscript_postprocess.py
```

This will generate a results directory tree with the resulting VTK files for each specimen/region in
appropriate sub-folders. At the root level of the results directory, Excel files containing the analysis results
for each specimen will be created. Finally, after running manuscript_postprocess.py, 
manuscript_analyses_aggregate.xlsx will be written with the measurements for all cells aggregated into a single file.
