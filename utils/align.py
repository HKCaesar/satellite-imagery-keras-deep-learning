import numpy as np
import cv2
import matplotlib.pyplot as plt
from spectral import get_rgb
from skimage.measure import structural_similarity as ssim
from sklearn.preprocessing import MinMaxScaler

def get_affine_matrix(image_tif_bgrn, image_jpg_bgr, verbose=False):
# Code adpated from http://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/
# Parametric Image Alignment using Enhanced Correlation Coefficient Maximization
	im1= image_jpg_bgr
	im2= image_tif_bgrn

	tif_rgb = get_rgb(im2, [2, 1, 0]) # RGB
	# rescaling to 0-255 range - uint8 for display
	rescaleIMG = np.reshape(tif_rgb, (-1, 1))
	scaler = MinMaxScaler(feature_range=(0, 255))
	rescaleIMG = scaler.fit_transform(rescaleIMG)
	img_scaled = (np.reshape(rescaleIMG, tif_rgb.shape)).astype(np.uint8)

	# Convert images to grayscale
	im1_gray = cv2.cvtColor(im1,cv2.COLOR_BGR2GRAY).astype(np.uint8)
	im2_gray = cv2.cvtColor(img_scaled,cv2.COLOR_RGB2GRAY).astype(np.uint8)

	#plt.imshow(im2_gray, cmap = plt.cm.gray)
	
	warp_mode = cv2.MOTION_TRANSLATION
	warp_matrix = np.eye(2, 3, dtype=np.float32)

	# TODO Refine termination criteria
	number_of_iterations = 5000
	termination_eps = 1e-10
	criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)

	# Run the ECC algorithm. The results are stored in warp_matrix.
	# TODO detect cases when there is no convergence.
	correlation, warp_matrix = cv2.findTransformECC(
		im1_gray, 
		im2_gray, 
		warp_matrix, 
		warp_mode, 
		criteria)

	#print(warp_matrix)

	tx = warp_matrix[0,2]
	ty = warp_matrix[1,2]

	warp_matrix[0,2] = np.round(tx)
	warp_matrix[1,2] = np.round(ty)

	tx = warp_matrix[0,2]
	ty = warp_matrix[1,2]

	#print(warp_matrix)
	if verbose:
		print('tx:{} ty:{} corr:{}'.format(tx, ty, np.round(correlation, decimals=2)))

	return correlation, warp_matrix

def align_target_tif_to_jpg(image_tif_bgrn, image_jpg_bgr, target, verbose=False):
	"""compute translational tranform matrix mapping image_tif to image_jpg and then apply the same matrix transform to target"""
	correlation, warp_matrix = get_affine_matrix(image_tif_bgrn, image_jpg_bgr)

	sz = image_jpg_bgr.shape

	tif_aligned = cv2.warpAffine(
		target,
		warp_matrix,
		(sz[1],sz[0]),
		flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, 
		borderMode = cv2.BORDER_CONSTANT, 
		borderValue = 0)

	return tif_aligned