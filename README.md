# RomGEO Geospatial Utilities for Romania

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/cartografie-ro/romgeo/blob/main/README.md)
[![ro](https://img.shields.io/badge/lang-ro-green.svg)](https://github.com/cartografie-ro/romgeo/blob/main/README.ro.md)

RomGEO is an open source software toolbox for doing geodetic datum transformations to EPSG:3844 (Stereo70) for Romania  

 - The source code is hosted on github.com:
    <https://github.com/cartografie-ro/romgeo/>   
 - The python package is hosted at:
    <https://pypi.org/project/romgeo/>

# Installation

## Install python package with pip:
```console
foo@bar:~$ pip install romgeo
```

### Optional packages can be installed
RomGEO has extra packages:
- romgeo_benchmark, command line and GUI benchmark utility
- romgeo_console, command line utilities 
- romgeo_api, fastapi implementation with single-point
- romgeo_gui, graphical implementation with some mapping tools
   
that can be installed along side, by executing:

```console
foo@bar:~$ pip install romgeo_benchmark,romgeo_console,romgeo_api,romgeo_gui
```
 
## Installation issues on Windows 10,11:
* **1. Requires the  installation of Nvidia CUDA-Toolkit, must be of the same version as the draphics drivers**
  - Download CUDA-Toolkit from <https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64>
  - Install everything except Nvidia Nsight
  - **Reboot**

# Packaging
RomGEO is delivered as a set of python modules and as a compiled Windows x64 binary Setup Package under CC BY-SA 4.0 license.

# Installing on x64 Windows 10, 11
*under development*

  
## Command line interface and executable scripts
* *the romgeo_console is still under development, est. Q4 2025*
* *the romgeo_gui is still under development, est. Q4 2025*
  
# License and copyright

Copyright (C) 2024 Centrul National de Cartografie
(<copyright@romgeo.ro>)

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/4.0/.

You are free to:
* Share — copy and redistribute the material in any medium or format
* Adapt — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

* Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
* ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

~This work is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.~

You should have received a copy of the Creative Commons Attribution-ShareAlike 4.0 International License along with this work. If not, see <https://creativecommons.org/licenses/by-sa/4.0/>
