import os
import numpy as np
import cv2 as cv


def shot_cut(frames):
    num = frames.shape[0]
    threshold = 50
    # count = np.zeros(num)

    pre_frame = frames[0]
    pre_frame = cv.cvtColor(pre_frame, cv.COLOR_BGR2GRAY)
    pre_frame = cv.resize(pre_frame, (8, 8))
    pre_frame = np.array(pre_frame)

    diff = []
    for i in range(1, num):
        # print(i)
        now_frame = frames[i]
        now_frame = cv.cvtColor(now_frame, cv.COLOR_BGR2GRAY)

        now_frame = cv.resize(now_frame, (8, 8))
        now_frame = np.array(now_frame.reshape(8, 8))
        count = 0
        for j in range(8):
            for k in range(8):
                # print(pre_frame[j][k])
                if abs(pre_frame[j][k] - now_frame[j][k]) > 20:
                    count = count + 1
        diff.append(count)
        pre_frame = now_frame

    cut_id = []
    for i in range(1, num - 2):
        print(diff[i])
        print(threshold)
        print("^^^")
        if diff[i] > threshold:
            cut_id.append(i)

    return cut_id


# 从视频读入所有帧
def read_img(sourcePath):  # 便于算法学习
    cap = cv.VideoCapture(sourcePath)
    # cap = sourcePath
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


# 主函数
if __name__ == '__main__':
    # 视频路径 输出关键帧路径
    sourcePath = 'popo.mp4'
    outputDir = './result2/'
    outputPath = 'output.mp4'

    if not os.path.exists(outputDir):  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(outputDir)

    path = "popo2.mp4"
    file = "output.mp4"
    videoCapture = cv.VideoCapture(path)
    fps = videoCapture.get(cv.CAP_PROP_FPS)
    width = videoCapture.get(cv.CAP_PROP_FRAME_WIDTH)
    height = videoCapture.get(cv.CAP_PROP_FRAME_HEIGHT)
    videoWriter = cv.VideoWriter(outputPath, cv.VideoWriter_fourcc('m', 'p', '4', 'v'), fps,
                                 (int(width), int(height)))

    videoCapture.release()

    # 从视频中读入所有帧
    frames = read_img(sourcePath)
    cut_id = shot_cut(frames)
    print(cut_id)

    # for i in range(1, 200):
    #     # img = cv.imread('%d'.jpg % i)
    #     img = frames[i]
    #     videoWriter.write(img)
    cut_id = np.array(cut_id)

    if cut_id.size == 0:
        print("There is not cut id")
        exit(-1)

    index = 0
    shot_index = 1
    id_index = 0
    id_now = cut_id[id_index]
    # print(index)
    # print(frames.shape[0])
    # print(id_index)
    # print(cut_id.size)
    while True:
        # print(index)
        # print(frames.shape[0])
        # print(id_index)
        # print(cut_id.size)
        if index >= frames.shape[0]:
            break
        # print("test")

        if id_index >= cut_id.size:
            id_now = frames.shape[0] - 1
        else:
            id_now = cut_id[id_index]

        shot_name = outputDir + "shot_" + str(shot_index) + ".mp4"
        print(shot_name)
        videoWriter = cv.VideoWriter(shot_name, cv.VideoWriter_fourcc('m', 'p', '4', 'v'), fps,
                                     (int(width), int(height)))

        while index <= id_now:
            videoWriter.write(frames[index])
            index = index + 1

        videoWriter.release()
        shot_index = shot_index + 1
        id_index = id_index + 1
        # id_now = cut_id[id_index]

    videoWriter.release()
    # # 读入视频
    # cap = cv.VideoCapture(str(sourcePath))
    # # 写出所有关键帧图像
    # success, frame = cap.read()
    # idx = 0
    # while (success):
    #     if idx in key_id:
    #         name = "keyframe_" + str(idx) + ".jpg"
    #         cv.imwrite(outputDir + name, frame)
    #         # key_id.remove(idx)
    #     idx = idx + 1
    #     success, frame = cap.read()
    # cap.release()
    # # cv.waitKey()
