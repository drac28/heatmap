import numpy as np
import cv2
import copy
from tqdm import tqdm
import os
import json
import standard

def count_frames(path, cache):
    if "frames" in cache:
        return cache["frames"]
    (major, minor, _) = cv2.__version__.split(".")
    video = cv2.VideoCapture(path)
    total = 0
    try:
        if major == "3":
            total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        elif major == "2":
            total = int(video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        else:
            raise Exception
    except:
        while True:
            try:
                (grabbed, frame) = video.read()
                if not grabbed:
                    break
                total += 1
            except KeyboardInterrupt:
                break
    print(total, "frames in total")
    cache["frames"] = total
    json.dump(cache, open(".cache", "w"))
    return total

def main():
    print("OpenCV Version:", cv2.__version__)
    if os.path.isfile(".cache"):
        cache = json.load(open(".cache"))
    else:
        cache = {"file": ""}
    path = input("Path to Videofile: ")
    if path != cache["file"]:
        cache = {}
    cache["file"] = path
    cap = cv2.VideoCapture(path)
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

    all_frames = count_frames(path, cache)
    divider = standard.input_int("All Frames divided by: ")
    frames = int(all_frames / divider)

    first_iteration_indicator = 1
    for i in tqdm(range(0, frames)):
        '''
        There are some important reasons this if statement exists:
            -in the first run there is no previous frame, so this accounts for that
            -the first frame is saved to be used for the overlay after the accumulation has occurred
            -the height and width of the video are used to create an empty image for accumulation (accum_image)
        '''
        if (first_iteration_indicator == 1):
            ret, frame = cap.read()
            first_frame = copy.deepcopy(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape[:2]
            accum_image = np.zeros((height, width), np.uint8)
            first_iteration_indicator = 0
        else:
            ret, frame = cap.read()  # read a frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to grayscale

            fgmask = fgbg.apply(gray)  # remove the background

            # for testing purposes, show the result of the background subtraction
            # cv2.imshow('diff-bkgnd-frame', fgmask)

            # apply a binary threshold only keeping pixels above thresh and setting the result to maxValue.  If you want
            # motion to be picked up more, increase the value of maxValue.  To pick up the least amount of motion over time, set maxValue = 1
            thresh = 2
            maxValue = 2 * divider
            ret, th1 = cv2.threshold(fgmask, thresh, maxValue, cv2.THRESH_BINARY)
            # for testing purposes, show the threshold image
            # cv2.imwrite('diff-th1.jpg', th1)

            # add to the accumulated image
            accum_image = cv2.add(accum_image, th1)
            # for testing purposes, show the accumulated image
            # cv2.imwrite('diff-accum.jpg', accum_image)

            # for testing purposes, control frame by frame
            # raw_input("press any key to continue")

        # for testing purposes, show the current frame
        # cv2.imshow('frame', gray)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
         
        for i in range(1, divider):
            cap.read()

    # apply a color map
    # COLORMAP_PINK also works well, COLORMAP_BONE is acceptable if the background is dark
    color_image = im_color = cv2.applyColorMap(accum_image, cv2.COLORMAP_HOT)
    # for testing purposes, show the colorMap image
    # cv2.imwrite('diff-color.jpg', color_image)

    # overlay the color mapped image to the first frame
    result_overlay = cv2.addWeighted(first_frame, 0.7, color_image, 0.7, 0)

    # save the final overlay image
    cv2.imwrite('diff-overlay.jpg', result_overlay)

    # cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("User sent exit signal.\nBye")