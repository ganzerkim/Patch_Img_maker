# -*- coding: utf-8 -*-
"""
Created on Wed May 18 09:32:02 2022

@author: Mingeon Kim, CT/MI Research Collaboration Scientist, SIEMENS Healthineers, Korea
"""

#%%
import numpy as np
import matplotlib.pyplot as plt
import pydicom
from os import listdir
from os.path import isfile, join
import os
import cv2
#import SimpleITK as sitk
import pydicom._storage_sopclass_uids
import cv2
from PIL import Image

# metadata
fileMeta = pydicom.Dataset()
fileMeta.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
fileMeta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
fileMeta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

# 선택 정렬
def selection_sort(dicom):
    # 코드를 입력하세요.
    
    for i in range(len(dicom)):
                
        for j in range(i + 1, len(dicom)):
            value = dicom[j].SliceLocation
            value_d = dicom[j]
            if value < dicom[i].SliceLocation:
                                
                temp = dicom[i]
                dicom[i] = value_d
                dicom[j] = temp
                
        print(i)
    return dicom

mask_path = "C:/Users/User/Desktop/DL_Radiomics/mask"
img_path = "C:/Users/User/Desktop/DL_Radiomics/image"

msk_path_tmp = []
msk_name_tmp = []
msk_img_tmp = []

for (msk_path, dir, msk_files) in os.walk(mask_path):
    for filename in msk_files:
        ext = os.path.splitext(filename)[-1]
        
        if ext == '.dcm' or '.IMA':
            print("%s/%s" % (msk_path, filename))
            msk_path_tmp.append(msk_path)
            msk_name_tmp.append(filename)

msk_dcm_tmp = []
msk_label = []

for i in range(len(msk_path_tmp)):
    msk_dcm_p = pydicom.dcmread(msk_path_tmp[i] + '/' + msk_name_tmp[i], force = True)
    msk_dcm_tmp.append(msk_dcm_p)
    ccc = msk_dcm_p.pixel_array
    lll = msk_dcm_p.SegmentSequence[0].SegmentDescription
    msk_img_tmp.append(ccc)
    msk_label.append(lll)
    
msk_array = np.array(msk_img_tmp)
arr_msk_array = msk_array

# msk_array = np.array(msk_img_tmp)[0, :, :, :]
# arr_msk_array = msk_array[:, :, :, np.newaxis]

reverse = arr_msk_array[:, ::-1, :, :]
# pp = np.where(reverse == 1)

              
###################################################################
path_tmp = []
name_tmp = []
img_tmp = []

for (path, dir, files) in os.walk(img_path):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        
        if ext == '.dcm' or '.IMA':
            print("%s/%s" % (path, filename))
            path_tmp.append(path)
            name_tmp.append(filename)

dcm_tmp = []

for i in range(len(path_tmp)):
    dcm_p = pydicom.dcmread(path_tmp[i] + '/' + name_tmp[i], force = True)
    dcm_tmp.append(dcm_p)
    # ccc = dcm_p.pixel_array
    # img_tmp.append(ccc)

sort_dcm_tmp = selection_sort(dcm_tmp)

for ii in range(len(sort_dcm_tmp)):
    ccc = sort_dcm_tmp[ii].pixel_array
    img_tmp.append(ccc)

img_array = np.array(img_tmp)
arr_img_array = img_array

#######################################################################
def padding(img, set_size):
    h,w = img.shape

    if max(h, w) > set_size:
        return img

    delta_w = set_size - w
    delta_h = set_size - h
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    new_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    return new_img


#########################################################################
msk_roi_img = []
patch_img = []

idx = 0
dsizex = 400
dsizey = 400
marginx = 5
marginy = 5

####resize version
for idx in range(len(reverse[:, 0, 0, 0])):
    check = arr_img_array * reverse[idx, :, :, :]
    msk_roi_img.append(check)
    
    patch_slice = []
    
    for iidx in range(len(check[:, 0, 0])):
        
        if np.max(check[iidx, :, :]) != 0:
            pos = np.where(check[iidx, :, :] != 0)
            patch = check[iidx, np.min(pos[0]) - marginx:np.max(pos[0]) + marginx, np.min(pos[1]) - marginy:np.max(pos[1]) + marginy]
            res = cv2.resize(patch, dsize=(dsizex, dsizey), interpolation=cv2.INTER_LINEAR)
            patch_slice.append(res)
        else:
            pass
    
    patch_img.append(patch_slice)

####pading version    
for idx in range(len(reverse[:, 0, 0, 0])):
    check = arr_img_array * reverse[idx, :, :, :]
    msk_roi_img.append(check)
    
    patch_slice = []
    
    for iidx in range(len(check[:, 0, 0])):
        
        if np.max(check[iidx, :, :]) != 0:
            pos = np.where(check[iidx, :, :] != 0)
            patch = check[iidx, np.min(pos[0]) - marginx:np.max(pos[0]) + marginx, np.min(pos[1]) - marginy:np.max(pos[1]) + marginy]
            res = padding(patch, dsizex)
            patch_slice.append(res)
        else:
            pass
    
    patch_img.append(patch_slice)

###################################################################

save_path = 'C:/Users/User/Desktop/DL_Radiomics/result'


for itr in range(len(patch_img)):
    result_path = save_path + '/' + str(msk_label[itr])
    if not(os.path.exists(result_path)):
        os.makedirs(result_path + '/png')
        os.makedirs(result_path + '/npy')
    p_slices = []
    for seg in range(len(patch_img[itr])):
        im = Image.fromarray(patch_img[itr][seg])
        p_slices.append(patch_img[itr][seg])
        
        plt.imsave(result_path + '/png/patch'+ str(itr)+ '_' + str(seg) + '.png', im, cmap ='gray')
    
    np.save(result_path + '/npy/' +str(itr) + '.npy', p_slices)
    
    print(itr)
        

             

#####################################################

# test_img = check[35, :, :, 0]

# # plt.imshow(test_img[141:180, 209:244])
# pos = np.where(test_img != 0)

# patch_img = test_img[np.min(pos[0]):np.max(pos[0]), np.min(pos[1]):np.max(pos[1])]
# plt.imshow(patch_img, cmap='gray')


# res = cv2.resize(patch_img, dsize=(100, 100), interpolation=cv2.INTER_LINEAR)
# plt.imshow(res, cmap='gray')

####################################################



