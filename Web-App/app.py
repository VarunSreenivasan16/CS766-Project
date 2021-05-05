from flask import Flask, render_template, request, send_from_directory, send_file, jsonify
from PIL import Image
import io
import cv2
import numpy as np
import requests
import os
import json
import base64
import time
from ObjectDetector import Detector
import img_transforms

app = Flask(__name__)
detector = Detector()

ACTIVE_GRABCUT_DATA = {
	"keys": []
}

RENDER_FACTOR = 5

# Serve the webapp
@app.route("/")
def index():
	return render_template('index.html')

# Handle standard mode-based instance segmentation
@app.route("/standard", methods=['POST'])
def standardInference():

	batchId = request.form['id']
	batchSubId = request.form['subId']
	base64Image = request.form['image']
	imageFormat = request.form['imageFormat']
	inferenceMode = request.form['inferenceMode']

	base64ImageComponents = base64Image.split(",")
	base64ImagePrefix = base64ImageComponents[0]
	base64ImageData = base64ImageComponents[1]

	if imageFormat == "jpeg":
		imageFormat = "jpg"

	curTime = str(time.time()).split(".")[0]

	# What do we want to do?
	# We need to convert the base64 string into an image, save it, and pass the file path
	
	# Encoding Attempt 1 - Convert the base64 image into an image of the proper format
	# ------------------
	imageData = base64.b64decode(base64ImageData)
	preprocessed_filename = curTime + '_' + batchId + '_' + batchSubId + '.' + imageFormat

	print("In app.standardInference()")
	print('=============================')
	print('File Name: ' + preprocessed_filename)
	print('=============================')

	with open(preprocessed_filename, 'wb') as f:
		f.write(imageData)

	# Inference Attempt 1 - extract the image from the path returned by the function
	# -------------------

	# - We have a string containing the path to the processed image
	postprocessed_filename = run_inference(preprocessed_filename, inferenceMode, imageFormat)
	print("In app.standardInference()")
	print('=============================')
	print('Processed File Name: ' + postprocessed_filename)

	# - Get the image as base64 representation
	postprocessed_base64Image = base64Image # testing purposes for the API

	# postprocessed_image = cv2.imread(postprocessed_filename) - cv2
	with open(postprocessed_filename, "rb") as image_file:
		postprocessed_base64Image = base64.b64encode(image_file.read())

	# - Clean up created images
	imageDeletionStatus = "success"
	try:
		os.remove(preprocessed_filename)
		os.remove(postprocessed_filename)
	except:
		imageDeletionStatus = "failure"

	print('Image Deletion: ' + imageDeletionStatus)
	
	# - Create response object
	apiResponse = {
		'id': batchId,
		'subId': batchSubId,
		'processedImage': base64ImagePrefix + ',' + postprocessed_base64Image.decode('utf-8'),
		'imageFormat': imageFormat,
		'inferenceMode': inferenceMode,
		'imageDeletionStatus': imageDeletionStatus
	}

	print('=============================')
	# - Send the jsonified response
	return jsonify(apiResponse)

# Handle grabcut custom instance segmentation
@app.route("/grabcut", methods=['POST'])
def grabcutInference():

	batchId = request.form['id']
	batchSubId = request.form['subId']
	base64Image = request.form['image']
	base64ImageFormat = request.form['imageFormat']
	base64Mask= request.form['adjustmentMap']
	base64MaskFormat = request.form['adjustmentMapFormat']
	imageWidth = request.form['imageWidth']
	imageHeight = request.form['imageHeight']
	boundingBoxString = request.form['boundingBox']
	grabcutMode = request.form['grabcutMode']
	iterationCount = request.form['iterationCount']
	requestSessionKey = request.form['sessionKey']

	base64ImageComponents = base64Image.split(",")
	base64ImagePrefix = base64ImageComponents[0]
	base64ImageData = base64ImageComponents[1]

	base64MaskComponents = base64Mask.split(",")
	base64MaskPrefix = base64MaskComponents[0]
	base64MaskData = base64MaskComponents[1]

	boundingBox = boundingBoxString.split(",")

	if base64ImageFormat == "jpeg":
		base6iImageFormat = "jpg"

	if base64MaskFormat == "jpeg":
		base64MaskFormat = "jpg"

	curTime = str(time.time()).split(".")[0]

	imageData = base64.b64decode(base64ImageData)
	preprocessed_filename = curTime + '_grabcut.' + base64ImageFormat
	maskData = base64.b64decode(base64MaskData)
	preprocessed_mask_filename = curTime + '_mask_grabcut.' + base64MaskFormat

	print("In app.grabcutInference()")
	print('=============================')
	print('File Name: ' + preprocessed_filename)
	print('Mask File Name: ' + preprocessed_mask_filename)
	print('boundingBox', boundingBox)
	print('grabcutMode', grabcutMode)
	print('iterationCount', iterationCount)
	print('requestSessionKey', requestSessionKey)
	print('=============================')

	with open(preprocessed_filename, 'wb') as f:
		f.write(imageData)
		f.seek(0)

	with open(preprocessed_mask_filename, 'wb') as f:
		f.write(maskData)

	img = Image.open(preprocessed_filename)
	new_width, new_height = 480, 640
	wpercent = (new_width / float(img.size[0]))
	hsize = int((float(img.size[1]) * float(wpercent)))

	if img.mode != "RGB":
		img = img.convert('RGB')

	og_img = None
	if img.size[0] < new_width:
	#upscale
		og_img = img.resize((new_width, hsize), Image.BICUBIC)
	elif img.size[0] >= new_width:
	#downscale
		og_img = img.resize((new_width, hsize), Image.ANTIALIAS)

	og_img = og_img.crop((0, 0, 480, 640))
	og_img.save(preprocessed_filename)

	sessionKey = "-1"

	# if (grabcutMode == 'advanced'):
	# 	if (iterationCount == 1):
	# 		pass
	# 	else:	
	# 		pass
	# else:
	# 	if (iterationCount == "1"):
	# 		# From the request, we need:
	# 		# - Image
	# 		# - Mask
	# 		# - Bounding box
	# 		# From the server, we need: 
	# 		# - All white binary mask - Make sure to pay attention to sizes here, might be good to make dynamic
	# 		sessionKey = curTime
	# 		# TODO: Create the all white image here
	# 		# maskData = base64.b64decode(base64MaskData)
	# 		preprocessed_initial_mask_filename = curTime + '_initial_grabcut.png'

	# 		white_img = np.zeros([int(imageHeight), int(imageWidth), 3], dtype=np.uint8)
	# 		white_img.fill(255)
	# 		im = Image.fromarray(white_img)
	# 		im.save(preprocessed_initial_mask_filename)

	# 		# with open(preprocessed_initial_mask_filename, 'wb') as f:
	# 		# 	f.write(imageData)

	# 		print('Initial Mask File Name: ' + preprocessed_initial_mask_filename)

	# 		postprocessed_filename, mask, gmm_posteriors = detector.cut_mask(
	# 			img_path=preprocessed_filename,
	# 			file_human_hint=preprocessed_mask_filename,
	# 			file_mask=preprocessed_initial_mask_filename,
	# 			np_mask=None,
	# 			bounding_box=(int(boundingBox[0]), int(boundingBox[1]), int(boundingBox[2]), int(boundingBox[3])),
	# 			first_round=True,
	# 			save_figure=False,
	# 			dict_output_figure_names=None,
	# 			gmm_priors=None
	# 		)
	# 		# no prior info for the models
	# 		ACTIVE_GRABCUT_DATA['keys'].append(sessionKey)
	# 		ACTIVE_GRABCUT_DATA[sessionKey + '_mask'] = mask
	# 		ACTIVE_GRABCUT_DATA[sessionKey + '_gmmPosteriors'] = gmm_posteriors
	# 	else:
	# 		sessionKey = requestSessionKey
	# 		postprocessed_filename, mask, gmm_posteriors = detector.cut_mask(
	# 			img_path=preprocessed_filename,
	# 			file_human_hint=preprocessed_mask_filename,
	# 			file_mask=None,
	# 			np_mask=ACTIVE_GRABCUT_DATA[sessionKey + '_mask'] ,
	# 			bounding_box=(int(boundingBox[0]), int(boundingBox[1]), int(boundingBox[2]), int(boundingBox[3])),
	# 			first_round=False,
	# 			save_figure=False,
	# 			dict_output_figure_names=None,
	# 			# no prior info for the models
	# 			gmm_priors=ACTIVE_GRABCUT_DATA[sessionKey + '_gmmPosteriors']
	# 		)
	# 		ACTIVE_GRABCUT_DATA[sessionKey + '_mask'] = mask
	# 		ACTIVE_GRABCUT_DATA[sessionKey + '_gmmPosteriors'] = gmm_posteriors

	# Inference Attempt 1 - extract the image from the path returned by the function
	# -------------------

	# - We have a string containing the path to the processed image
	 
	print("In app.grabcutInference()")
	print('=============================')
	# print('Processed File Name: ' + postprocessed_filename)

	# - Get the image as base64 representation
	postprocessed_base64Image = base64Image # testing purposes for the API
	
	# with open(postprocessed_filename, "rb") as image_file:
	# 	postprocessed_base64Image = base64.b64encode(image_file.read())
	
	with open(preprocessed_filename, "rb") as image_file:
		postprocessed_base64Image = base64.b64encode(image_file.read())

	# # - Clean up created images
	imageDeletionStatus = "success"
	try:
		os.remove(preprocessed_filename)
		os.remove(preprocessed_mask_filename)
		if (iterationCount == 1):
			os.remove(preprocessed_initial_mask_filename)
		os.remove(postprocessed_filename)
	except:
		imageDeletionStatus = "failure"

	print('Image Deletion: ' + imageDeletionStatus)

	apiResponse = {
		'id': batchId,
		'subId': batchSubId,
		'processedImage': base64ImagePrefix + ',' + postprocessed_base64Image.decode('utf-8'),
		'imageFormat': base64ImageFormat,
		'imageDeletionStatus': imageDeletionStatus,
		'sessionKey': sessionKey
	}

	print('=============================')
	return jsonify(apiResponse)

@app.route("/clear-grabcut-session", methods=['POST'])
def clearGrabcutSession():

	sessionKey = request.form['sessionKey']

	if sessionKey in ACTIVE_GRABCUT_DATA['keys']:
		ACTIVE_GRABCUT_DATA['keys'].remove(sessionKey)
	ACTIVE_GRABCUT_DATA.pop(sessionKey + '_mask', None)
	ACTIVE_GRABCUT_DATA.pop(sessionKey + '_gmmPosteriors', None)

	if sessionKey + '_mask' in ACTIVE_GRABCUT_DATA:
		status = 'failure'
	else:
		status = 'success'

	# - Create response object
	apiResponse = {
		'sessionKey': sessionKey,
		'status': status
	}

	# - Send the jsonified response
	return jsonify(apiResponse)

# Run inference using detectron2
def run_inference(img_path = 'file.jpg', mode = 'generic', formatString = 'jpg'):

	# run inference using detectron2
	result_img = detector.inference(img_path, mode, formatString)
	return result_img

# Run grabcut inference using cv2
def run_grabcut(img_path = 'file.jpg', mask_path = 'mask.jpg', imgFormatString = 'jpg', maskFormatString = 'jpg'):
	
	FIRST_ROUND = True
	SECOND_ROUND = True
	SAVE_FIGURE = False

	result_img = detector.cut_mask(
		file_raw_img=img_path,
		file_human_hint=FILE_STEP0_HUMAN_HINT,
        file_mask=FILE_INITIAL_MASK,
		np_mask=None,
		bounding_box=(36, 0, 370, 380),
		first_round=FIRST_ROUND,
		save_figure=SAVE_FIGURE,
		dict_output_figure_names=dict_output_figure_names_step0,
		# no prior info for the models
		gmm_priors=None
	)
	return result_img

#### MAIN APP HANDLER ####
if __name__ == "__main__":

	# get port. Default to 8080
	port = int(os.environ.get('PORT', 8080))

	# run app
	app.run(host='0.0.0.0', port=port)

# Steps for image transformation - work in progress
# 	# get height, width of image
# 	original_img = Image.open(img_path)

# 	# transform to square, using render factor
# 	transformed_img = img_transforms._scale_to_square(original_img, targ=RENDER_FACTOR*16)
# 	transformed_img.save(transformed_path)

# 	# run inference using detectron2
# 	untransformed_result = detector.inference(transformed_path)

# 	# unsquare
# 	result_img = img_transforms._unsquare(untransformed_result, original_img)