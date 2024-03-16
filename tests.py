
import os
import shutil
import matlab
import matlab.engine

import SimpleITK as sitk
import numpy as np
from PIL import Image
import base64
import cv2
from io import BytesIO
from datetime import datetime, date, timedelta

from CMFFN.main import run_model as run_model_advscn
from CMFFN.main1 import run_model as run_model_mcivscn
from CMFFN.main2 import run_model as run_model_smcivspmci
import pandas as pd

import zipfile
name = 'T1_MPRAGE_SAG_FS_P2_ISO_0009.zip'
mri_add = "I:/AD_cloudsys/dataset" + "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/"+name
zip_add = "I:/AD_cloudsys/dataset" + "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/" +name.split('.')[0]
nii_add = "I:/AD_cloudsys/dataset" + "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/" + \
          name.split('.')[0] + '.nii'
zip_file = zipfile.ZipFile(mri_add)
if os.path.isdir(zip_add):
    pass
else:
    os.mkdir(zip_add)
for names in zip_file.namelist():
    zip_file.extract(names, zip_add + '/')
zip_file.close()

reader = sitk.ImageSeriesReader()
dicom_names = reader.GetGDCMSeriesFileNames(zip_add+'/'+name.split('.')[0])
reader.SetFileNames(dicom_names)
image2 = reader.Execute()
# 2.将整合后的数据转为array，并获取dicom文件基本信息
image_array = sitk.GetArrayFromImage(image2)  # z, y, x
origin = image2.GetOrigin()  # x, y, z
spacing = image2.GetSpacing()  # x, y, z
direction = image2.GetDirection()  # x, y, z
# 3.将array转为img，并保存为.nii.gz
image3 = sitk.GetImageFromArray(image_array)
image3.SetSpacing(spacing)
image3.SetDirection(direction)
image3.SetOrigin(origin)
sitk.WriteImage(image3, nii_add)

engine = matlab.engine.start_matlab()  # 启动matlab engine
engine.calcACPC(nii_add + ',1', nargout=0)
engine.spmVBM_par(nii_add + ',1', nargout=0)
