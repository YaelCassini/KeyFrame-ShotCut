# 特征转变法
import os
import numpy as np
import cv2 as cv


# 从视频读入所有帧
def read_img(sourcePath):  # 便于算法学习
    cap = cv.VideoCapture(sourcePath)
    # 获取帧速率
    Frame_rate = cap.get(5)  # 一秒多少帧
    Frame_number = int(cap.get(7))  # 帧数
    Frame_time = 1000 / Frame_rate  # 一帧多少毫秒

    img_array = []  # 转换后
    index = 0  # 帧序号
    time = 0  # 当前时间
    while (cap.isOpened()):
        # 在当前时间取帧图像
        cap.set(cv.CAP_PROP_POS_MSEC, time)
        ret, img = cap.read()  # 获取图像
        if not ret:
            break
        img_array.append(img)
        time += Frame_time
        index += 1
        if index >= Frame_number:
            break
        if index % 50 == 0:
            print("当前帧序号：" + str(index))
    img_array = np.array(img_array)
    # 返回读入的所有帧图像
    return img_array


# 直方图差异
def hist_diff(ahist, bhist):
    s = 0
    for j in range(0, 256):
        s += min(ahist[j], bhist[j])

    d = s / sum(ahist)
    return d


# 帧图像差异
def frame_diff(aframe, bframe):
    # 在三个通道分别取直方图差异，并按照比例权重求和
    r_diff = hist_diff(aframe[0], bframe[0])
    g_diff = hist_diff(aframe[1], bframe[1])
    b_diff = hist_diff(aframe[2], bframe[2])
    r = 0.3
    g = 0.3
    b = 0.4

    # 返回差异结果
    return r * r_diff + g * g_diff + b * b_diff


# 通过直方图特征计算关键帧
def key_frame(frames, threshold):
    frames_number = int(frames.shape[0])
    num = frames_number

    # 如果没有帧图像
    if num == 0:
        print('Sorry, there is no pictures in images folder!')

    # 将第一帧作为关键帧
    key_id = []
    key_id.append(0)
    frame0 = frames[0]

    # 计算第一帧图像的三个通道直方图
    pre_hist = []
    b, g, r = cv.split(frame0)
    pre_histR = cv.calcHist([r], [0], None, [256], [0.0, 255.0])
    pre_histG = cv.calcHist([g], [0], None, [256], [0.0, 255.0])
    pre_histB = cv.calcHist([b], [0], None, [256], [0.0, 255.0])
    prehist = cv.calcHist([frame0], [0], None, [256], [0.0, 255.0])

    pre_hist.append(pre_histR)
    pre_hist.append(pre_histG)
    pre_hist.append(pre_histB)

    # 依次读入帧图像并处理
    for k in range(1, num):
        # 计算当前帧的直方图
        nowframe = frames[k]
        now_hist = []
        b, g, r = cv.split(nowframe)
        now_histR = cv.calcHist([r], [0], None, [256], [0.0, 255.0])
        now_histG = cv.calcHist([g], [0], None, [256], [0.0, 255.0])
        now_histB = cv.calcHist([b], [0], None, [256], [0.0, 255.0])

        now_hist.append(now_histR)
        now_hist.append(now_histG)
        now_hist.append(now_histB)
        nowhist = cv.calcHist([nowframe], [0], None, [256], [0.0, 255.0])

        # 计算当前帧和上一个被确定为关键帧的图像的直方图差异
        now_diff = frame_diff(pre_hist, now_hist)
        print(now_diff)

        # 如果差别小于阈值就将当前帧作为新的关键帧，并记录当前帧序号
        if now_diff < threshold:
            pre_hist = now_hist
            key_id.append(k)
    # 返回所有关键帧序号
    return key_id


# 主函数
if __name__ == '__main__':
    # 视频路径 输出关键帧路径
    sourcePath = 'popo.mp4'
    outputDir = './result2/'
    threshold = 0.75

    if not os.path.exists(outputDir):  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(outputDir)

    # 从视频中读入所有帧
    frames = read_img(sourcePath)
    # 总帧数
    frames_number = int(frames.shape[0])

    # 通过计算直方图特征选取关键帧
    key_id = key_frame(frames, threshold)
    print(key_id)

    # 读入视频
    cap = cv.VideoCapture(str(sourcePath))
    # 写出所有关键帧图像
    success, frame = cap.read()
    idx = 0
    while (success):
        if idx in key_id:
            name = "keyframe_" + str(idx) + ".jpg"
            cv.imwrite(outputDir + name, frame)
            key_id.remove(idx)
        idx = idx + 1
        success, frame = cap.read()
    cap.release()
