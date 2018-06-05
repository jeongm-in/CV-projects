# Cell Track
GUI program to detect cells movement based on python script files.
Cells are under uniformly increasing alternating current, receiving dielectrophoresis force (DEP force).
At certain frequency, the cells would change their direction of motion as DEP force becomes the net force.
With this crossover frequency and the radius of cell, below equation can be solved.[^1]
<center>![equation](https://latex.codecogs.com/png.latex?%5Clarge%20C_%7Bmembrane%7D%20%3D%20%5Cfrac%7B%5Csigma_%7Bs%7D%7D%7B%5Csqrt%7B2%7D%5Cpi%20R%20f%7D)</center>
![Cmemb](https://latex.codecogs.com/gif.latex?C_%7Bmembrane%7D%20%3A%20%5Ctextup%7BCell%5C%20membrane%5C%20Condcutance%7D)
![CapMed](https://latex.codecogs.com/gif.latex?%5Csigma_%7Bs%7D%20%3A%20%5Ctextup%7BCapacitance%20of%20Suspending%20Medium%7D)
![R](https://latex.codecogs.com/gif.latex?R%20%3A%20%5Ctextup%7BRadius%20of%20Cell%7D)
![f](https://latex.codecogs.com/gif.latex?f%20%3A%20%5Ctextup%7BCrossover%20Frequency%7D)

Because Capacitance of cell membrane is a unique property of cells, this value could be used for cell identifications, such as distinguishing cancer cells from normal cells.


# Cell Track GUI
This is the GUI version of the python script to track cells.

This program aims to find the crossover frequency and the radius of cells to provide data for rapid identification of cells.

Python 3.6.5, OpenCV 3.4.0, and PyQt 5.10.1

![title](https://raw.githubusercontent.com/jeongm/CV-projects/master/cellTrack/sample/GUI_sample.jpg)

---
[^1]:Gascoyne PRC, Shim S. Isolation of Circulating Tumor Cells by Dielectrophoresis. Cancers. 2014;6(1):545-579. doi:10.3390/cancers6010545.
