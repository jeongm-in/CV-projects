# Cell Track
## Dielectrophoretic Force
Dielectrophoresis is the movement of particles within the asymmetric electric fields.
When cells are suspended in a medium with alternating electric fields, they will recieve dielectrophoretic(DEP) force according to the frequency and the conductivity of the suspending medium. 
If the conductivity of the suspending medium is low enough, at lower frequencies the cells will receive negative DEP force that repels cells from the high field region.
The size of DEP force decreases as frequency increases, and at a certain frequency the value of DEP force becomes zero. This frequency is defined as "Crossover Frequency."
After this "Crossover Frequency," the cell will now receive positive DEP force that attracts cells to the high field region.
Because different cells have different DEP crossover frequency, this value could be used to identify cells.

## Goal
In this experiment, the high field region is the region with optical rays, and the frequency increases from 10 kHz to 35 kHz with uniform increment.
The goal of this project was to find the "Crossover Frequency" of each cells to solve below equation.<sup>1</sup>

![equation](https://raw.githubusercontent.com/jeongm/CV-projects/master/cellTrack/sample/equation.png)  
![c_memb](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/cmemb.png?raw=true) 

![sigma](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/sigma.png?raw=true)

![r](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/r.png?raw=true)  

![f](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/f.png?raw=true)

## Method
- Region of interest(ROI) is selected from the experimental video. 
- For each frame in the video, image is sliced out according to the dimension of ROI.
- The program will first convert the image into grayscale image and denoise using gaussian blur. 
- With OpenCV's simpleBlobDetector, the program will find any significant "blobs" detected within the frame.
- Radius of cells are determined in the first frame, and the coordinate of the center of detected cells will be recorded.
- After the program finishes processing whole video, the list of frequencies for each frame will be calculated using total number of frames.
> frequency_range = numpy.linspace(initial_frequency, final_frequency, total_number_of_frames)

# Cell Track GUI
![title](https://raw.githubusercontent.com/jeongm/CV-projects/master/cellTrack/sample/GUI_sample.jpg)

This is the GUI version of the python script to track cells.

This program aims to find the crossover frequency and the radius of cells to provide data for rapid identification of cells.

After successful execution, the program will save the image of ROI with labels and record results to Microsoft excel file.

Built with Python 3.6.5, OpenCV 3.4.0, and PyQt 5.10.1

---
<sup>1</sup> Gascoyne PRC, Shim S. Isolation of Circulating Tumor Cells by Dielectrophoresis. Cancers. 2014;6(1):545-579. doi:10.3390/cancers6010545.
