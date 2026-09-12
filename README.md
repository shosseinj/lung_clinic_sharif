# Lung CT Processing and Registration Experiments

This repository contains medical-imaging experiments for processing thoracic CT studies. The code includes DICOM/array handling, lung or lobe-oriented processing, image registration, visualization, and air-trapping-related analysis utilities.

## Research Scope

The project investigates a processing workflow in which CT volumes from different respiratory states or acquisitions can be aligned and compared. The repository includes scripts for registration, lobe fragmentation/analysis, loading preprocessed arrays, plotting segmented DICOM data, and inspecting imaging metadata.

## Main Components

- `registration.py` / `reg.py` — image-registration experiments
- `fragment_lobes.py` — lobe-oriented processing utilities
- `plot_segmented_dcm.py` — visualization of segmented DICOM data
- `load_npy.py` — loading and inspecting preprocessed arrays
- `print_meta.py` — DICOM metadata inspection
- `air_trapping_results/` — experiment outputs related to air-trapping analysis

## Research Use

The repository is intended as an experimental medical-image analysis workspace rather than a clinical software product. Quantitative outputs should be interpreted together with the acquisition protocol, preprocessing steps, registration settings, and validation procedure used in the corresponding experiment.

## Data and Privacy

Medical images may contain protected or identifying information in pixel data or DICOM metadata. A public research repository should contain only data that are explicitly permitted for public redistribution and have been appropriately de-identified. Raw clinical studies should otherwise be stored outside Git.

