# proespm-py3

Proespm is a Python-based tool designed to transform scientific data into
interactive, shareable HTML reports. It supports automatic data processing for
specific types of data, such as image corrections for scanning probe microscopy
(SPM) data. An example of a generated report can be found
[here](https://matkrin.github.io/proespm-py3/example.html). This is a Python 3
implementation of [proespm](https://github.com/n-bock/proespm). Have a look a
the [documentation](https://matkrin.github.io/proespm-py3) for information about
installation, usage and extensibility.

## Supported Methods

- Scanning Probe Microscopy (SPM):
  - Specs Aarhus MUL (.mul, .flm)
  - Omicron MATRIX (.mtrx)
  - RHK SM4 (.sm4)
  - Nanonis SXM (.sxm)
  - Nanosurf STM and AFM (.nid)

- X-ray Photoelectron Spectroscopy (XPS):
  - Omicron EIS (.txt)

- Auger Electron Spectroscopy (AES):
  - STAIB WinSpectro (.vms, .dat)

- Quartz-Crystal Microbalance (QCMB):
  - Inficon STM2 (.log)

- Cyclic Voltammetry (CV), Chronoamperometry (CA), Linear Sweep Voltammetry
  (LSV), Impedence Spectroscopy (EIS):
  - Nordic Electrochemistry EC4
  - PalmSens (.cvs, .pssession)

- Temperature Programmed Desorption (TPD):
  - LabView (self written)

- png, jpg images, e.g. LEED images
