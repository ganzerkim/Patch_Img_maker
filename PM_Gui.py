# -*- coding: utf-8 -*-
"""
Created on Fri May 20 11:43:53 2022

@author: Mingeon Kim, CT/MI Research Collaboration Scientist, SIEMENS Healthineers, Korea
"""


import pydicom
import numpy as np
import matplotlib.pylab as plt
from os import listdir
from os.path import isfile, join
import os
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from tkinter import * # __all__
from tkinter import filedialog
from PIL import Image

import cv2
import pydicom._storage_sopclass_uids

# from PyInstaller.utils.hooks import collect_submodules

# # hiddenimports = collect_submodules('pydicom.encoders')
# # hiddenimports.extend(collect_submodules('pydicom.overlays'))
# # hiddenimports.extend(collect_submodules('pydicom.overlay_data_handlers'))

# hiddenimport = collect_submodules('pydicom')

# metadata
fileMeta = pydicom.Dataset()
fileMeta.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
fileMeta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
fileMeta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

root = Tk()
root.title("SIEMENS Radiomics Patch Image Maker Tool")

def add_file():
    files = filedialog.askdirectory(title="추가할 파일경로를 선택하세요", \
        initialdir=r".\Desktop")
        # 최초에 사용자가 지정한 경로를 보여줌

    # 사용자가 선택한 파일 목록
    list_file.insert(END, files)

# 선택 삭제
def del_file():
    #print(list_file.curselection())
    for index in reversed(list_file.curselection()):
        list_file.delete(index)


def add_file_2():
    files = filedialog.askdirectory(title="추가할 파일경로를 선택하세요", \
        initialdir=r".\Desktop")
        # 최초에 사용자가 지정한 경로를 보여줌

    # 사용자가 선택한 파일 목록
    list_file_2.insert(END, files)

# 선택 삭제
def del_file_2():
    #print(list_file.curselection())
    for index in reversed(list_file_2.curselection()):
        list_file_2.delete(index)
        

# 추사 경로 (폴더)
def browse_dest_loadpath():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # 사용자가 취소를 누를 때
        # print("폴더 선택 취소")
        return
    #print(folder_selected)
    txt_dest_loadpath.delete(0, END)
    txt_dest_loadpath.insert(0, folder_selected)


# 저장 경로 (폴더)
def browse_dest_savepath():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # 사용자가 취소를 누를 때
        # print("폴더 선택 취소")
        return
    #print(folder_selected)
    txt_dest_savepath.delete(0, END)
    txt_dest_savepath.insert(0, folder_selected)
    
    
def hash_acc(num, length, sideID):
   try:
       siteID = str.encode(sideID)
       num = str.encode(num)
                              # hash
       m = hmac.new(siteID, num, hashlib.sha256).digest()
                              #convert to dec
       m = str(int(binascii.hexlify(m),16))
                              #split till length
       m=m[:length]
       return m
   except Exception as e:
          print("Something went wrong hashing a value :(")
          return

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


def patch_maker():
    
    try:
        
        global i, ii, iii, iidx, itr, check, sort_dcm_tmp
        option_type = cmb_width.get()
        # if option_type == "Resize":
        mask_path = list_file.get(0, END)[0]
        img_path = list_file_2.get(0, END)[0]
        
        # print(mask_path[0])
        # print(images_path[0])
        msk_path_tmp = []
        msk_name_tmp = []
        msk_img_tmp = []
        path_tmp = []
        name_tmp = []
        img_tmp = []
        msk_roi_img = []
        patch_img = []

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

            progress = (i + 1) / len(msk_path_tmp) * 100 # 실제 percent 정보를 계산
            p_var.set(progress)
            progress_bar.update()
            
        msk_array = np.array(msk_img_tmp)
        arr_msk_array = msk_array

        # msk_array = np.array(msk_img_tmp)[0, :, :, :]
        # arr_msk_array = msk_array[:, :, :, np.newaxis]

        reverse = arr_msk_array[:, ::-1, :, :]
        
       

        for (path, dir, files) in os.walk(img_path):
            for filename in files:
                ext = os.path.splitext(filename)[-1]
                
                if ext == '.dcm' or '.IMA':
                    print("%s/%s" % (path, filename))
                    path_tmp.append(path)
                    name_tmp.append(filename)

        dcm_tmp = []

        for ii in range(len(path_tmp)):
            dcm_p = pydicom.dcmread(path_tmp[ii] + '/' + name_tmp[ii], force = True)
            dcm_tmp.append(dcm_p)
            # ccc = dcm_p.pixel_array
            # img_tmp.append(ccc)
            progress = (i + ii + 1) / (len(msk_path_tmp) + len(path_tmp)) * 100 # 실제 percent 정보를 계산
            p_var.set(progress)
            progress_bar.update()

        sort_dcm_tmp = selection_sort(dcm_tmp)

        for iii in range(len(sort_dcm_tmp)):
            ccc = sort_dcm_tmp[iii].pixel_array
            img_tmp.append(ccc)
            progress = (i + ii + iii + 1) / (len(msk_path_tmp) + len(path_tmp) + len(sort_dcm_tmp)) * 100 # 실제 percent 정보를 계산
            p_var.set(progress)
            progress_bar.update()

        img_array = np.array(img_tmp)
        arr_img_array = img_array
        


        idx = 0
        dsizex = int(txt_studynumb.get())
        dsizey = int(txt_studynumb.get())
        marginx = int(txt_studyname.get())
        marginy = int(txt_studyname.get())
           
        if option_type == "Resize":
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
                
                progress = (i + ii + iii + iidx + 1) / (len(msk_path_tmp) + len(path_tmp) + len(sort_dcm_tmp) + len(check[:, 0, 0])) * 100 # 실제 percent 정보를 계산
                p_var.set(progress)
                progress_bar.update()
                
                patch_img.append(patch_slice)
                
        elif option_type == "Zero-padding":
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
                    
                progress = (i + ii + iii + iidx + 1) / (len(msk_path_tmp) + len(path_tmp) + len(sort_dcm_tmp) + len(check[:, 0, 0])) * 100 # 실제 percent 정보를 계산
                p_var.set(progress)
                progress_bar.update()
                
                patch_img.append(patch_slice)
                
        save_path = txt_dest_savepath.get() + "/result"
        print(save_path)
        
        if not(os.path.exists(save_path)):
            os.mkdir(save_path)
            
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
            
            progress = (itr + 1) / len(patch_img) * 100 # 실제 percent 정보를 계산
            p_var.set(progress)
            progress_bar.update()
            
            
            print(itr)
        
        # for remove_path in mask_path:
        #     shutil.rmtree(remove_path)
        msgbox.showinfo("알림", "Path data 생성이 완료되었습니다! Result 폴더를 확인해주세요.")
        
    except Exception as err: # 예외처리
        msgbox.showerror("에러", err + ", Research Scientist에게 문의해주세요!")

# 시작
def start():
    # 각 옵션들 값을 확인
    # print("가로넓이 : ", cmb_width.get())
    # print("간격 : ", cmb_space.get())
    # print("포맷 : ", cmb_format.get())

    # 파일 목록 확인
    if list_file.size() == 0:
        msgbox.showwarning("경고", "Mask 폴더 경로를 추가해주세요")
        return

    # 저장 경로 확인
    if len(txt_dest_savepath.get()) == 0:
        msgbox.showwarning("경고", "저장 경로를 선택해주세요")
        return

    # 이미지 통합 작업
    patch_maker()



photo = PhotoImage(file="./pics/xx.png")
label2 = Label(root, image=photo)
label2.pack()

# 파일 프레임 (파일 추가, 선택 삭제)
file_frame = Frame(root)
file_frame.pack(fill="x", padx=5, pady=5) # 간격 띄우기

btn_add_file = Button(file_frame, padx=5, pady=5, width=20, text="Mask Dicom 폴더추가", command=add_file)
btn_add_file.pack(side="left")

btn_del_file = Button(file_frame, padx=5, pady=5, width=20, text="선택삭제", command=del_file)
btn_del_file.pack(side="right")

# 리스트 프레임
list_frame = Frame(root)
list_frame.pack(fill="both", padx=5, pady=5)

scrollbar = Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

list_file = Listbox(list_frame, selectmode="extended", height=0, yscrollcommand=scrollbar.set)
list_file.pack(side="right", fill="both", expand=True)
scrollbar.config(command=list_file.yview)



# 파일 프레임 (파일 추가, 선택 삭제)
file_frame_2 = Frame(root)
file_frame_2.pack(fill="x", padx=5, pady=5) # 간격 띄우기

btn_add_file_2 = Button(file_frame_2, padx=5, pady=5, width=20, text="Origianl Dicom 폴더추가", command=add_file_2)
btn_add_file_2.pack(side="left")

btn_del_file_2 = Button(file_frame_2, padx=5, pady=5, width=20, text="선택삭제", command=del_file_2)
btn_del_file_2.pack(side="right")

# 리스트 프레임
list_frame_2 = Frame(root)
list_frame_2.pack(fill="both", padx=5, pady=5)

scrollbar_2 = Scrollbar(list_frame_2)
scrollbar_2.pack(side="right", fill="y")

list_file_2 = Listbox(list_frame_2, selectmode="extended", height=0, yscrollcommand=scrollbar_2.set)
list_file_2.pack(side="left", fill="both", expand=True)
scrollbar_2.config(command=list_file_2.yview)


# # 추가 경로 프레임
# loadpath_frame = LabelFrame(root, text="Source data 경로")
# loadpath_frame.pack(fill="x", padx=5, pady=5, ipady=5)

# txt_dest_loadpath = Entry(loadpath_frame)
# txt_dest_loadpath.pack(side="left", fill="x", expand=True, padx=5, pady=5, ipady=4) # 높이 변경

# btn_dest_loadpath = Button(loadpath_frame, text="찾아보기", width=10, command=browse_dest_loadpath)
# btn_dest_loadpath.pack(side="right", padx=5, pady=5)

# 저장 경로 프레임
savepath_frame = LabelFrame(root, text="저장경로")
savepath_frame.pack(fill="x", padx=5, pady=5, ipady=5)

txt_dest_savepath = Entry(savepath_frame)
txt_dest_savepath.pack(side="left", fill="x", expand=True, padx=5, pady=5, ipady=4) # 높이 변경

btn_dest_savepath = Button(savepath_frame, text="찾아보기", width=10, command=browse_dest_savepath)
btn_dest_savepath.pack(side="right", padx=5, pady=5)

# 옵션 프레임
frame_option = LabelFrame(root, text="*Mask data를 생성하실 옵션과 값을 입력해주세요.*")
frame_option.pack(padx=15, pady=15, ipady=1)
################################################################

# 실행할 옵션 선택
lbl_option = Label(frame_option, text="실행옵션", width=8)
lbl_option.pack(side="left", padx=5, pady=5)

# 실행 옵션 콤보
opt_width = ["Resize", "Zero-padding"]
cmb_width = ttk.Combobox(frame_option, state="readonly", values=opt_width, width=10)
cmb_width.current(0)
cmb_width.pack(side="left", padx=5, pady=5)

# Study number 옵션
lbl_studynumb = Label(frame_option, text="Size", width = 10)
lbl_studynumb.pack(side="top", padx = 5, pady = 0, fill="both", expand=True)

txt_studynumb = Entry(frame_option, width=5)
txt_studynumb.pack(pady = 5)
txt_studynumb.insert(END, "400")

# 익명화 이름 옵션
lbl_studyname = Label(frame_option, text="Margin", width = 10)
lbl_studyname.pack(side="top", padx = 5, pady = 5, fill="both", expand=True)

txt_studyname = Entry(frame_option, width=5)
txt_studyname.pack(pady = 5)
txt_studyname.insert(END, "5")


##################################################################
# 진행 상황 Progress Bar
frame_progress = LabelFrame(root, text="진행상황")
frame_progress.pack(fill="x", padx=5, pady=5, ipady=5)

p_var = DoubleVar()
progress_bar = ttk.Progressbar(frame_progress, maximum=100, variable=p_var)
progress_bar.pack(fill="x", padx=5, pady=5)

# 실행 프레임
frame_run = Frame(root)
frame_run.pack(fill="x", padx=5, pady=5)

btn_close = Button(frame_run, padx=5, pady=5, text="닫기", width=12, command=root.quit)
btn_close.pack(side="right", padx=5, pady=5)

btn_start = Button(frame_run, padx=5, pady=5, text="시작", width=12, command=start)
btn_start.pack(side="right", padx=5, pady=5)

root.resizable(False, False)
root.mainloop()