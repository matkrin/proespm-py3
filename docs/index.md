# Proespm

Proespm is a Python-based tool designed to transform scientific data into
interactive, shareable HTML reports. It supports automatic data processing for
specific types of data, such as image corrections for scanning probe microscopy
(SPM) data.

If you intend to use `proespm`, have a look at the
[Installtion](installation.md) and [Usage](usage.md) sections.

If you want to extend the program's functionality, see ...TODO...

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
