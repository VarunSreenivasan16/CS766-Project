import numpy as np
import cv2
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from typing import List, Tuple

from collections import Counter


def cut_mask(file_raw_img: str, file_human_hint: str, file_mask: str, np_mask: np.ndarray, bounding_box: tuple, first_round: bool, save_figure=False, dict_output_figure_names=None, gmm_priors=None):
    """Grabcut the mask predicted by mask-rcnn.
    Note for the codes for the mask image used by Grabcut
    - 0: sure background / 2: possible background
    - 1: sure foreground / 3: possible foreground

    Args:
        file_raw_img (str): The file of the raw image without any annotation (unit8).
        file_human_hint (str): The file of the human hints (unit8).
            - White (255) = sure foreground, black (0) = sure background, gray = no hints.
        file_mask (str): Used only if `first_round = True`. The file of the current mask (unit8). Grabcut works based on this mask.
        np_mask (2d np array with uint8): Used only if `first_round = False`. Grabcut works based on this mask.
        bounding_box (List(int)): The upper-left and bottom-right points of the box (st_col, st_row, end_col, end_row).
        first_round (bool): Whether this is the first round of grabcut. If so, then create a hard bounding box based on mask-rcnn's predicted bounding box.
        save_figure (bool=False): Whether to save the figures.
        dict_output_figure_names (dict=None): Only used when `save_figure = True`.
            file_initial_segment_img: used only when `first_round=True`. the segmented image before Grabcut.
            file_before_overlay_hint_raw_mask: the raw mask overlaid with the human hints before Grabcut.
            file_segment_img: the updated segmented image after Grabcut.
            file_segment_binary_mask: the updated segmented binary mask after Grabcut.
            file_segment_raw_mask: the updated segmented raw mask (code: 0-3) after Grabcut.
            file_segment_raw_mask_npy: the updated segmented raw mask (code: 0-3) after Grabcut in the numpy format.
        gmm_priors (dict=None):
            fgdModel: the prior for the foreground model.
            bgdModel: the prior for the background model.
            Each should be of size (1,65) with type = np.float64.
            If not specified, they are both set to np.zeros((1, 65), np.float64) by default.

    Returns:
        img_segmented (2d np array with uint8): The segmented image.
        np_mask_updated (2d np array with uint8): The updated mask produced by Grabcut.
        gmm_posteriors (dict):  the updated models for the foreground/background model.
            fgdModel: the posterior for the foreground model.
            bgdModel: the posterior for the background model.
    """
    # read in the raw image
    # - img: (427, 640, 3)
    img = cv2.imread(file_raw_img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # ---------------------
    # load the initial mask
    # - and convert to the correct format
    # - mask: (280, 450)
    # ---------------------
    if first_round:    
        mask = cv2.imread(file_mask)
        mask = mask[:, :, 0]  # all channels encode the same information
        # - convert the values to "possible background" (code = 2) and "possible foreground" (code = 3)
        # -- Counter({0: 187298, 255: 85982})
        mask[mask == 0] = 2
        mask[mask == 255] = 3
        # - this magically fixed a bug (https://github.com/opencv/opencv/issues/18120#issuecomment-675517683)
        mask = np.array(mask)
    else:
        mask = np_mask

    if first_round and save_figure:
        # ----------------------
        # save the image segmented by the initial mask (before Grabcut)
        # ----------------------
        mask_init = np.where((mask == 2) | (
            mask == 0), 0, 1).astype('uint8')
        img_init = img*mask_init[:, :, np.newaxis]
        plt.imsave(
            dict_output_figure_names['file_initial_segment_img'], img_init)
        plt.close()

    # ---------------------
    # modify the mask by the human hint
    # - mark as "sure foreground and sure background"
    # ---------------------
    mask_hint = cv2.imread(file_human_hint, 0)
    mask[mask_hint >= 200] = 1
    mask[mask_hint == 0] = 0

    # ---------------------
    # modify the mask by the bounding box
    # - mark anything outside the box as "sure background"
    # ---------------------
    # - (st_col, st_row, end_col, end_row)
    box = bounding_box
    mask_box = np.zeros(img.shape[:-1], np.uint8)
    mask_box[box[0]:box[2], box[1]:box[3]] = 3
    mask[mask_box == 0] = 0

    # ---------------------
    # save the mask with human hints and bounding box included
    # ---------------------
    if save_figure:
        plt.imsave(
            dict_output_figure_names['file_before_overlay_hint_raw_mask'], mask, cmap=cm.gray)
        plt.close()

    # ---------------------
    # grab cut using the modified mask
    # ---------------------
    if gmm_priors is None:
        fgdModel = np.zeros((1, 65), np.float64)
        bgdModel = np.zeros((1, 65), np.float64)
    else:
        fgdModel = gmm_priors["fgdModel"]
        bgdModel = gmm_priors["bgdModel"]
    cv2.grabCut(img, mask, None, bgdModel,
                fgdModel, 5, cv2.GC_INIT_WITH_MASK)

    # ----------------------
    # apply the updated mask to the raw image
    # ----------------------
    # - mask: Counter({2: 47900, 3: 44100, 0: 34000}); 0: background, 2: probable background
    # - convert that to a binary mask
    # -- mask2: Counter({0: 81900, 1: 44100})
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    img = img*mask2[:, :, np.newaxis]

    if save_figure:
        # ----------------------
        # save the segmented image
        # ----------------------
        # plt.imshow(img)
        # plt.show()
        # plt.savefig(path.join(PATH_OUTPUT, FILENAME_VERSION + "-img-grid.jpg"))
        # plt.close()
        plt.imsave(dict_output_figure_names['file_segment_img'], img)
        plt.close()

        # ----------------------
        # also save the binary mask
        # ----------------------
        # plt.imshow(mask2, cmap="gray")
        # plt.savefig(
        #     path.join(PATH_OUTPUT, FILENAME_VERSION + "-binary-mask-grid.jpg"))
        # plt.close()
        plt.imsave(
            dict_output_figure_names['file_segment_binary_mask'], mask2, cmap=cm.gray)
        plt.close()

        # ----------------------
        # also save the raw mask (with value in [1,5])
        # ----------------------
        # plt.imshow(mask, cmap="gray")
        # plt.savefig(path.join(PATH_OUTPUT, FILENAME_VERSION + "-raw-mask-grid.jpg"))
        # plt.close()
        plt.imsave(
            dict_output_figure_names['file_segment_raw_mask'], mask, cmap=cm.gray)
        plt.close()

        # ----------------------
        # also save the raw value (imsave() will scale the value according to the coloar map)
        # ----------------------
        np.save(
            dict_output_figure_names['file_segment_raw_mask_npy'], mask)
    gmm_posteriors = {"fgdModel": fgdModel,
                        "bgdModel": bgdModel}
    return (img, mask, gmm_posteriors)
