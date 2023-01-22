import numpy as np
import cv2.ximgproc as xip
import cv2
import random
random.seed(999)

def computeDisp(Il, Ir, max_disp):
    h, w, ch = Il.shape
    labels = np.zeros((h, w), dtype=np.float32)
    Il = Il.astype(np.float32)
    Ir = Ir.astype(np.float32)
    sigma_r, sigma_s, WMF_r = 4, 11, 11
#     sigma_r, sigma_s, WMF_r = 15, 5, 15

    # >>> Cost Computation
    # TODO: Compute matching cost
    # [Tips] Census cost = Local binary pattern -> Hamming distance
    # [Tips] Set costs of out-of-bound pixels = cost of closest valid pixel  
    # [Tips] Compute cost both "Il to Ir" and "Ir to Il" for later left-right consistency
    
    # transform local binary pattern
    # zero padding
    imgL = cv2.copyMakeBorder(Il,1,1,1,1, cv2.BORDER_CONSTANT, value=0)
    imgR = cv2.copyMakeBorder(Ir,1,1,1,1, cv2.BORDER_CONSTANT, value=0)
    # zero matrix with shape (9, 290, 386, 3) to record 9 binary values
    imgL_bin = np.zeros((9, *imgL.shape))
    imgR_bin = np.zeros((9, *imgR.shape))
    idx = 0
    # rolling the whole image with 3x3 window
    for x in range(-1, 2):
        for y in range(-1, 2):
            # assign "1" if the value of central pixel is greater than peripheral pixel
            maskL = (imgL > np.roll(imgL, [y, x], axis=[0, 1]))
            imgL_bin[idx][maskL] = 1
            maskR = (imgR > np.roll(imgR, [y, x], axis=[0, 1]))
            imgR_bin[idx][maskR] = 1
            idx += 1
    # remove the padded border
    imgL_bin = imgL_bin[:, 1:-1, 1:-1] 
    imgR_bin = imgR_bin[:, 1:-1, 1:-1]

    # >>> Cost Aggregation
    # TODO: Refine the cost according to nearby costs
    # [Tips] Joint bilateral filter (for the cost of each disparty)
    # create cost volumes of shape (h,w,N+1) to record Hamming distances under N+1 disparity
    l_cost_volume = np.zeros((max_disp+1, h, w))
    r_cost_volume = np.zeros((max_disp+1, h, w))
    wndw_size = -1 # calculate window size from spatial kernel
    for d in range(max_disp+1):
        l_shift = imgL_bin[:, :, d:].astype(np.uint32)
        r_shift = imgR_bin[:, :, :w-d].astype(np.uint32)
        #compute Hamming distance with XOR. ie. 00111010^10111000=10000010
        cost = np.sum(l_shift^r_shift, axis=0)
        cost = np.sum(cost, axis=2).astype(np.float32) # sum up costs of different channels
        # left-to-right check
        # fill left border with border_replicate
        l_cost = cv2.copyMakeBorder(cost, 0, 0, d, 0, cv2.BORDER_REPLICATE)
        l_cost_volume[d] = xip.jointBilateralFilter(Il, l_cost, wndw_size, sigma_r, sigma_s)
        # right-to-left check
        # fill right border with border_replicate
        r_cost = cv2.copyMakeBorder(cost, 0, 0, 0, d, cv2.BORDER_REPLICATE)
        r_cost_volume[d] = xip.jointBilateralFilter(Ir, r_cost, wndw_size, sigma_r, sigma_s)

    # >>> Disparity Optimization
    # TODO: Determine disparity based on estimated cost.
    # [Tips] Winner-take-all
    l_disp_map = np.argmin(l_cost_volume, axis=0)
    r_disp_map = np.argmin(r_cost_volume, axis=0)
    
    # >>> Disparity Refinement
    # TODO: Do whatever to enhance the disparity map
    # [Tips] Left-right consistency check -> Hole filling -> Weighted median filtering
    lr_check = np.zeros((h, w), dtype=np.float32)
    x, y = np.meshgrid(range(w),range(h))
    r_x = (x - l_disp_map) # x-DL(x,y)
    mask1 = (r_x >= 0) # coordinate should be non-negative integer
    l_disp = l_disp_map[mask1]
    r_disp = r_disp_map[y[mask1], r_x[mask1]]
    mask2 = (l_disp == r_disp) # check if DL(x,y) = DR(x-DL(x,y))
    lr_check[y[mask1][mask2], x[mask1][mask2]] = l_disp_map[mask1][mask2]

    # hole filling
    # pad maximum disparity for the holes in boundary
    lr_check_pad = cv2.copyMakeBorder(lr_check,0,0,1,1, cv2.BORDER_CONSTANT, value=max_disp)
    l_labels = np.zeros((h, w), dtype=np.float32)
    r_labels = np.zeros((h, w), dtype=np.float32)
    for y in range(h):
        for x in range(w):
            idx_L, idx_R = 0, 0
            # 𝐹𝐿, the disparity map filled by closest valid disparity from left
            while lr_check_pad[y, x+1-idx_L] == 0:
                idx_L += 1
            l_labels[y, x] = lr_check_pad[y, x+1-idx_L]
            # 𝐹𝑅, the disparity map filled by closest valid disparity from right
            while lr_check_pad[y, x+1+idx_R] == 0:
                idx_R += 1
            r_labels[y, x] = lr_check_pad[y, x+1+idx_R]
    # Final filled disparity map 𝐷 = min(𝐹𝐿 , 𝐹𝑅) (pixel-wise minimum)
    labels = np.min((l_labels, r_labels), axis=0)

    # weighted median filter
    labels = xip.weightedMedianFilter(Il.astype(np.uint8), labels, WMF_r)

    return labels.astype(np.uint8)
    