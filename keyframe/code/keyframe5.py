# 改良K-Means聚类
import os
import numpy as np
import cv2 as cv
# from sklearn.decomposition import PCA


# 从视频读入所有帧
def read_img(sourcePath):
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
    return img_array


def calc_hist(frames):
    num = int(frames.shape[0])
    hists = []
    for i in range(num):
        temp = frames[i]
        luv = cv.cvtColor(temp, cv.COLOR_RGB2YUV)
        l, u, v = cv.split(luv)
        temphist = cv.calcHist([l], [0], None, [256], [0.0, 255.0])
        hists.append(temphist)

    return hists


def get_key_frame(input):
    # 相当于求图像与前一帧的差
    diff_C = input[1:] - input[:-1]
    # 差图像的均值
    mid_d = np.zeros(input.shape[1])
    for i in range(diff_C.shape[1]):
        mid_d[i] = np.mean(diff_C[:, i])
    mid_d = np.sum(np.abs(mid_d))

    # 差图像的所有像素值之和
    T = 10000
    # 确定聚类个数k
    # 当mid_d小于一定阈值时，可以认为视频内容变换平缓
    print(mid_d)
    if mid_d <= 3500:
        k1 = frames_number / 100
        k2 = np.sum(diff_C >= T)
        k = max(k1, k2)
    else:
        k1 = frames_number / 50
        k2 = np.sum(diff_C >= T)
        k = k1
    k = int(k)
    print(k)
    # 确认了提取关键帧的数量，接下来进行聚类法提取关键帧
    Cluster = []
    set_cluster = []
    now = 0
    # 选定最初的聚类中心，每隔一定间距选定一个关键帧
    for i in range(k):
        # 防止越界
        if now >= frames_number - 2:
            now = frames_number - 2
        Cluster.append(input[now])
        set_cluster.append({now})
        now += int(frames_number / (k-1))
        # if (np.sum(np.abs(diff_C[now])) > mid_d):
        #     now += int(frames_number / (3 * k))
        # else:
        #     now += int(frames_number / k)
    cnt = 0  # 防止迭代次数过多
    # 开始迭代
    while True:
        cnt += 1
        now = 0  # 指代当前分配帧数
        for i in range(k):
            set_cluster[i].clear()  # 先清空每个集合
        # 为每一帧选定所在的聚类
        for i in range(frames_number):
            # 当前帧前后各选取一个关键帧作对比
            l = now
            r = min(now + 1, k - 1)
            ldiff = np.mean(abs(Cluster[l] - input[i]))
            rdiff = np.mean(abs(Cluster[r] - input[i]))
            if ldiff < rdiff:
                set_cluster[l].add(i)
            else:
                set_cluster[r].add(i)
                now = r
        # ok是控制kmean聚类迭代停止的变量
        ok = True
        for i in range(k):
            # 重新求聚类的均值
            Len = len(set_cluster[i])
            if Len == 0:
                continue
            set_sum = np.zeros(input.shape[1])
            for x in set_cluster[i]:
                set_sum = set_sum + input[x]
            set_sum /= Len
            # 该中心稳定下来
            if np.mean(abs(Cluster[i] - set_sum)) < 1e-10:
                continue
            ok = False
            Cluster[i] = set_sum
        print("第" + str(cnt) + "次聚类")
        # 所有的中心都稳定下来或者迭代次数超过阈值则停止迭代
        if cnt >= 100 or ok == True:
            break
    return Cluster


if __name__ == '__main__':
    # 从视频中读入所有帧
    sourcePath = 'popo.mp4'
    outputDir = './result5/'
    # 聚类成为几类
    cluster_size = 60
    MAX_DIST =1000000000

    if not os.path.exists(outputDir):  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(outputDir)

    # 读入所有帧图像
    frames = read_img(sourcePath)
    # 总帧数
    frames_number = int(frames.shape[0])

    # 计算直方图
    histogram = calc_hist(frames)
    histogram = np.array(histogram)
    histogram.resize(histogram.shape[0], histogram.shape[1])
    # print(histogram.shape)

    # 使用改进的Kmeans聚类方法
    Cluster= get_key_frame(histogram)

    # 对每一类，找到视频帧图像中与之最接近的图像
    hist0 = histogram[0]
    key_id = []
    for i in range(len(Cluster)):
        keyframe = Cluster[i]
        min = np.linalg.norm(hist0 - keyframe)
        minindex = 0
        mindist = MAX_DIST
        for j in range(frames_number):
            temphist = histogram[j]
            # 取欧式距离
            tempdist = np.linalg.norm(temphist - keyframe)
            if tempdist < mindist:
                mindist = tempdist
                minindex = j
        # 记录与聚类结果最接近的帧图像
        key_id.append(minindex)

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
