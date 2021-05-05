"""
Use GrabCut based on mask for a bus that Matterport predicted.

- Note that the results might be different across trials with the same input data.
The reason is that in opencv, mixture are estimated using kmeans. kmeans gives a gaussian mixture using an iterative algorithm with random trials (5=GMM::componentsCount). 
-- see: https://answers.opencv.org/question/200262/difference-between-output-of-grabcut-between-runs/
"""

import numpy as np
import cv2
from matplotlib import pyplot as plt
from collections import Counter
from os import path
import matplotlib.cm as cm
import grabcut_pkg as gpk

# ---------------------
# constants
# ---------------------
# - par
FILENAME_VERSION = "bus-mask"
STEP0_HINT_VERSION = "v1"
STEP1_HINT_VERSION = "v1"

# -- whether run the step 0
RUN_FIRST = True
# -- whether to save to image segmented by the initial mask (within step 0)
SAVE_INITIAL = True
# -- whether run the step 1
RUN_SECOND = True

# - path
PATH_INPUT = path.join('..', 'images', 'bus-mask')
PATH_OUTPUT = path.join('..', 'outputs', 'bus-mask')
PATH_HUMAN_HINT = PATH_OUTPUT  # because it depends on the initial output

# - file
FILE_INPUT = path.join(PATH_INPUT, 'bus-raw.jpg')
# -- the initial mask predicted by Mask-RCNN
FILE_INITIAL_MASK = path.join(PATH_INPUT, 'bus-mask.png')
# -- the image segmented by the initial mask
FILE_INITIAL_SEGMENT_IMG = path.join(
    PATH_OUTPUT, FILENAME_VERSION + "-initial-img.jpg")

# -- step 0: segment after applying the first round of hint
FILE_STEP0_HUMAN_HINT = path.join(
    PATH_INPUT, FILENAME_VERSION + '-human-hint-step0-'+STEP0_HINT_VERSION+'.png')
FILE_BEFORE_STEP0_OVERLAY_HINT_RAW_MASK = path.join(PATH_OUTPUT, FILENAME_VERSION +
                                                    "-step0-before-raw-mask-with-hints-"+STEP0_HINT_VERSION+".jpg")
FILE_SEGMENT_STEP0_IMG = path.join(
    PATH_OUTPUT, FILENAME_VERSION + "-step0-updated-img.jpg")
FILE_SEGMENT_STEP0_BINARY_MASK = path.join(
    PATH_OUTPUT, FILENAME_VERSION + "-step0-updated-binary-mask.jpg")
FILE_SEGMENT_STEP0_RAW_MASK = path.join(
    PATH_OUTPUT, FILENAME_VERSION + "-step0-updated-raw-mask.jpg")
FILE_SEGMENT_STEP0_RAW_MASK_NPY = path.join(PATH_OUTPUT, FILENAME_VERSION +
                                            "-step0-raw-mask.npy")

# -- step 1: segment after applying the first round of hint
FILE_STEP1_HUMAN_HINT = path.join(
    PATH_OUTPUT, FILENAME_VERSION + '-human-hint-step1-'+STEP1_HINT_VERSION+'.png')
FILE_BEFORE_STEP1_OVERLAY_HINT_RAW_MASK = path.join(PATH_OUTPUT, FILENAME_VERSION +
                                                    "-step1-before-raw-mask-with-hints-"+STEP1_HINT_VERSION+".jpg")
FILE_SEGMENT_STEP1_RAW_MASK = path.join(PATH_OUTPUT, FILENAME_VERSION +
                                        "-step1-updated-raw-mask-"+STEP1_HINT_VERSION+".jpg")
FILE_SEGMENT_STEP1_BINARY_MASK = path.join(PATH_OUTPUT, FILENAME_VERSION +
                                           "-step1-updated-binary-mask-"+STEP1_HINT_VERSION+".jpg")
FILE_SEGMENT_STEP1_IMG = path.join(PATH_OUTPUT, FILENAME_VERSION +
                                   "-step1-updated-img-"+STEP1_HINT_VERSION+".jpg")
FILE_SEGMENT_STEP1_RAW_MASK_NPY = path.join(PATH_OUTPUT, FILENAME_VERSION +
                                            "-step1-updated-raw-mask.npy")

# ---------------------
# step 0:
# - start with the initial mask from mask-rcnn
# - modify by the 1st hint given by the human
# - also modify by the bounding given by the human
# codes:
# - 0: sure background / 2: possible background
# - 1: sure foreground / 3: possible foreground
# ---------------------
if RUN_FIRST:
    # set the output figure names
    dict_output_figure_names_step0 = {
        # used only when `first_round=True`. the segmented image before Grabcut.
        "file_initial_segment_img": FILE_INITIAL_SEGMENT_IMG,
        # the raw mask overlaid with the human hints before Grabcut.
        "file_before_overlay_hint_raw_mask": FILE_BEFORE_STEP0_OVERLAY_HINT_RAW_MASK,
        #  the updated segmented image after Grabcut.
        "file_segment_img": FILE_SEGMENT_STEP0_IMG,
        # the updated segmented binary mask after Grabcut.
        "file_segment_binary_mask": FILE_SEGMENT_STEP0_BINARY_MASK,
        # the updated segmented raw mask (code: 0-3) after Grabcut.
        "file_segment_raw_mask": FILE_SEGMENT_STEP0_RAW_MASK,
        # the updated segmented raw mask (code: 0-3) after Grabcut in the numpy format.
        "file_segment_raw_mask_npy": FILE_SEGMENT_STEP0_RAW_MASK_NPY
    }
    # run Grabcut
    _, mask, gmm_posteriors = gpk.cut_mask(file_raw_img=FILE_INPUT,
                                           file_human_hint=FILE_STEP0_HUMAN_HINT,
                                           file_mask=FILE_INITIAL_MASK,
                                           np_mask=None,
                                           bounding_box=(36, 0, 370, 380),
                                           first_round=True,
                                           save_figure=True,
                                           dict_output_figure_names=dict_output_figure_names_step0,
                                           # no prior info for the models
                                           gmm_priors=None
                                           )
    # # read in the raw image
    # # - img: (427, 640, 3)
    # img = cv2.imread(FILE_INPUT)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # # ---------------------
    # # load the initial mask
    # # - and convert to the correct format
    # # - mask: (280, 450)
    # # ---------------------

    # mask = cv2.imread(FILE_INITIAL_MASK)
    # mask = mask[:, :, 0]  # all channels encode the same information
    # # - convert the values to "possible background" (code = 2) and "possible foreground" (code = 3)
    # # -- Counter({0: 187298, 255: 85982})
    # mask[mask == 0] = 2
    # mask[mask == 255] = 3
    # # - this magically fixed a bug (https://github.com/opencv/opencv/issues/18120#issuecomment-675517683)
    # mask = np.array(mask)

    # if SAVE_INITIAL:
    #     # ----------------------
    #     # save the image segmented by the initial mask
    #     # ----------------------
    #     mask_init = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    #     img_init = img*mask_init[:, :, np.newaxis]
    #     plt.imsave(FILE_INITIAL_SEGMENT_IMG, img_init)
    #     plt.close()

    # # ---------------------
    # # modify the mask by the human hint
    # # - mark as "sure foreground and sure background"
    # # ---------------------
    # mask_hint = cv2.imread(FILE_STEP0_HUMAN_HINT, 0)
    # mask[mask_hint >= 200] = 1
    # mask[mask_hint == 0] = 0

    # # ---------------------
    # # modify the mask by the bounding box
    # # - mark anything outside the box as "sure background"
    # # ---------------------
    # # - (st_col, st_row, end_col, end_row)
    # box = (36, 0, 370, 380)
    # mask_box = np.zeros(img.shape[:-1], np.uint8)
    # mask_box[box[0]:box[2], box[1]:box[3]] = 3
    # mask[mask_box == 0] = 0

    # # ---------------------
    # # save the mask with human hints and bounding box included
    # # ---------------------
    # plt.imsave(FILE_BEFORE_STEP0_OVERLAY_HINT_RAW_MASK, mask, cmap=cm.gray)
    # plt.close()

    # # ---------------------
    # # grab cut using the modified mask
    # # ---------------------
    # bgdModel = np.zeros((1, 65), np.float64)
    # fgdModel = np.zeros((1, 65), np.float64)
    # cv2.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)

    # # ----------------------
    # # apply the updated mask to the raw image
    # # ----------------------
    # # - mask: Counter({2: 47900, 3: 44100, 0: 34000}); 0: background, 2: probable background
    # # - convert that to a binary mask
    # # -- mask2: Counter({0: 81900, 1: 44100})
    # mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    # img = img*mask2[:, :, np.newaxis]

    # # ----------------------
    # # save the segmented image
    # # ----------------------
    # # plt.imshow(img)
    # # plt.show()
    # # plt.savefig(path.join(PATH_OUTPUT, FILENAME_VERSION + "-img-grid.jpg"))
    # # plt.close()
    # plt.imsave(FILE_SEGMENT_STEP0_IMG, img)
    # plt.close()

    # # ----------------------
    # # also save the binary mask
    # # ----------------------
    # # plt.imshow(mask2, cmap="gray")
    # # plt.savefig(
    # #     path.join(PATH_OUTPUT, FILENAME_VERSION + "-binary-mask-grid.jpg"))
    # # plt.close()
    # plt.imsave(FILE_SEGMENT_STEP0_BINARY_MASK, mask2, cmap=cm.gray)
    # plt.close()

    # # ----------------------
    # # also save the raw mask (with value in [1,5])
    # # ----------------------
    # # plt.imshow(mask, cmap="gray")
    # # plt.savefig(path.join(PATH_OUTPUT, FILENAME_VERSION + "-raw-mask-grid.jpg"))
    # # plt.close()
    # plt.imsave(FILE_SEGMENT_STEP0_RAW_MASK, mask, cmap=cm.gray)
    # plt.close()

    # # ----------------------
    # # also save the raw value (imsave() will scale the value according to the coloar map)
    # # ----------------------
    # np.save(FILE_SEGMENT_STEP0_RAW_MASK_NPY, mask)

# ----------------------
# step 1: modify the mask by 2nd hint given by human
# ----------------------
if RUN_SECOND:
   # set the output figure names
    dict_output_figure_names_step1 = {
        # the raw mask overlaid with the human hints before Grabcut.
        "file_before_overlay_hint_raw_mask": FILE_BEFORE_STEP1_OVERLAY_HINT_RAW_MASK,
        #  the updated segmented image after Grabcut.
        "file_segment_img": FILE_SEGMENT_STEP1_IMG,
        # the updated segmented binary mask after Grabcut.
        "file_segment_binary_mask": FILE_SEGMENT_STEP1_BINARY_MASK,
        # the updated segmented raw mask (code: 0-3) after Grabcut.
        "file_segment_raw_mask": FILE_SEGMENT_STEP1_RAW_MASK,
        # the updated segmented raw mask (code: 0-3) after Grabcut in the numpy format.
        "file_segment_raw_mask_npy": FILE_SEGMENT_STEP1_RAW_MASK_NPY
    }
    if not RUN_FIRST:
        # load the raw mask from the previous round in numpy format
        mask = np.load(FILE_SEGMENT_STEP0_RAW_MASK_NPY)
        # note that this will recompute the foreground and background GMM from scratch again
        # - rather than using the results from the previous round
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        gmm_posteriors = {"fgdModel": fgdModel, "bgdModel": bgdModel}
    # run Grabcut
    _, mask, gmm_posteriors = gpk.cut_mask(file_raw_img=FILE_INPUT,
                                           file_human_hint=FILE_STEP1_HUMAN_HINT,
                                           file_mask=None,
                                           np_mask=mask,
                                           bounding_box=(36, 0, 370, 380),
                                           first_round=False,
                                           save_figure=True,
                                           dict_output_figure_names=dict_output_figure_names_step1,
                                           # continue to use the same models
                                           gmm_priors=gmm_posteriors
                                           )

    # # read in the raw image again
    # img = cv2.imread(FILE_INPUT)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # # mask_hint is the mask image I manually labelled
    # mask_hint = cv2.imread(FILE_STEP1_HUMAN_HINT, 0)
    # if not RUN_FIRST:
    #     # load the raw mask in numpy format
    #     mask = np.load(FILE_SEGMENT_STEP0_RAW_MASK_NPY)
    #     # note that this will recompute the foreground and background GMM from scratch again
    #     # - rather than using the results from the previous round
    #     bgdModel = np.zeros((1, 65), np.float64)
    #     fgdModel = np.zeros((1, 65), np.float64)

    # # edit the mask directly
    # # - whereever it is marked white (sure foreground), change mask = 1 [3: possible foreground]
    # # - whereever it is marked black (sure background), change mask = 0 [2: possible background]
    # # -- Counter(mask_hint.ravel()):
    # mask[mask_hint >= 200] = 1
    # mask[mask_hint == 0] = 0

    # # save the mask with human hints included
    # plt.imsave(FILE_BEFORE_STEP1_OVERLAY_HINT_RAW_MASK, mask, cmap=cm.gray)
    # plt.close()

    # # rerun grabCut() with the "mask mode"
    # mask, bgdModel, fgdModel = cv2.grabCut(
    #     img, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)

    # # apply the binary mask to the image
    # mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    # img = img*mask2[:, :, np.newaxis]

    # # save the updated mask
    # # - save the binary mask
    # plt.imsave(FILE_SEGMENT_STEP1_BINARY_MASK,
    #            mask2, cmap=cm.gray)
    # plt.close()
    # # - save the raw mask (with value in [1,5])
    # plt.imsave(FILE_SEGMENT_STEP1_RAW_MASK, mask, cmap=cm.gray)
    # plt.close()
    # # preserve the raw value (imsave() will scale the value according to the coloar map)
    # np.save(FILE_SEGMENT_STEP1_RAW_MASK_NPY, mask)

    # # plt.imshow(img)
    # # plt.imsave(path.join(PATH_OUTPUT, FILENAME_VERSION +
    # #            "-img-after-grid.jpg"), img)
    # # plt.close()
    # # preserve the raw value (imsave() will scale the value according to the coloar map)
    # plt.imsave(FILE_SEGMENT_STEP1_IMG, img)
    # plt.close()
