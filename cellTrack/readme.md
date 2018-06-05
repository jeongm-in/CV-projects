# Cell Track
GUI program to detect cells movement based on python script files.
Cells are under uniformly increasing alternating current, receiving dielectrophoresis force (DEP force).
At certain frequency, the cells would change their direction of motion as DEP force becomes the net force.
With this crossover frequency and the radius of cell, below equation can be solved.<sup>1</sup>
<center>![equation](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/equation.png?raw=true)</center>
![Cmemb](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/cmemb.png)
![CapMed](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/sigma.png)
![R](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/r.png?raw=true)
![f](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/f.png?raw=true)

Because Capacitance of cell membrane is a unique property of cells, this value could be used for cell identifications, such as distinguishing cancer cells from normal cells.


# Cell Track GUI
This is the GUI version of the python script to track cells.

This program aims to find the crossover frequency and the radius of cells to provide data for rapid identification of cells.

Python 3.6.5, OpenCV 3.4.0, and PyQt 5.10.1

![title](https://raw.githubusercontent.com/jeongm/CV-projects/master/cellTrack/sample/GUI_sample.jpg)

---
<sup>1</sup> Gascoyne PRC, Shim S. Isolation of Circulating Tumor Cells by Dielectrophoresis. Cancers. 2014;6(1):545-579. doi:10.3390/cancers6010545.
