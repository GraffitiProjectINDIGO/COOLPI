import os
import copy

import cv2
import matplotlib.pyplot as plt
import numpy as np

from coolpi.auxiliary.errors import ColourCheckerError, ClassMethodError
import coolpi.auxiliary.common_operations as cop

def get_abs_path_coolpi():
    from coolpi import __file__ as current_dir
    coolpy_path = os.path.abspath(current_dir)
    return coolpy_path[:-12]
    
def feature_detection_sift_opencv(training_img, sample_img, show_figure = False):
    # copy to protect the original images
    show_kp1 = copy.copy(training_img)
    show_kp2 = copy.copy(sample_img)
    algorithm = cv2.SIFT_create()
    # alternative algorithm ORB. Note: Orb works with BFMatcher not with FlannBasedMatcher. WORST RESULTS
    #algorithm = cv2.ORB_create()
    kp1, des1 = algorithm.detectAndCompute(training_img, None) # key point, des numpy array ?
    kp2, des2 = algorithm.detectAndCompute(sample_img, None)
    show_kp1 = cv2.drawKeypoints(show_kp1, kp1, show_kp1)
    show_kp2 = cv2.drawKeypoints(show_kp2, kp2, show_kp2)
    
    b, g, r = np.dsplit(show_kp1, 3) # rwo.split_img_channels(show_kp1)
    rgb_show_kp1 = np.dstack([r,g,b]) # rwo.merge_img_channels(r,g,b)
    
    # rgb, not bgr
    if show_figure:
        plt.imshow(rgb_show_kp1)
        plt.show() 
        plt.close()

    b, g, r = np.dsplit(show_kp2, 3) # rwo.split_img_channels(show_kp2)
    rgb_show_kp2 = np.dstack([r,g,b]) # rwo.merge_img_channels(r,g,b) 
    if show_figure:
        plt.imshow(rgb_show_kp2)
        plt.show()
        plt.close()
    
    return kp1, des1, kp2, des2
    
def find_matches_FlannBasedMatcher_opencv(kp1, des1, kp2, des2):
    MIN_MATCH_COUNT = 20
    FLANN_INDEX_KDTREE = 1 # algorithm
    #FLANN_INDEX_LINEAR = 0
    #FLANN_INDEX_KDTREE = 1
    #FLANN_INDEX_KMEANS = 2
    #FLANN_INDEX_COMPOSITE = 3
    #FLANN_INDEX_KDTREE_SINGLE = 4
    #FLANN_INDEX_HIERARCHICAL = 5
    #FLANN_INDEX_LSH = 6
    #FLANN_INDEX_SAVED = 254
    #FLANN_INDEX_AUTOTUNED = 255
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    
    # Alternative approach: ussing BFMatcher with default params. WORST RESULTS
    #bf = cv2.BFMatcher() # worst results
    #matches = bf.knnMatch(des1,des2,k=2)
    
    return matches

# filter
def extract_good_matches(matches, factor = 0.8):
    best_matches = []
    for m, n in matches:
        if m.distance < factor*n.distance: 
            best_matches.append(m)
    return best_matches

def compute_M_homography_array_coefficients(kp1, kp2, good):
    # compute M coefficients
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    #print(M) # M homograpy array
    return M

def apply_M_transform(M, point):
    ''''
    Function to apply the M homography matrix to a list or np.darray of points
    
    Parameters:    M       np.darray   M homography array coefficients
                   point   list os np.darray with the input image points coordinates 
    Returns        dst     list with the transformed coordinates
    '''
    point = np.float32(point).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(point, M)
    dst = list([int(dst[0][0][0]), int(dst[0][0][1])])
    return dst 

def compute_size_rect(corners, checker_name):
    x1, y1 = corners["TopLeft"]
    x2, y2 = corners["TopRight"]
    dist = cop.euclidean_distance_between_2D_points(x1, y1, x2, y2)
    if "XRCCPP" or "CCPPV" or "CCPP2" in checker_name:
        size_rect = int((dist/6)*0.15) 
    elif "CCC" in checker_name:
        size_rect = int((dist/6)*0.4) 
    elif "CCDSG" in checker_name:
        size_rect = int((dist/14)*0.15) 
    elif "SCK100" in checker_name:
        size_rect = int((dist/9)*0.3) 
    
    return size_rect
    
def draw_border(img, M, corners, colour = (0,0,255), thickness = 3, show_image=False):
    sample_img = copy.copy(img)
    pts = np.float32(corners).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts, M) # into img system coordinates
    dst = np.int32(dst)
    sample_img = cv2.rectangle(sample_img, (dst[0][0][0], dst[0][0][1]), (dst[1][0][0], dst[1][0][1]), colour, thickness)
    
    b, g, r = np.dsplit(sample_img, 3) # rwo.split_img_channels(sample_img)
    rgb_sample_img = np.dstack([r,g,b]) # rwo.merge_img_channels(r, g, b)  
    if show_image:
        plt.imshow(rgb_sample_img)
        plt.show()
        plt.close()

def colourchecker_patch_detection(rgb_array, opencv_descriptor = "SIFT", checker_name = "XRCCPP_24", show_image=False):
    coolpi_dir = get_abs_path_coolpi()
    valid_colour_checker = ["CCC", "CCDSG", "CCPP2_24", "CCPP2_26", "CCPPV_24", "CCPPV_3", "SCK100_48", "XRCCPP_24", "XRCCPP_26"]
    valid_opencv_descriptor = ["SIFT", "SURF", "ORB"]

    if checker_name not in valid_colour_checker:
        raise ColourCheckerError("Colour checker not implemented")
    if opencv_descriptor not in valid_opencv_descriptor:
        raise ClassMethodError("OpenCv descriptor not implemented")

    if checker_name == "CCC":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "CCC.jpg"])
        corners = {"TopLeft":[22.41,37.19], "TopRight":[936.35,36.11], "BottomRight":[936.93,634.95], "BottomLeft":[22.09,633.28]}
    elif checker_name == "CCDSG":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "CCDSG.jpg"])
        corners = {"TopLeft":[90.42,54.14], "TopRight":[1122.36,55.34], "BottomRight":[1122.56,798.33], "BottomLeft":[87.41,800.21]}
    elif checker_name == "CCPP2_24":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "CCPP2.jpg"])
        corners = {"TopLeft":[234.76,258.57], "TopRight":[232.56,33.87], "BottomRight":[381.75,32.85], "BottomLeft":[383.42,257.87]}
    elif checker_name == "CCPP2_26":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "CCPP2.jpg"])
        corners = {"TopLeft":[23.38,274.76], "TopRight":[22.26,19.39], "BottomRight":[162.83,19.39], "BottomLeft":[165.40,273.09]}    
    elif checker_name == "CCPPV_24":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "CCPPV.jpg"])
        corners = {"TopLeft":[858.87,951.87], "TopRight":[859.95,160.25], "BottomRight":[1385.45,160.83], "BottomLeft":[1384.71,951.52]}
    elif checker_name == "CCPPV_3":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "CCPPV.jpg"])
        corners = {"TopLeft":[116.95,939.93], "TopRight":[119.19,173.36], "BottomRight":[618.5,174.09], "BottomLeft":[617.25,942.28]}
    elif checker_name == "SCK100_48":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "SCK100.jpg"])
        corners = {"TopLeft":[35.53,99.82], "TopRight":[1897.57,102.58], "BottomRight":[1893.53,1337.18], "BottomLeft":[40.68,1331.81]}    
    elif checker_name == "XRCCPP_24":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "XRCCPP.jpg"])
        corners = {"TopLeft":[897.54,1010.47], "TopRight":[898.63,169.59], "BottomRight":[1463.83,170.22], "BottomLeft":[1465.50,1009.44]}
    elif checker_name == "XRCCPP_26":
        path_checker = os.path.join(coolpi_dir, *["data", "colourchecker", "img", "XRCCPP.jpg"])
        corners = {"TopLeft":[124.19, 1056.03], "TopRight":[129.88, 124.85], "BottomRight":[634.35,125.85], "BottomLeft":[634.55,1058.24]} 
        
    else:
        return None
    
    checker_bgr_img = cv2.imread(path_checker, -1) # bgr
    r,g,b = np.dsplit(rgb_array, 3) # rwo.split_img_channels(rgb_array)
    bgr_img = np.dstack([b,g,r]) # rwo.merge_img_channels(b,g,r)

    kp1, des1, kp2, des2 = feature_detection_sift_opencv(checker_bgr_img, bgr_img)
    matches = find_matches_FlannBasedMatcher_opencv(kp1, des1, kp2, des2)
    good = extract_good_matches(matches)

    if len(good) >= int(len(matches)/15):
        M = compute_M_homography_array_coefficients(kp1, kp2, good)
        #corners_draw = [corners["TopLeft"], corners["BottomRight"]] # checker_bgr_img.shape[1], 0], [0, checker_bgr_img.shape[0]]] # LeftTop / BottomRight
        #draw_border(bgr_img, M, corners_draw, show_image=False)
        
        # apply M to corners
        m_corners={}
        for key in corners.keys():
            point = corners[key]
            dst = apply_M_transform(M, point)
            m_corners[key] = dst
        return m_corners
    else:
        return None