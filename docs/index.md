# Proespm

Proespm is a Python-based tool designed to transform scientific data into
interactive, shareable [HTML reports](assets/example.html). It supports automatic data
processing for specific types of data, such as image corrections for scanning
probe microscopy (SPM) data.

If you intend to use `proespm`, have a look at the
[Installation](installation.md) and [Usage](usage.md) sections.

If you want to extend the program's functionality, see
[Extending functionality](extend.md).

## Supported Methods

- Scanning Probe Microscopy (SPM):
    - Specs Aarhus MUL (.mul, .flm)
    - Omicron MATRIX (.mtrx)
    - RHK SM4 (.sm4)
    - Nanonis SXM (.sxm)
    - Nanosurf STM and AFM (.nid)
    - FAST module (.h5): fast scan, atom tracking, error topography, slow image,
      high speed

- X-ray Photoelectron Spectroscopy (XPS):
    - Omicron EIS (.txt)

- Auger Electron Spectroscopy (AES):
    - STAIB WinSpectro (.vms, .dat)

- Quartz-Crystal Microbalance (QCMB):
    - Inficon STM2 (.log)

- Cyclic Voltammetry (CV), Chronoamperometry (CA), Linear Sweep Voltammetry
  (LSV), Impedence Spectroscopy (EIS):
    - Nordic Electrochemistry EC4
    - PalmSens (.csv, .pssession)

- Temperature Programmed Desorption (TPD):
    - LabView (self written)

- Residual Gas Analyzer Software (RGA):
    - Analog Scan
    - Pressure vs Time Scan

- png, jpg images, e.g. LEED images
