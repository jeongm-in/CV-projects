import cv2, numpy, time, sys, math
import directory


def create_blob_detector_object():
    params = cv2.SimpleBlobDetector_Params()
    # Parameters are as follows
    params.filterByArea = True
    params.minArea = 400
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
ROI_drawn = cv2.rectangle(src_img, (ix, iy), (ix + w, iy + h), (0, 255, 127), 2)
cv2.imwrite(directory + 'ROI_marked.jpg', ROI_drawn)

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
frame_number = -1
failed_frames = 0
first_ROI = True  # Flag to record radius of cell in first frame
radii = []

# Loop through all frames of video
font = cv2.FONT_HERSHEY_SIMPLEX

while True:
    read_success, frame = capture_video.read()
    frame_number += 1

    if not read_success:
        break

    ROI = frame[iy:iy + h, ix:ix + w]
    grayscale = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grayscale, (11, 11), 0)
    th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                               cv2.THRESH_BINARY, 35, 2)

    detected_img, detected_kp = feature_detector(parameters, th)

    if first_ROI:
        first_ROI = False
        k = cv2.waitKey(0) & 0xFF
        numkp = cv2.KeyPoint_convert(detected_kp)
        detected_cell_number = len(numkp)
        for i in range(detected_cell_number):
            label = '#' + str(i)
            point = (numkp[i][0], numkp[i][1])
            R_point = (int(numkp[i][0] + ix), int(numkp[i][1] + iy))
            cv2.putText(detected_img, label, point, font, 0.5, (64, 255, 127), 1, cv2.LINE_AA)
            cv2.putText(ROI_drawn, label, R_point, font, 1, (0, 0, 0), 2, cv2.LINE_AA)

        cv2.namedWindow('Detected')
        cv2.resizeWindow('Detected', 200, 960)
        cv2.imshow('Detected', detected_img)
        cv2.waitKey(0)
        cv2.imwrite(directory + str(frame_number) + '.jpg', detected_img)
        cv2.imwrite(directory + 'ROI_marked.jpg', ROI_drawn)

        print('Found ' + str(detected_cell_number) + ' cells in first frame. Press ESC to abort.')

        if k == 27:
            sys.exit()
        else:
            time_begin = time.time()
            coord = numpy.zeros((400, detected_cell_number, 2))
            prev = numpy.zeros((detected_cell_number, 2))
            now = numpy.zeros((detected_cell_number, 2))
            errors = [0] * detected_cell_number

            if detected_cell_number > 0:
                coord[0] = numkp
                for i, v in enumerate(detected_kp):
                    radii.append(round(v.size / 5, 3))

        continue

    cell_count = len(cv2.KeyPoint_convert(detected_kp))
    if cell_count < detected_cell_number:
        print('Feature detection error in ' + str(frame_number) + ' frame!')
        if frame_number < 11:
            print('Feature detection error before first 11 frames. Terminating script')
            sys.exit()

        now = cv2.KeyPoint_convert(detected_kp)
        prev = coord[frame_number - 1]
        trend = [1] * detected_cell_number
        temp = [0] * detected_cell_number
        for t in range(detected_cell_number):
            slope = (coord[frame_number - 1][t][1] - coord[frame_number - 11][t][1]) / \
                    (coord[frame_number - 1][t][0] - coord[frame_number - 11][t][0])
            if slope < 0:
                trend[t] = -1

        for i, a in enumerate(prev):
            min_comp = [100000000, 0, -10000000]
            for j, b in enumerate(now):
                diff = math.sqrt(
                    (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]))

                if diff < min_comp[0]:
                    min_comp[0] = diff
                    min_comp[1] = j
                    min_comp[2] = b

            coord[frame_number][i] = min_comp[2]
            temp[i] = min_comp[0]

        for i in range(detected_cell_number - cell_count):
            invalid_I = numpy.argmax(temp)
            temp[invalid_I] = -1
            errors[invalid_I] += 1
            coord[frame_number][invalid_I][0] = prev[invalid_I][0] + trend[invalid_I]
            coord[frame_number][invalid_I][1] = prev[invalid_I][1] + trend[invalid_I]


    else:
        now = cv2.KeyPoint_convert(detected_kp)
        prev = coord[frame_number - 1]

        # Brute force difference calculation
        for i, a in enumerate(prev):
            min_comp = [100000000, 0, -10000000]
            for j, b in enumerate(now):
                diff = math.sqrt(
                    (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]))

                if diff < min_comp[0]:
                    min_comp[0] = diff
                    min_comp[1] = j
                    min_comp[2] = b

            # if min_comp[0] > 4:
            #     coord[frame_number][min_comp[1]][0] = prev[i][0]
            #     coord[frame_number][min_comp[1]][1] = prev[i][1]
            #
            # else:
            coord[frame_number][i] = min_comp[2]

    for i in range(detected_cell_number):
        label = '#' + str(i)
        point = (int(coord[frame_number][i][0]), int(coord[frame_number][i][1]))
        cv2.putText(detected_img, label, point, font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    cv2.imshow('Detected', detected_img)
    cv2.imwrite(directory + str(frame_number) + '.jpg', detected_img)

    cv2.waitKey(5) & 0xFF

# End of loop
cv2.destroyAllWindows()
time_end = time.time()

# Calculate Crossover frequency
frequency_range = numpy.linspace(10000, 35000, frame_number)
frequencies = []
print('\n' + str(detected_cell_number) + ' cells detected. ')

# Print results
f = open(directory + 'result.txt', 'w')
for i in range(detected_cell_number):
    maxI = numpy.argmax(coord[:, i, 0])
    freq_crossover = int(frequency_range[maxI])
    frequencies.append(freq_crossover)
    statement = ('Cell # ' + str(i) + '\n') + ('Radius : ' + str(radii[i]) + ' um\n') + \
                ('Crossover frequency : ' + str(freq_crossover) + ' kHz\n') + \
                ('Total ' + str(errors[i]) + ' approximations were made.\n\n')
    f.write(statement)
    print(statement)

f.close()

# Debug area for coordinate recording
# f = open(directory + 'debug.txt', 'w')
# bbb = 1
# for line in coord[:, i, 0]:
#     f.write(str(bbb) + ' ' + str(line) + '\n')
#     bbb += 1
#
# f.close()

time_elapsed = time_end - time_begin
print('Script completed in ' + str(round(time_elapsed, 4)) + ' seconds.', end='\n')
