import cv2, numpy, os, time, sys
import directory


# Function Definitions
def create_blob_detector_object():
    """
    set_params() defines parameter with different values for blob detection.
    Change parameters according to expected and required object dimension.
    Since one cell exists in one ROI, below parameters are by default set loosely to match any object.
    :return: parameter for cv2.SimpleBlobDetector()
    """
    params = cv2.SimpleBlobDetector_Params()

    # Parameters are as follows
    params.filterByArea = True
    params.minArea = 300
    params.maxArea = 4000

    params.filterByCircularity = True
    params.minCircularity = 0.001

    params.filterByConvexity = True
    params.minConvexity = 0.001

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
    keypoints = detector_object.detect(img)
    img_with_keypoints = cv2.drawKeypoints(img, keypoints, numpy.array([]), (0, 0, 255),
                                           cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return img_with_keypoints, keypoints


# Ask user to choose whether to visualize images during whole process
show_frames = input('Show image files?: ( y / n ) ')
save_frames = input('Save frame by frame cuts?: ( y / n ) ')

show_frame, save_frame = show_frames == 'y', save_frames == 'y'

# Edit directory of files to begin processing.
# Change value of variable 'run' to save to different directory
run = input('Type name of directory to save files: ')
source_video = directory.svideo
directory = directory.fdirectory
extension = '.jpg'
final_directory = directory + str(run) + '/'

if not os.path.exists(final_directory):
    os.makedirs(final_directory)

# Read first frame of input video and select Region of Interest (ROI)
read = cv2.VideoCapture(source_video)
ret, src_img = read.read()
read.release()

cv2.namedWindow('Select ROI', 0)
cv2.resizeWindow('Select ROI', 640, 480)  # Change the size of the window for ROI selection
r = cv2.selectROI('Select ROI', src_img)
cv2.waitKey(0) & 0xFF
cv2.destroyAllWindows()

ix, iy, w, h = r
ROI_drawn = cv2.rectangle(src_img, (ix, iy), (ix + w, iy + h), (0, 255, 0), 2)
cv2.imwrite(final_directory + 'ROI_marked.jpg', ROI_drawn)

if show_frame:
    cv2.namedWindow('ROI', 0)
    cv2.resizeWindow('ROI', 640, 480)
    cv2.imshow('ROI', ROI_drawn)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Record frame by frame from source video
capture_video = cv2.VideoCapture(source_video)
frame_number = 0
failed_frames = 0
first_ROI = True  # Flag to record radius of cell in first frame
cell_coordinates = []
time_begin = time.time()
cv2.namedWindow('Binary Image', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('Feature', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow('Binary Image', 100, 100)
cv2.moveWindow('Feature', 400, 100)

print('Processing', end='')
parameters = create_blob_detector_object()
while True:
    frame_number += 1
    if frame_number % 20 == 0:
        print('.', end='')

    read_success, frame = capture_video.read()
    if not read_success:
        break

    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ROI = grayscale[iy:iy + h, ix:ix + w]

    # Decrease noise from cropped ROI image using Gaussian Blur
    blur = cv2.GaussianBlur(ROI, (5, 5), 0)  # Param: source, kernel_size,

    # Change image to binary image using Otsu's method
    return_value, binary_image = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if show_frame:
        cv2.imshow('Binary Image', binary_image)

    # Begin feature detection and record location
    detected_image, kp = feature_detector(detector_object=parameters, img=binary_image)
    keypoint_list = cv2.KeyPoint_convert(kp)

    if len(keypoint_list) != 1:
        failed_frames += 1

    try:
        cell_coordinates.append(list(keypoint_list)[0][0])
    except IndexError as e:
        print('\nFailed to detect feature in ' + str(frame_number) + 'th frame!')
        print('Select different ROI. Script terminated.')
        sys.exit()

    if first_ROI:
        first_ROI = False
        cell_diameter = kp[0].size
        cell_rad = round(cell_diameter / 5, 3)

    if show_frame:
        cv2.imshow('Feature', detected_image)
        cv2.waitKey(40) & 0xFF
    if save_frame:
        if frame_number < 10:
            file_number = '00' + str(frame_number)
        elif 10 <= frame_number < 100:
            file_number = '0' + str(frame_number)
        else:
            file_number = str(frame_number)
        file_name = final_directory + file_number + extension
        cv2.imwrite(file_name, detected_image)

cv2.destroyAllWindows()

# Define result variables
number_of_frames = len(cell_coordinates)

# Measure time elapsed to run the script
time_end = time.time()
time_elapsed = time_end - time_begin

# Print results
print('\nScript completed in ' + str(round(time_elapsed, 4)) + ' seconds.', end='\n')
print('Failed to detect ' + str(failed_frames) + ' frames out of ' + str(number_of_frames) + ' frames!\n')

if not failed_frames:
    frequencies = numpy.linspace(10000, 35000, number_of_frames)
    turning_point_fq = round(frequencies[numpy.argmax(cell_coordinates)], None) * 0.001

    print('* Cell radius measured from first frame is ' + str(cell_rad) + ' um.')
    print('* Frequency at turning point is ' + format(turning_point_fq, '.3f') + ' kHz.')

    # Write to text file
    f = open(directory + str(run) + '_coordinates.txt', 'w')
    for line in cell_coordinates:
        f.write(str(line) + '\n')
    f.write(str(turning_point_fq) + '\n')
    f.write(str(cell_rad))
    f.close()
