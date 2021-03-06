# Jeong-Min Lim (limjeongmin@wustl.edu)
# https://github.com/jeongm/CV-projects
# Python 3.6.5, OpenCV 3.4.0, and PyQt 5.10.1
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QAction,
                             QApplication, QLabel, QFileDialog, QMessageBox,
                             QMainWindow, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from math import sqrt
from random import randrange
import sys, cv2, numpy, openpyxl, time


class MainFrame(QMainWindow):

    def __init__(self, rad, cord, err):
        super().__init__()
        self.radii = rad
        self.coord = cord
        self.errors = err
        self.initUI()

    def initUI(self):
        # Define button to begin detection
        self.roi_button = QPushButton('Select ROI', self)
        self.roi_button.clicked.connect(self.select_roi)
        self.roi_button.setGeometry(290, 40, 130, 35)
        self.roi_button.setStatusTip('Select ROI')

        self.detect_button = QPushButton('Begin Detect', self)
        # self.begin_detect.clicked.connect(self.run_detect)
        self.detect_button.clicked.connect(self.begin_detect)
        self.detect_button.setGeometry(290, 85, 130, 35)
        self.detect_button.setStatusTip('Begin Detection')

        # Define ListWidget to show system messages
        self.text_console = QListWidget(self)
        self.text_console.setGeometry(20, 160, 400, 280)
        self.text_console.setStatusTip('This console will display system messages.')

        # Define ListWidget to display results
        self.result_console = QListWidget(self)
        self.result_console.setGeometry(440, 40, 400, 400)
        self.result_console.setStatusTip('This console will display the result.')

        # Define label to show first frame image
        self.first_frame = QLabel(self)
        self.first_frame.move(860, 40)
        self.first_frame.setStatusTip('This is the first frame of the video with labels.')

        # Define file open dialog
        openFile = QAction(QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        # Define clear window
        clear_window = QAction(QIcon('web.png'), 'Clear', self)
        clear_window.setShortcut('Ctrl+R')
        clear_window.setStatusTip('Clear program')
        clear_window.triggered.connect(self.clearWindow)

        # Define toggle adaptive threshold
        self.adaptive_check = QAction('Adaptive Threshold', self, checkable=True)
        self.adaptive_check.setStatusTip('Toggle to enable adaptive threshold.')
        self.adaptive_check.triggered.connect(self.adaptive_on)

        # Define menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(clear_window)
        fileMenu.addAction(self.adaptive_check)

        # Define display for ROI coordinates
        self.roi_values = QLineEdit(self)
        self.roi_values.setGeometry(20, 130, 180, 25)
        self.roi_values.setPlaceholderText('ROI coordinates')
        self.roi_values.setAlignment(Qt.AlignCenter)
        self.roi_values.setStatusTip('This is the dimension of ROI.')

        # Define display for detected cell count
        self.detect_count = QLineEdit(self)
        self.detect_count.setGeometry(240, 130, 180, 25)
        self.detect_count.setPlaceholderText('Detected Count')
        self.detect_count.setAlignment(Qt.AlignCenter)
        self.detect_count.setStatusTip('This is the number of cells detected in the ROI in the first frame.')

        # Define labels to show units and values
        unit1, unit2, unit3 = QLabel(self), QLabel(self), QLabel(self)
        name1, name2, name3 = QLabel(self), QLabel(self), QLabel(self)
        self.source_video = QLabel(self)
        self.source_video.setText('Source Video Directory')
        self.source_video.setGeometry(20, 450, 400, 25)
        unit1.setText('Hz')
        unit1.move(230, 35)
        unit2.setText('Hz')
        unit2.move(230, 65)
        unit3.setText('pixel')
        unit3.move(230, 95)
        name1.setText('Initial Frequency')
        name1.setGeometry(20, 35, 120, 25)
        name2.setText('Final Frequency')
        name2.setGeometry(20, 65, 120, 25)
        name3.setText('Px to 10um scale')
        name3.setGeometry(20, 95, 120, 25)

        # Define parameter displays
        # Define initial frequency. Default value is 10000 (Hz)
        self.init_fq = QLineEdit(self)
        self.init_fq.setGeometry(146, 40, 75, 24)
        self.init_fq.setAlignment(Qt.AlignRight)
        self.init_fq.setText('10000')
        self.init_fq.setStatusTip('This is the initial frequency of the alternating current on cells.')

        # Define final frequency. Default value is 35000 (Hz)
        self.fin_freq = QLineEdit(self)
        self.fin_freq.setGeometry(146, 70, 75, 24)
        self.fin_freq.setAlignment(Qt.AlignRight)
        self.fin_freq.setText('35000')
        self.fin_freq.setStatusTip('This is the final frequency of the alternating current on cells.')

        # Define scale. Default value is 25 (pixel to 1 um)
        self.scale = QLineEdit(self)
        self.scale.setGeometry(146, 100, 75, 24)
        self.scale.setAlignment(Qt.AlignRight)
        self.scale.setText('25')
        self.scale.setStatusTip('This is the scale of the video.')

        # Define size of main window
        self.setGeometry(200, 250, 1200, 520)
        self.setWindowTitle('Cell Track')
        self.statusBar()
        self.show()

    # Function to open source video
    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.source_video.setText(fname[0])
        QListWidgetItem('{0} loaded!'.format(fname[0]), self.text_console)

    # Function to select ROI for cell detection
    def select_roi(self):
        # Read first frame from the source video
        directory = self.source_video.text()
        read = cv2.VideoCapture(directory)
        read_successful, src_img = read.read()
        read.release()

        # Prevent program accessing wrong source
        if not read_successful or type(src_img) is None:
            error_message = 'Invalid source video directory detected..'
            QListWidgetItem(error_message, self.text_console)
            return

        cv2.namedWindow('Select ROI', 0)
        cv2.moveWindow('Select ROI', 1100, 250)
        cv2.resizeWindow('Select ROI', 768, 576)
        r = cv2.selectROI('Select ROI', src_img)
        ix, iy, w, h = r
        cv2.destroyAllWindows()

        # Original image
        ROI_drawn = cv2.rectangle(src_img, (ix, iy), (ix + w, iy + h), (0, 255, 0), 2)

        bd = self.define_detector_parameters()

        cut = src_img[iy:iy + h, ix:ix + w]
        detected_img, detected_kp = self.detect_feature(cut, bd)

        numkp = cv2.KeyPoint_convert(detected_kp)
        detected_cell_number = len(numkp)

        # save values to GUI displays
        self.roi_values.setText('{0} {1} {2} {3}'.format(ix, iy, w, h))
        self.detect_count.setText(str(detected_cell_number))

        # Draw labels on the ROI image
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(detected_cell_number):
            label = str(i)
            point = (numkp[i][0], numkp[i][1])
            R_point = (int(numkp[i][0] + ix), int(numkp[i][1] + iy))
            cv2.putText(detected_img, label, point, font, 1.5, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(ROI_drawn, label, R_point, font, 2, (0, 0, 0), 2, cv2.LINE_AA)

        self.coord = numpy.resize(self.coord, (400, detected_cell_number, 2))
        self.errors = self.errors * detected_cell_number

        if detected_cell_number > 0:
            self.coord[0] = numkp
            for i, v in enumerate(detected_kp):
                self.radii.append(v.size * 5 / int(self.scale.text()))

        # Show image within the GUI
        image_height, image_width, image_depth = detected_img.shape
        Qimg = cv2.cvtColor(detected_img, cv2.COLOR_BGR2RGB)
        Qimg = QImage(Qimg.data, image_width, image_height, image_width * image_depth, QImage.Format_RGB888)
        convertFrame = QPixmap.fromImage(Qimg)
        self.first_frame.setFixedSize(image_width, image_height)
        self.first_frame.setPixmap(convertFrame)
        QListWidgetItem('ROI image with labels saved!', self.text_console)
        cv2.imwrite('Original_ROI.jpg', ROI_drawn)

    # Function to detect cells in ROI of video.
    def begin_detect(self):
        directory = self.source_video.text()
        read = cv2.VideoCapture(directory)
        read_successful, src_img = read.read()
        read.release()

        # Prevent program accessing wrong source
        if not read_successful or type(src_img) is None or self.roi_values.text() == '':
            error_message = 'Select ROI first..'
            QListWidgetItem(error_message, self.text_console)
            return

        QListWidgetItem('Begin cell detection!', self.text_console)
        ix, iy, w, h = [int(s) for s in self.roi_values.text().split()]
        cv2.namedWindow('ROI')
        cv2.moveWindow('ROI', ix + w + 800, 290)

        capture_video = cv2.VideoCapture(directory)
        frame_number, failed_frames = 0, 0
        b_detector = self.define_detector_parameters()
        detected_cell_number = int(self.detect_count.text())
        prev = numpy.zeros((detected_cell_number, 2))
        now = numpy.zeros((detected_cell_number, 2))

        time_b = time.time()

        while True:
            read_successful, frame = capture_video.read()
            frame_number += 1

            # Break loop when video reaches final frame
            if not read_successful:
                break

            ROI = frame[iy:iy + h, ix:ix + w]
            detected_ROI, detected_kp = self.detect_feature(ROI, b_detector)

            cell_count = len(cv2.KeyPoint_convert(detected_kp))
            now = cv2.KeyPoint_convert(detected_kp)
            prev = self.coord[frame_number - 1]

            # If cells escape ROI, assume the cells were moving to the left.
            if cell_count < detected_cell_number:
                error_message = 'Feature detection error in frame {0}'.format(frame_number)
                QListWidgetItem(error_message, self.text_console)
                temp = [0] * detected_cell_number

                for i, a in enumerate(prev):
                    min_comp = [100000000, 0, -10000000]
                    for j, b in enumerate(now):
                        diff = sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
                        if diff < min_comp[0]:
                            min_comp = [diff, j, b]
                    self.coord[frame_number][i] = min_comp[2]
                    temp[i] = min_comp[0]

                for i in range(detected_cell_number - cell_count):
                    invalid_I = numpy.argmax(temp)
                    temp[invalid_I] = -1
                    self.errors[invalid_I] += 1
                    self.coord[frame_number][invalid_I][0] = prev[invalid_I][0] - 1 / 2
                    self.coord[frame_number][invalid_I][1] = prev[invalid_I][1] + randrange(-1, 1) / 2

            else:
                for i, a in enumerate(prev):
                    min_comp = [100000000, 0, -10000000]
                    for j, b in enumerate(now):
                        diff = sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
                        if diff < min_comp[0]:
                            min_comp = [diff, j, b]

                    self.coord[frame_number][i] = min_comp[2]

            # Draw labels on cells in ROI
            for i in range(detected_cell_number):
                label = str(i)
                point = (int(self.coord[frame_number][i][0]), int(self.coord[frame_number][i][1]))
                cv2.putText(detected_ROI, label, point, cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2, cv2.LINE_AA)

            cv2.imshow('ROI', detected_ROI)
            cv2.waitKey(20)

        cv2.destroyAllWindows()
        time_e = time.time()

        # Return results
        freq_b = int(self.init_fq.text())
        freq_e = int(self.fin_freq.text())
        frequency_range = numpy.linspace(freq_b, freq_e, frame_number)
        frequencies = []
        time_total = time_e - time_b

        # Write result to excel file
        book = openpyxl.Workbook()
        sheet = book.active
        sheet.title = 'Frequency and Radius'
        sheet.cell(2, 1).value = 'Radius (um)'
        sheet.cell(3, 1).value = 'Frequency (Hz)'

        for f_i in range(2, detected_cell_number + 2):
            i = f_i - 2
            sheet.cell(row=1, column=f_i).value = 'Cell {0}'.format(i)
            maxI = numpy.argmax(self.coord[:, i, 0])
            freq_crossover = frequency_range[maxI]
            frequencies.append(freq_crossover)
            statement = 'Cell # {0}\nRadius : {1:.3f} um\nCrossover frequency : {2:.0f} Hz' \
                        '\nTotal {3} approximations were made.\n' \
                .format(i, self.radii[i], freq_crossover, self.errors[i])
            sheet.cell(row=2, column=f_i).value = round(self.radii[i],3)
            sheet.cell(row=3, column=f_i).value = round(freq_crossover,3)

            QListWidgetItem(statement, self.result_console)

        QListWidgetItem('Total process run in {0:.3f} seconds!'.format(time_total), self.text_console)
        QListWidgetItem('Result saved to Cell_Frequency_Radius.xlsx!', self.text_console)

        book.save('Cell_Frequency_Radius.xlsx')
        return

    # Define simbleBlobDetector Object
    def define_detector_parameters(self):
        params = cv2.SimpleBlobDetector_Params()

        params.filterByArea = True
        params.minArea = 800
        params.maxArea = 3300

        params.filterByCircularity = True
        params.minCircularity = 0.01

        params.filterByConvexity = True
        params.minConvexity = 0.00001

        params.filterByColor = False
        params.filterByInertia = False
        blob_detector = cv2.SimpleBlobDetector_create(params)
        return blob_detector

    # Find keypoints with simpleBlobDetector
    def detect_feature(self, frame, detector):
        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(grayscale, (11, 11), 0)
        if self.adaptive_check.isChecked():
            th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                       cv2.THRESH_BINARY, 65, 2)
        else:
            th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        keypoints = detector.detect(th)
        img_with_keypoints = cv2.drawKeypoints(th, keypoints, numpy.array([]), (0, 255, 0),
                                               cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        return img_with_keypoints, keypoints

    def clearWindow(self):
        self.text_console.clear()
        self.result_console.clear()
        self.roi_values.clear()
        self.detect_count.clear()
        self.first_frame.clear()
        self.source_video.setText('Source Video Directory')
        cv2.destroyAllWindows()

    def closeEvent(self, event):
        cv2.destroyAllWindows()

        reply = QMessageBox.question(self, 'Message',
                                     "Do you really want to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            cv2.destroyAllWindows()
            cv2.destroyWindow('Select ROI')
            event.accept()
        else:
            event.ignore()

    def adaptive_on(self,state):
        if state:
            QListWidgetItem('Adaptive threshold enabled!', self.text_console)
        else:
            QListWidgetItem('Adaptive threshold disabled!', self.text_console)


if __name__ == '__main__':
    radius = []
    coordinate = numpy.zeros((1, 1, 1))
    error = [0]
    app = QApplication(sys.argv)
    ex = MainFrame(radius, coordinate, error)
    sys.exit(app.exec_())
