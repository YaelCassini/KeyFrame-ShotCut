# 设置阈值的聚类
import os
import numpy as np
import cv2 as cv


# 从视频读入所有帧
def read_img(sourcePath):
    cap = cv.VideoCapture(sourcePath)
    # 获取帧速率
    Frame_rate = cap.get(5)  # 一秒多少帧
    Frame_number = int(cap.get(7))  # 帧数
    Frame_time = 1000 / Frame_rate  # 一帧多少毫秒

    len_windows = 0
    local_windows = 0
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
    return img_array

# 直方图聚合
def hist_cluster(frames):
    frames_number = int(frames.shape[0])
    num = frames_number
    key = np.zeros(num)
    cluster = np.zeros(num)
    clusterCount = np.zeros(num)
    count = 0
    threshold = 0.75

    centrodR = []
    centrodG = []
    centrodB = []

    if num == 0:
        print('Sorry, there is no pictures in images folder!')
    else:
        count = count + 1
        frame0 = frames[30]
        # print(frame0)
        cv.imshow("frame0", frame0)

        # histR = np.histogram(frame0[:, :, 0], bins=2)  # 用numpy包计算直方图
        # histG = np.histogram(frame0[:, :, 1], bins=2)  # 用numpy包计算直方图
        # histB = np.histogram(frame0[:, :, 2], bins=2)  # 用numpy包计算直方图

        b, g, r = cv.split(frame0)

        histR = cv.calcHist([r], [0], None, [256], [0.0, 255.0])
        histG = cv.calcHist([g], [0], None, [256], [0.0, 255.0])
        histB = cv.calcHist([b], [0], None, [256], [0.0, 255.0])

        # minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(histR)
        # histImg = np.zeros([256, 256, 3], np.uint8)
        # hpt = int(0.9 * 256);
        # for h in range(256):
        #     intensity = int(histR[h] * hpt / maxVal)
        #     cv.line(histImg, (h, 256), (h, 256 - intensity), [255, 0, 0])
        # cv.imshow("histImgB", histImg)

        # print(histR.shape)
        # print(histB.shape)

        cluster[0] = 0
        clusterCount[0] = clusterCount[0] + 1

        centrodR.append(histR)
        centrodG.append(histG)
        centrodB.append(histB)

        for k in range(1, num):
            nowframe = frames[k]
            b, g, r = cv.split(nowframe)
            temphistR = cv.calcHist([r], [0], None, [256], [0.0, 255.0])
            temphistG = cv.calcHist([g], [0], None, [256], [0.0, 255.0])
            temphistB = cv.calcHist([b], [0], None, [256], [0.0, 255.0])

            clusterGroupId = 1
            maxSimilar = 0

            for clusterCountI in range(0, count):
                sR = 0
                sG = 0
                sB = 0
                for j in range(0, 256):
                    sR = min(centrodR[clusterCountI][j], temphistR[j]) + sR
                    sG = min(centrodG[clusterCountI][j], temphistG[j]) + sG
                    sB = min(centrodB[clusterCountI][j], temphistB[j]) + sB

                dR = sR / sum(temphistR)
                dG = sG / sum(temphistG)
                dB = sB / sum(temphistB)

                d=0.30*dR+0.59*dG+0.11*dB

                if d>maxSimilar:
                    clusterGroupId=clusterCountI
                    maxSimilar=d

            print(maxSimilar)

            if maxSimilar>threshold:
                for ii in range(0, 256):
                    centrodR[clusterGroupId][ii]=centrodR[clusterGroupId][ii]*clusterCount[clusterGroupId]\
                                                /(clusterCount[clusterGroupId]+1)+temphistR[ii]*1.0/(clusterCount[clusterGroupId]+1)
                    centrodG[clusterGroupId][ii]=centrodG[clusterGroupId][ii]*clusterCount[clusterGroupId]\
                                                /(clusterCount[clusterGroupId]+1)+temphistG[ii]*1.0/(clusterCount[clusterGroupId]+1)
                    centrodB[clusterGroupId][ii]=centrodB[clusterGroupId][ii]*clusterCount[clusterGroupId]\
                                                /(clusterCount[clusterGroupId]+1)+temphistB[ii]*1.0/(clusterCount[clusterGroupId]+1)

                clusterCount[clusterGroupId]=clusterCount[clusterGroupId]+1
                cluster[k]=clusterGroupId

            else:
                clusterCount[count]=clusterCount[count]+1
                centrodR.append(temphistR)
                centrodG.append(temphistG)
                centrodB.append(temphistB)
                cluster[k]=count
                count = count + 1


        maxSimilarity=np.zeros(count)
        frame=np.zeros(count)
        # print(count)
        for i in range(0, num):
            sR=0
            sG=0
            sB=0
            # print(i)
            # print(cluster.shape)
            for j in range(0, 256):
                sR += min(centrodR[int(cluster[i])][j], temphistR[j])
                sG += min(centrodG[int(cluster[i])][j], temphistG[j])
                sB += min(centrodB[int(cluster[i])][j], temphistB[j])

            dR = sR / sum(temphistR)
            dG = sG / sum(temphistG)
            dB = sB / sum(temphistB)

            d=0.30*dR+0.59*dG+0.11*dB
            if d>maxSimilarity[int(cluster[i])]:
                maxSimilarity[int(cluster[i])]=d
                frame[int(cluster[i])]=i
        print(count)
        key_id = []
        for j in range(0, count):
            # cv.imshow("frame"+str(j), frames[int(frame[j])])
            # print(j)
            # print(frame[j])
            key_id.append(int(frame[j]))
            # cv.imwrite("./result02/frame"+str(int(frame[j]))+".jpg", frames[int(frame[j])])
            # key[int(frame[j])]=1
    return key_id


if __name__ == '__main__':
    # 从视频中读入所有帧
    sourcePath = 'popo.mp4'
    outputDir = './result3/'


    if not os.path.exists(outputDir):  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(outputDir)

    frames = read_img(sourcePath)
    # 总帧数
    frames_number = int(frames.shape[0])
    key_id = hist_cluster(frames)

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
    # cv.waitKey()
