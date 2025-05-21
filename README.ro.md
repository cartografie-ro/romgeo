# RomGEO Utilitare Geospațiale pentru România

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/cartografie-ro/romgeo/blob/main/README.md)
[![ro](https://img.shields.io/badge/lang-ro-green.svg)](https://github.com/cartografie-ro/romgeo/blob/main/README.ro.md)

RomGEO este un set de instrumente software open source pentru realizarea transformărilor geodezice datumului EPSG:3844 (Stereo70) pentru România.

 - Codul sursă este găzduit pe github.com:
    <https://github.com/cartografie-ro/romgeo/>   
 - Pachetul Python este găzduit pe:
    <https://pypi.org/project/romgeo/>

# Instalare

## Instalare pachet Python cu pip:
```console
foo@bar:~$ pip install romgeo
```

### Pachete opționale care pot fi instalate
RomGEO are pachete suplimentare:
- romgeo_benchmark, utilitar de benchmark în linie de comandă și GUI
- romgeo_console, utilitare de linie de comandă
- romgeo_api, implementare fastapi punct cu punct
- romgeo_gui, implementare grafică cu unele unelte de mapare
   
care pot fi instalate, executând:

```console
foo@bar:~$ pip install romgeo_benchmark,romgeo_console,romgeo_api,romgeo_gui
```
 
## Probleme de instalare pe Windows 10, 11:
* **1. Necesită instalarea Nvidia CUDA-Toolkit, trebuie să fie aceeași versiune ca și driverele grafice**
  - Descărcați CUDA-Toolkit de la <https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64>
  - Instalați totul, cu excepția Nvidia Nsight
  - **Reboot**

# Packaging
romgeo_GUI este livrat ca module Python și ca pachet de instalare compilat Windows x64 sub licență CC BY-SA 4.0

# Instalare pe x64 Windows 10, 11
*în dezvoltare*

  
## Interfață de linie de comandă și scripturi executabile
* *romgeo_console este încă în dezvoltare, estimare Q4 2024*
* *romgeo_gui este încă în dezvoltare, estimare Q4 2024*
  
# Licență și drepturi de autor

Copyright (C) 2024 Centrul National de Cartografie
(<copyright@romgeo.ro>)

Această lucrare este licențiată sub Licența Creative Commons Attribution-ShareAlike 4.0 International. Pentru a vizualiza o copie a acestei licențe, vizitați <https://creativecommons.org/licenses/by-sa/4.0/>.

Sunteți liber să:
* Distribuiți — copiați și redistribuiți materialul în orice format sau mediu
* Adaptați — remixați, transformați și construiți pe baza materialului pentru orice scop, chiar și comercial.

În următoarele condiții:

* Atribuire — Trebuie să acordați credit adecvat, să furnizați un link către licență și să indicați dacă au fost făcute modificări. Puteți face acest lucru în orice mod rezonabil, dar nu într-un mod care să sugereze că licențiatorul vă sprijină pe dvs. sau utilizarea dvs.
* ShareAlike — Dacă remixați, transformați sau construiți pe baza materialului, trebuie să distribuiți contribuțiile dvs. sub aceeași licență ca și originalul.

Fără restricții suplimentare — Nu puteți aplica termeni legali sau măsuri tehnologice care să restricționeze legal pe alții să facă orice permite licența.

~Această lucrare este distribuită în speranța că va fi utilă, dar FĂRĂ NICI O GARANȚIE; fără chiar garanția implicită de VANDABILITATE sau POTRIVIRE PENTRU UN ANUMIT SCOP.~

Ar trebui să fi primit o copie a licenței Creative Commons Attribution-ShareAlike 4.0 International împreună cu această lucrare. Dacă nu, vizitați <https://creativecommons.org/licenses/by-sa/4.0/>
