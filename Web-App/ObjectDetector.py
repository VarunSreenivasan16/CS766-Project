import cv2
import json
import torch
import torchvision
import numpy as np
from PIL import Image
import os
from os import path
import json
import base64
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from typing import List, Tuple
from collections import Counter

import detectron2
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.data.datasets import register_coco_instances
from detectron2.engine import DefaultPredictor
from detectron2.modeling import build_model
from detectron2.utils.visualizer import Visualizer
from detectron2.utils.visualizer import ColorMode
from detectron2.structures import BoxMode
from detectron2 import model_zoo

class Detector:

	def __init__(self):

		# Generic
		lvis_metadata = MetadataCatalog.get("lvis_v0.5_train")
		self.generic_metadata = lvis_metadata

		lvis_scale = 0.8
		self.generic_scale = lvis_scale

		lvis_cfg = get_cfg()
		lvis_cfg.merge_from_file("configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
		lvis_cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1230
		lvis_cfg.MODEL.WEIGHTS = os.path.join("modes/LVIS/Model/", "model_final_571f7c.pkl")
		lvis_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5   # set the testing threshold for this model
		lvis_cfg.MODEL.DEVICE = "cpu"

		lvis_predictor = DefaultPredictor(lvis_cfg)
		self.generic_predictor = lvis_predictor

		# Cityscape
		cityscape_metadata = MetadataCatalog.get("cityscapes_fine_instance_seg_train")
		self.cityscape_metadata = cityscape_metadata

		cityscape_scale = 1.0
		self.cityscape_scale = cityscape_scale

		cityscape_cfg = get_cfg()
		cityscape_cfg.merge_from_file("configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
		cityscape_cfg.MODEL.ROI_HEADS.NUM_CLASSES = 8
		cityscape_cfg.MODEL.WEIGHTS = os.path.join("modes/Cityscapes/Model/", "model_final_af9cf5.pkl")
		cityscape_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5   # set the testing threshold for this model
		cityscape_cfg.MODEL.DEVICE = "cpu"

		cityscape_predictor = DefaultPredictor(cityscape_cfg)
		self.cityscape_predictor = cityscape_predictor

		# Marine
		register_coco_instances("marine", {}, "modes/TrashCan/Dataset/instance_version/instances_train_trashcan.json", "modes/TrashCan/Dataset/instance_version/train")
		marine_metadata = MetadataCatalog.get("marine")
		self.marine_metadata = marine_metadata

		marine_scale = 1.0
		self.marine_scale = marine_scale

		marine_cfg = get_cfg()
		marine_cfg.merge_from_file("configs/COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x.yaml")
		marine_cfg.MODEL.ROI_HEADS.NUM_CLASSES = 22
		marine_cfg.MODEL.WEIGHTS = os.path.join("modes/TrashCan/Model/", "model_final.pth")
		marine_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5   # set the testing threshold for this model
		marine_cfg.MODEL.DEVICE = "cpu"

		marine_predictor = DefaultPredictor(marine_cfg)
		self.marine_predictor = marine_predictor

		# Nature
		register_coco_instances("Nature", {}, "modes/Nature/Dataset/Nature/train.json", "modes/Nature/Dataset/Nature/train")
		nature_metadata = MetadataCatalog.get("Nature")
		self.nature_metadata = nature_metadata

		nature_scale = 1.0
		self.nature_scale = nature_scale

		nature_cfg = get_cfg()
		nature_cfg.merge_from_file("configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
		nature_cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2
		nature_cfg.MODEL.WEIGHTS = os.path.join("modes/Nature/Model/", "model_final.pth")
		nature_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5   # set the testing threshold for this model
		nature_cfg.MODEL.DEVICE = "cpu"

		nature_predictor = DefaultPredictor(nature_cfg)
		self.nature_predictor = nature_predictor

		# Micro-Controller
		register_coco_instances("micro_controller", {}, "modes/Microcontroller-Segmentation/Dataset/train.json", "./Microcontroller-Segmentation/Dataset/train")
		micro_metadata = MetadataCatalog.get("micro_controller")
		self.micro_metadata = micro_metadata

		micro_scale = 1.0
		self.micro_scale = micro_scale

		micro_cfg = get_cfg()
		micro_cfg.merge_from_file("configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
		micro_cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4
		micro_cfg.MODEL.WEIGHTS = os.path.join("modes/Microcontroller-Segmentation/Model/", "model_final.pth")
		micro_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5   # set the testing threshold for this model
		micro_cfg.MODEL.DEVICE = "cpu"

		micro_predictor = DefaultPredictor(micro_cfg)
		self.micro_predictor = micro_predictor

		# Balloon
		DatasetCatalog.register("balloons", lambda: self.get_balloon_dicts("modes/balloon/Dataset/train"))
		MetadataCatalog.get("balloons").set(thing_classes=["balloon"])
		balloon_metadata = MetadataCatalog.get("balloons")
		self.balloon_metadata = balloon_metadata

		balloon_scale = 1.0
		self.balloon_scale = balloon_scale

		balloon_cfg = get_cfg()
		balloon_cfg.merge_from_file("configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
		balloon_cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
		balloon_cfg.MODEL.WEIGHTS = os.path.join("modes/balloon/Model/", "model_final.pth")
		balloon_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5   # set the testing threshold for this model
		balloon_cfg.MODEL.DEVICE = "cpu"

		balloon_predictor = DefaultPredictor(balloon_cfg)
		self.balloon_predictor = balloon_predictor

	def inference(self, imagePathString, modePathString = 'generic', imageFormatString = 'jpg'):

		if (modePathString == 'marine'):
			predictor = self.marine_predictor
			metadata = self.marine_metadata
			scale = self.marine_scale
		elif (modePathString == 'city'):
			predictor = self.cityscape_predictor
			metadata = self.cityscape_metadata
			scale = self.cityscape_scale
		elif (modePathString == 'nature'):
			predictor = self.nature_predictor
			metadata = self.nature_metadata
			scale = self.nature_scale
		elif (modePathString == 'micro-controller'):
			predictor = self.micro_predictor
			metadata = self.micro_metadata
			scale = self.micro_scale
		elif (modePathString == 'balloon'):
			predictor = self.balloon_predictor
			metadata = self.balloon_metadata
			scale = self.balloon_scale
		else:
			predictor = self.generic_predictor
			metadata = self.generic_metadata
			scale = self.generic_scale

		print("In Detector.inference()")
		print('=============================')
		print('Current Directory: ' + os.getcwd())
		print('Image Path: ' + imagePathString)
		print('Path Exists: ' + str(path.exists(imagePathString)))
		print('Mode: ' + modePathString)
		print('Format: ' + imageFormatString)
		print('=============================')

		im = cv2.imread(imagePathString)

		outputs = predictor(im)
		# v = Visualizer(im[:, :, ::-1],
		# 			metadata=metadata,
		# 			scale=scale, 
		# 			instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels
		# )

		v = Visualizer(im[:, :, :],
					metadata=metadata,
					scale=scale, 
					instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels
		)

		v = v.draw_instance_predictions(outputs["instances"].to("cpu"))

		# Attempt 1 - save the image to a png or jpg file and read back in
		# Return: return the path of the saved image so it can be read back in in app
		
		imagePathComponents = imagePathString.split(".")
		filename = imagePathComponents[0] + '_processed.' + imagePathComponents[1]
		cv2.imwrite(filename, v.get_image())

		print('Response Path: ' + filename)
		print('=============================')
		return filename

	def cut_mask(self, img_path: str, file_human_hint: str, file_mask: str, np_mask: np.ndarray, bounding_box: tuple, first_round: bool, save_figure=False, dict_output_figure_names=None, gmm_priors=None):
		"""Grabcut the mask predicted by mask-rcnn.
		Note for the codes for the mask image used by Grabcut
		- 0: sure background / 2: possible background
		- 1: sure foreground / 3: possible foreground

		Args:
			img_path (str): The file of the raw image without any annotation (unit8).
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
		img = cv2.imread(img_path)
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		print(img.shape)

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

		print('Mask Shape: ')
		print(mask.shape)
		# ---------------------
		# modify the mask by the human hint
		# - mark as "sure foreground and sure background"
		# ---------------------
		mask_hint = cv2.imread(file_human_hint, 0)
		print('Mask Hint Shape: ')
		print(mask_hint.shape)
		mask[mask_hint >= 200] = 1
		mask[mask_hint == 0] = 0 # Changed this from == 0 to < 1



		# ---------------------
		# modify the mask by the bounding box
		# - mark anything outside the box as "sure background"
		# ---------------------
		# - (st_col, st_row, end_col, end_row)
		box = bounding_box
		print(bounding_box)
		mask_box = np.zeros([640, 480], np.uint8) # Changed this from :-1 to :1
		print(mask_box.shape)
		mask_box[box[0]:box[2], box[1]:box[3]] = 3
		mask[mask_box == 0] = 0 # Changed this from == 0 to < 1

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

		imagePathComponents = img_path.split(".")
		filename = imagePathComponents[0] + '_processed_grabcut.' + imagePathComponents[1]
		plt.imsave(filename, img)
		plt.close()

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

		# TODO: Save the image to the file system and return the path to the processed image
		# return (img, mask, gmm_posteriors)
		return (filename, mask, gmm_posteriors)

    # Helper function for the Balloon initialization
	@staticmethod
	def get_balloon_dicts(img_dir):
		json_file = os.path.join(img_dir, "via_region_data.json")
		with open(json_file) as f:
			imgs_anns = json.load(f)

		dataset_dicts = []
		for idx, v in enumerate(imgs_anns.values()):
			record = {}
			
			filename = os.path.join(img_dir, v["filename"])
			height, width = cv2.imread(filename).shape[:2]
			
			record["file_name"] = filename
			record["image_id"] = idx
			record["height"] = height
			record["width"] = width

			annos = v["regions"]
			objs = []
			for _, anno in annos.items():
				assert not anno["region_attributes"]
				anno = anno["shape_attributes"]
				px = anno["all_points_x"]
				py = anno["all_points_y"]
				poly = [(x + 0.5, y + 0.5) for x, y in zip(px, py)]
				poly = [p for x in poly for p in x]

				obj = {
					"bbox": [np.min(px), np.min(py), np.max(px), np.max(py)],
					"bbox_mode": BoxMode.XYXY_ABS,
					"segmentation": [poly],
					"category_id": 0,
				}
				objs.append(obj)
			record["annotations"] = objs
			dataset_dicts.append(record)
		return dataset_dicts