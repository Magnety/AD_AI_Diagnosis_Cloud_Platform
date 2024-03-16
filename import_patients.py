# Create your views here.
import os
import SimpleITK as sitk
import numpy as np
from PIL import Image
import base64
import cv2
from io import BytesIO
from datetime import datetime, date, timedelta
import matlab
import matlab.engine
engine = matlab.engine.start_matlab()  # 启动matlab engine
engine.calcROI_AAL_DTI(nargout=0)



