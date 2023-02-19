import numpy as np
import cv2
import copy
import os
import standard
import json
from tqdm import tqdm
from multiprocessing import Process

def count_frames(origin, path):
    try:
        if os.path.exists(origin+"/.cache"):
            total = json.load(open(origin+"/.cache"))[path]
        else:
            raise Exception
    except:
        (major, minor, _) = cv2.__version__.split(".")
        video = cv2.VideoCapture(origin+"/"+path)
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
    return total

def main(origin, path, num, divider, level, frames=0):
    outpath = path+"_"+str(num)+".mp4"
    cap = cv2.VideoCapture(origin+"/"+path)
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    currentframe = 0

    first_iteration_indicator = 1
    for i in tqdm(range(0, frames), position=num, desc="Frame generation"):
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
            maxValue = int(2 * divider / level)
            ret, th1 = cv2.threshold(fgmask, thresh, maxValue, cv2.THRESH_BINARY)
            # for testing purposes, show the threshold image
            # cv2.imshow('diff-th1.jpg', th1)

            # add to the accumulated image
            accum_image = cv2.add(accum_image, th1)
            # for testing purposes, show the accumulated image
            # cv2.imshow('diff-accum.jpg', accum_image)

            # for testing purposes, control frame by frame
            color_image = im_color = cv2.applyColorMap(accum_image, cv2.COLORMAP_HOT)
            result_overlay = cv2.addWeighted(frame, 0.7, color_image, 0.7, 0)
            if not os.path.exists(origin+"/working/"+outpath):
                os.mkdir(origin+"/working/"+outpath)
            cv2.imwrite(origin+"/working/"+outpath+"/"+str(currentframe)+".jpg", result_overlay)

        # for testing purposes, show the current frame
        # cv2.imshow('frame', gray)
         
        for i in range(1, divider):
            try:
                cap.read()
            except:
                pass
        currentframe += 1

    home = os.getcwd()
    standard.rename(origin+"/working/"+outpath)
    os.chdir(home)

    out = cv2.VideoWriter(origin+"/output/"+outpath, cv2.VideoWriter_fourcc(*'mp4v'), 15, (width, height))
    working_dir = standard.sort_nicely(os.listdir(origin+"/working/"+outpath))
    for i in tqdm(range(0, len(working_dir)), position=num, desc="Video generation"):
        img = cv2.imread(origin+"/working/"+outpath+"/"+working_dir[i])
        out.write(img)
    out.release()

    standard.remove(origin+"/working/"+outpath)

    # overlay the color mapped image to the first frame
    result_overlay = cv2.addWeighted(first_frame, 0.7, color_image, 0.7, 0)

    # cleanup
    cap.release()

if __name__=='__main__':
    try:
        print("OpenCV Version:", cv2.__version__)
        path = input("Path to Videofolder/-file: ")
        divider = standard.input_int("All Frames divided by: ")
        frames = {}
        if os.path.isdir(path):
            standard.mkdir(path)
            for file in tqdm(os.listdir(path), desc="Files"):
                if not os.path.isdir(path+"/"+file):
                    if file != ".cache":
                        print("counting:", file)
                        frames[file] = count_frames(path, file)
            print(frames)
            json.dump(frames, open(path+"/.cache", "w"), sort_keys=True, indent=4)
            for file in tqdm(frames, position=0, desc="General"):
                if not os.path.isdir(path+"/"+file):
                    print(file)
                    p1 = Process(target=main, args=(path, file, 1, divider, 1, frames[file], ))
                    p2 = Process(target=main, args=(path, file, 2, divider, 1.5, frames[file]))
                    p3 = Process(target=main, args=(path, file, 3, divider, 2, frames[file]))
                    p1.start()
                    p2.start()
                    p3.start()
                    p1.join()
                    p2.join()
                    p3.join()
        else:
            path, file = os.path.split(path)
            standard.mkdir(path)
            print("preview:", file)
            frames[file] = main(path, path+"/"+file, file+"_preview.mp4", divider*4, 1)
            print(frames)
            print(file)
            p1 = Process(target=main, args=(path, path+"/"+file, file+"_1.mp4", divider, 1, frames[file], ))
            p2 = Process(target=main, args=(path, path+"/"+file, file+"_2.mp4", divider, 1.5, frames[file]))
            p3 = Process(target=main, args=(path, path+"/"+file, file+"_3.mp4", divider, 2, frames[file]))
            p1.start()
            p2.start()
            p3.start()
            p1.join()
            p2.join()
            p3.join()
    except KeyboardInterrupt:
        print("User sent exit signal.\nBye")