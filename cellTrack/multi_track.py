import cv2, numpy, time, sys
import directory


def create_blob_detector_object():
    params = cv2.SimpleBlobDetector_Params()
    # Parameters are as follows
    params.filterByArea = True
    params.minArea = 600
    params.maxArea = 4000

    params.filterByCircularity = True
    params.minCircularity = 0.01

    params.filterByConvexity = True
    params.minConvexity = 0.000000001

    params.filterByColor = False
    params.filterByInertia = False

    new_blob_detector = cv2.SimpleBlobDetector_create(params)
    return new_blob_detector


def feature_detector(detector_object, img):
    """
    blob_detector detects blobs in binary image
    :param detector_object: parameter object
    :param img: input (binary) image for blob detection
    :return: ROI image with keypoint drawn and corresponding keypoint object
    """
    keypoints = detector_object.detect(th)
    img_with_keypoints = cv2.drawKeypoints(th, keypoints, numpy.array([]), (0, 0, 255),
                                           cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return img_with_keypoints, keypoints


# Ask user to choose whether to show frame or save frame.
# Both actions add up to processing time
run = input('Type name of directory to save files: ')

# String concatenations for directories
source_video = directory.svideo
directory = directory.fdirectory

# Read first frame
read = cv2.VideoCapture(source_video)
ret, src_img = read.read()
read.release()

# ROI selection
cv2.namedWindow('Select ROI', 0)
cv2.resizeWindow('Select ROI', 640, 480)  # Change the size of the window for ROI selection
r = cv2.selectROI('Select ROI', src_img)
cv2.waitKey(0) & 0xFF
cv2.destroyAllWindows()

# ROI region from ROI selection
ix, iy, w, h = r
ROI_drawn = cv2.rectangle(src_img, (ix, iy), (ix + w, iy + h), (0, 255, 0), 2)
cv2.imwrite(directory + run + 'ROI_marked.jpg', ROI_drawn)

# Show first ROI region
cv2.namedWindow('ROI', 0)
cv2.resizeWindow('ROI', 640, 480)
cv2.imshow('ROI', ROI_drawn)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Measure radii of cells from first frame
parameters = create_blob_detector_object()

# Record frame by frame from source video
capture_video = cv2.VideoCapture(source_video)
frame_number = 0
failed_frames = 0
first_ROI = True  # Flag to record radius of cell in first frame
radii = []

# Loop through all frames of video
cv2.namedWindow('Detected')
cv2.resizeWindow('Detected', 200, 960)
while True:
    frame_number += 1
    read_success, frame = capture_video.read()
    if not read_success:
        break

    ROI = frame[iy:iy + h, ix:ix + w]
    grayscale = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grayscale, (11, 11), 0)
    th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                               cv2.THRESH_BINARY, 45, 2)

    detected_img, detected_kp = feature_detector(parameters, th)
    cv2.imshow('Detected', detected_img)
    if first_ROI:
        first_ROI = False
        k = cv2.waitKey(0) & 0xFF
        if k == 27:
            sys.exit()
        else:
            numkp = cv2.KeyPoint_convert(detected_kp)
            detected_cell_number = len(numkp)
            coord = numpy.zeros((400, detected_cell_number + 1))
            if detected_cell_number > 0:
                for i in detected_kp:
                    radii.append(round(i.size / 5, 3))
            time_begin = time.time()

    if len(cv2.KeyPoint_convert(detected_kp)) != detected_cell_number:
        print('Feature detection error in ' + str(frame_number) + ' frame!')
    else:
        for i, v in enumerate(cv2.KeyPoint_convert(detected_kp)):
            coord[frame_number - 1][i] = v[0]

    cv2.waitKey(5) & 0xFF

cv2.destroyAllWindows()
time_end = time.time()

frequency_range = numpy.linspace(10000, 35000, frame_number)
frequencies = []

# Calculate Crossover frequency
print('\n' + str(detected_cell_number) + ' cells detected. ')

# Print results
for i in range(detected_cell_number):
    maxI = numpy.argmax(coord[:, i])
    freq_crossover = round(frequency_range[maxI])
    frequencies.append(freq_crossover)

    print('Cell # ' + str(i + 1))
    print('Radius : ' + str(radii[i]) + ' um')
    print('Crossover frequency : ' + str(freq_crossover) + ' kHz.')

# Write radius and frequency to file
f = open(directory + run + '_radii_frequencies.txt', 'w')
result = numpy.vstack((radii, frequencies))
f.write(str(result))
f.close()

time_elapsed = time_end - time_begin
print('\nScript completed in ' + str(round(time_elapsed, 4)) + ' seconds.', end='\n')
