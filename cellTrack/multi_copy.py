import cv2, numpy, time, sys, math
import preset


def create_blob_detector_object():
    params = cv2.SimpleBlobDetector_Params()
    # Parameters are as follows
    params.filterByArea = True
    params.minArea = 800
    params.maxArea = 4000

    params.filterByCircularity = True
    params.minCircularity = 0.01

    params.filterByConvexity = False
    params.filterByColor = False
    params.filterByInertia = False

    new_blob_detector = cv2.SimpleBlobDetector_create(params)
    return new_blob_detector


def feature_detector(detector_object, img):
    keypoints = detector_object.detect(th)  # parameter object
    img_with_keypoints = cv2.drawKeypoints(th, keypoints, numpy.array([]), (0, 0, 255),
                                           cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return img_with_keypoints, keypoints


# Read directory from preset.py
src_video = preset.source_video
directory = preset.source_directory

# Read first frame from the video
read = cv2.VideoCapture(src_video)
ret, src_img = read.read()
read.release()

# Prompt user to select Region of Interest (ROI)
cv2.namedWindow('Select ROI', 0)
cv2.resizeWindow('Select ROI', 640, 480)
r = cv2.selectROI('Select ROI', src_img)
cv2.waitKey(0) & 0xFF
cv2.destroyAllWindows()

# ROI region data
ix, iy, w, h = r
ROI_drawn = cv2.rectangle(src_img, (ix, iy), (ix + w, iy + h), (0, 255, 0), 2)
cv2.imwrite(directory + 'ROI_marked.jpg', ROI_drawn)

# Show first frame with ROI marked
cv2.namedWindow('ROI', 0)
cv2.resizeWindow('ROI', 640, 480)
cv2.imshow('ROI', ROI_drawn)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Define variables for cell detection
parameters = create_blob_detector_object()
font = cv2.FONT_HERSHEY_PLAIN

# Open and read from source video
capture_video = cv2.VideoCapture(src_video)
frame_number, failed_frames, first_ROI = -1, 0, True
radii = []

# Loop through all frames of video
while True:
    read_success, frame = capture_video.read()
    frame_number += 1

    if not read_success:
        break

    ROI = frame[iy:iy + h, ix:ix + w]
    grayscale = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grayscale, (11, 11), 0)
    th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                               cv2.THRESH_BINARY, 65, 2)

    detected_img, detected_kp = feature_detector(parameters, th)

    if first_ROI:
        first_ROI = False
        k = cv2.waitKey(0) & 0xFF
        numkp = cv2.KeyPoint_convert(detected_kp)
        detected_cell_number = len(numkp)
        for i in range(detected_cell_number):
            label = str(i)
            point = (numkp[i][0], numkp[i][1])
            R_point = (int(numkp[i][0] + ix), int(numkp[i][1] + iy))
            cv2.putText(detected_img, label, point, font, 1, (100, 255, 100), 1, cv2.LINE_AA)
            cv2.putText(ROI_drawn, label, R_point, font, 2, (0, 0, 0), 2, cv2.LINE_AA)

        cv2.namedWindow('Detected')
        cv2.resizeWindow('Detected', 200, 960)
        cv2.imshow('Detected', detected_img)
        cv2.waitKey(0)
        cv2.imwrite(directory + str(frame_number) + '.jpg', detected_img)
        cv2.imwrite(directory + 'ROI_marked.jpg', ROI_drawn)

        print('Found {0} cells in first frame. Press ESC to abort.'.format(detected_cell_number))

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
        print('Feature detection error in {0} frame!'.format(frame_number))
        if frame_number < 21:
            print('Feature detection error before first 11 frames. Terminating script')
            sys.exit()

        now = cv2.KeyPoint_convert(detected_kp)
        prev = coord[frame_number - 1]
        trend = [1] * detected_cell_number
        temp = [0] * detected_cell_number
        for t in range(detected_cell_number):
            slope = (-coord[frame_number - 1][t][1] + coord[frame_number - 21][t][1]) / \
                    (coord[frame_number - 1][t][0] - coord[frame_number - 21][t][0])
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
            coord[frame_number][invalid_I][0] = prev[invalid_I][0] + trend[invalid_I] / 2
            coord[frame_number][invalid_I][1] = prev[invalid_I][1] + trend[invalid_I] / 2

    elif cell_count >= detected_cell_number:
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

            coord[frame_number][i] = min_comp[2]

    for i in range(detected_cell_number):
        label = '#' + str(i)
        point = (int(coord[frame_number][i][0]), int(coord[frame_number][i][1]))
        cv2.putText(detected_img, label, point, font, 1, (100, 255, 100), 1, cv2.LINE_AA)

    cv2.imshow('Detected', detected_img)
    cv2.imwrite(directory + str(frame_number) + '.jpg', detected_img)

    cv2.waitKey(5) & 0xFF

# End of loop
cv2.destroyAllWindows()
time_end = time.time()

# Calculate Crossover frequency
freq_b = preset.begin_freq
freq_e = preset.end_freq
frequency_range = numpy.linspace(freq_b, freq_e, frame_number)
frequencies = []
print('\n{0} cells detected.\n'.format(detected_cell_number))

# Print results
f = open(directory + 'result.txt', 'w')
for i in range(detected_cell_number):
    maxI = numpy.argmax(coord[:, i, 0])
    freq_crossover = int(frequency_range[maxI])
    frequencies.append(freq_crossover)
    statement = 'Cell # {0}\nRadius : {1} um\nCrossover frequency : {2} kHz' \
                '\nTotal {3} approximations were made.\n'.format(i, radii[i], freq_crossover, errors[i])
    f.write(statement)
    print(statement)

f.close()

time_elapsed = time_end - time_begin
print('Script completed in {0} seconds.'.format(round(time_elapsed, 4)))
