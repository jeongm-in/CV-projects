# Cell Track
## Dielectrophoretic Force
Dielectrophoresis is the movement of particles within the asymmetric electric fields.

When cells are suspended in a medium with alternating electric fields, they will recieve dielectrophoretic(DEP) force according to the frequency and the conductivity of the suspending medium. 

If the conductivity of the suspending medium is low enough, at lower frequencies the cells will receive negative DEP force that repels cells from the high field region.  

The size of DEP force decreases as frequency increases, and at a certain frequency the value of DEP force becomes zero. This frequency is "Crossover Frequency."

After this "Crossover Frequency," the cell will now receive positive DEP force that attracts cells to the high field region.

Because different cells have different DEP crossover frequency, this value could be used to identify cells.

## Goal
In this experiment, the high field region is the region with optical rays, and the frequency increases from 10 kHz to 35 kHz with uniform increment.
The goal of this project was to find the "Crossover Frequency" of each cells to solve below equation.<sup>2</sup>

![equation](https://raw.githubusercontent.com/jeongm/CV-projects/master/cellTrack/sample/equation.png)  
![c_memb](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/cmemb.png?raw=true) 

![sigma](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/sigma.png?raw=true)

![r](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/r.png?raw=true)  

![f](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/f.png?raw=true)

## Method
1. Prompt user to select region of interest (ROI) from the first frame of the source video.<sup>1</sup>
![ROI](https://github.com/jeongm/CV-projects/blob/master/cellTrack/sample/Original_ROI.jpg?raw=true)
2. For each frame in the video, slice out only the ROI and process the image.
  - Convert to grayscale - denoise - binarize
3. Use OpenCV's simpleBlobDetector to find meaningful "blobs" within the ROI.
4. Record radius of cells from first frame, record coordinate of the detected cells in every frame.
5. After processing the whole video, find frequency at each frame using below code
> frequency_range = numpy.linspace(initial_frequency, final_frequency, total_number_of_frames)
6. Find crossover frequency, which is the frequency of the maximum value of cells' x-coordinate value.
> max_value_index = numpy.argmax(cells_x_coordinates[:])
> crossover_frequency  = frequency_range[max_val

## Issues in multiple cell detection


# Cell Track GUI
![title](https://raw.githubusercontent.com/jeongm/CV-projects/master/cellTrack/sample/GUI_sample.jpg)

This is the GUI version of the python script to track cells.

This program aims to find the crossover frequency and the radius of cells to provide data for rapid identification of cells.

After successful execution, the program will save the image of ROI with labels and record results to Microsoft excel file.

Built with Python 3.6.5, OpenCV 3.4.0, and PyQt 5.10.1

---
<sup>1</sup> Courtesy of Yanbin Lin, Shanghai University Nanoscale Controls Laboratory

<sup>2</sup> Gascoyne PRC, Shim S. Isolation of Circulating Tumor Cells by Dielectrophoresis. Cancers. 2014;6(1):545-579. doi:10.3390/cancers6010545.
