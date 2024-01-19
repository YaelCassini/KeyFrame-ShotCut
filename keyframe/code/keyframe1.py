# 帧间差 局部极大值
import os
import cv2 as cv
import numpy as np
from scipy.signal import argrelextrema


# 对绝对帧间差曲线做平滑处理
def smooth(x, window_len=13, window='hanning'):
    # print(len(x), window_len)
    s = np.r_[2 * x[0] - x[window_len:1:-1],
              x, 2 * x[-1] - x[-1:-window_len:-1]]

    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]


if __name__ == "__main__":
    # 局部极大值
    # 视频路径 输出关键帧路径
    sourcePath = 'popo.mp4'
    outputDir = './result1/'
    # 对变化曲线做平滑的窗口大小
    len_window = int(25)

    if not os.path.exists(outputDir):  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(outputDir)

    # 读入视频
    cap = cv.VideoCapture(sourcePath)
    curr_frame = None
    prev_frame = None
    # 储存帧间差
    frame_diffs = []
    success, frame = cap.read()
    i = 0
    while (success):
        # 转化颜色空间
        # luv = cv.cvtColor(frame, cv.COLOR_BGR2LUV)
        curr_frame = frame
        if curr_frame is not None and prev_frame is not None:
            # 求相邻两帧图像的差
            diff = cv.absdiff(curr_frame, prev_frame)
            # 绝对帧间差
            diff_sum = np.sum(diff)
            diff_sum_mean = diff_sum / (diff.shape[0] * diff.shape[1])
            frame_diffs.append(diff_sum_mean)
        prev_frame = curr_frame
        i = i + 1
        success, frame = cap.read()
    cap.release()

    # 计算关键帧
    key_id = []
    diff_array = np.array(frame_diffs)
    # 对绝对帧差曲线做平滑处理（防止局部极大值过多）
    sm_diff_array = smooth(diff_array, len_window)
    key_id = np.asarray(argrelextrema(sm_diff_array, np.greater))[0]


    # 读入视频
    cap = cv.VideoCapture(str(sourcePath))
    # 写出所有关键帧图像
    success, frame = cap.read()
    idx = 0
    while (success):
        if idx in key_id:
            name = "keyframe_" + str(idx) + ".jpg"
            cv.imwrite(outputDir + name, frame)
            # key_id.remove(idx)
        idx = idx + 1
        success, frame = cap.read()
    cap.release()