# Data management plan

## Data collection

### Raw analytical data

Throughout the experimental part of the project, raw analytical data will be acquired with NMR and LC-MS.
The raw NMR data (including the acquisition and processing parameters) will be deposited into the database as IUPAC-developed [JCAMP-DX](https://opg.optica.org/as/abstract.cfm?uri=as-47-8-1093) files.
The raw MS data will be deposited as Waters `.RAW` archives locally but only the extracted averaged m/z values (stored as `.CSV`) will be archived in the final database.

On collection, instrument data will be saved as `{LCMS/NMR}_SAMOSA_EXP{0123}_B{00}_YYYY_MM_DD.format`, where `EXP` and `B` correspond to the experiment (continuous numbering) and batch number, respectively. Files will be renamed using UUIDv4 upon database insertion.

### Experimental metadata

Experimental metadata will form part of the the [database](../database) and will include:

* Experiment date
* Reaction solvents
* Reaction temperature
* Reaction time
* Total concentration of each component
* Total reaction volume

NMR acquisition parameters will be included as part of the `JCAMP-DX` file; the processing parameters form part of the database.
MS processing parameters form part of the database and the acquisition parameters will be included as part of the `.RAW` archive, in particular:

* `_HEADER.TXT` contains local paths to chromatographic methods, etc.
* `_INLET.INF` contains details of the gradient methods, detector, column compartment, and the autosampler.
* `_extern.inf` contains ionisation chamber and mass spectrometer information.

### Data analysis

Raw experimental data will be analysed using dedicated instrument software.
Nuclear magnetic resonance spectra will be processed and analysed using [TopSpin](https://store.bruker.com/products/topspin-for-processing-academic-government) via a [Python API](https://github.com/cooper-group-uol-robotics/fourier_nmr_driver) ([:fontawesome-solid-link:](https://zenodo.org/records/14261241)).
Mass spectra will be parsed using [MassLynx](https://microapps.on-demand.waters.com/home/downloads/masslynx-sdk) and in-house [LCMS Parser](https://github.com/cooper-group-uol-robotics/lcms_parser) ([:fontawesome-solid-link:](https://zenodo.org/records/11174536)).

### Data acquisition and review

At the end of each batch of reactions, the workflow software will produce a summary document with plots of all spectroscopic measurements for visual inspection.
The goal for those summary documents is to automatically convert them into relevant SI entries using Markdown or LaTeX.
The summary will be quickly reviewed by the experimenter, who will then decide whether all data points should be added into the database or whether any experiments should be repeated.
All negative results will be added into the database, repetitions will only be requested when the collected data are visibly wrong (*e.g.*, issues with shimming the magnet, blocked injection needles, empty solvent reservoirs).
Experimenter handle will be recorded at insertion time for future reference but will not be deposited with the manuscript.
Experimenter comments regarding the failure will also be deposited to help troubleshooting in the future.

## Access and storage

### Licensing

The recommended license for data is `CC0` where possible to allow for greatest interoperability and reusability.
We strive to use `CC BY 4.0` for non-data creative work and `(L)GPL v3` for software.

### Short- and long-term storage

During development, the all raw data will be held on the instrument computers in the AIC laboratories.
Processed data will be kept on the AIC group file server.
Code will be stored on the dedicated [GitHub repository](https://github.com/fiszczyp/supramol_explorer).
All tabular data will be validated and serialised for preservation.
When the project is submitted for publication, we will deposit all the associated data in machine-readable formats ([see here](#raw-analytical-data)) in an open-access repository ([Zenodo](https://zenodo.org/), [figshare](https://figshare.com/) or other - to be determined at the time of submission), which we would ask to be cited in any derivative works.
The corresponding authors will act as the main point of contact for the archived data; in the meantime please get in touch *via* [GitHub issues](https://github.com/fiszczyp/supramol_explorer/issues).

## Documentation

To aid with cross-institutional collaborations on the SAMOSA project, the documentation related to the data management and project contribution will be stored together with the software documentation (on project [GitHub](https://github.com/fiszczyp/supramol_explorer)) and the corresponding [pages](https://fiszczyp.github.io/supramol_explorer/).
In particular, separate pages will be dedicated to the documentation and logic of:

* ChemSpeed programme
* Raw data processing and analysis
* Autonomous decision maker
* Database design and API
