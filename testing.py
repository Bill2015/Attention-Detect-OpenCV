import dlib as DLIB
import cv2 as CV2
import numpy as NP

# 用來顯示的函示庫
import matplotlib.pyplot as plt
import matplotlib.image as mpimg 
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


# 將特徵點的座標轉成陣列
def shape_to_np(shape, dtype = "int"):
	# initialize the list of (x, y)-coordinates
	coords = NP.zeros((68, 2), dtype = dtype)
	# loop over the 68 facial landmarks and convert them
	# to a 2-tuple of (x, y)-coordinates
	for i in range(0, 68):
		coords[i] = (shape.part(i).x, shape.part(i).y)
	# return the list of (x, y)-coordinates
	return coords


def face_detect():
    # 建立人臉偵測
    detector = DLIB.get_frontal_face_detector()
    # 建立人臉細節偵測
    predictor = DLIB.shape_predictor('model/shape_predictor_68_face_landmarks.dat')

    img = CV2.imread('image.jpg')

    # 開啟視窗叫 "image"
    CV2.imshow('image', img)

    # 取得人臉位置
    rects = detector( img )

    while True:
        # 假如有多個人臉就迴圈判斷
        for rect in rects:
            # 找出人臉的眼睛、嘴吧、鼻子位置，並且加以標記
            shape = predictor(img, rect)
            for i in range(0, 68):
                CV2.circle(img, (shape.part(i).x, shape.part(i).y), 1, (0, 0, 255), -1)

            shape = shape_to_np(shape)

            # 建立特徵點陣列 (點由 Dlib 產生)
            image_points = NP.array([
                                    shape[30],     # 取得鼻尖點
                                    shape[8],      # 取得下巴點
                                    shape[36],     # 取得左眼左眼角
                                    shape[45],     # 取得右眼右眼角
                                    shape[48],     # 取得左嘴角
                                    shape[54]      # 取得右嘴角
                                ], 
                                dtype='double')
            for element in image_points:
                CV2.circle(img, (int(element[0]), int(element[1])), 3, (0,255,0), -1)

            # 顯示偵測出的圖片 與 閥值設定遮照圖
            CV2.imshow('face', img)

        # 離開迴圈，關閉攝影機q
        if CV2.waitKey(1) & 0xFF == ord('q'):
            break

    CV2.destroyAllWindows()

face_detect()

def face_model():
    # 建立臉部 3D 模型位置.
    FACE_3D_MODEL_POINT = NP.array([
                                (0.0, 0.0, 0.0),             # Nose tip
                                (0.0, -330.0, -65.0),        # Chin
                                (-225.0, 170.0, -135.0),     # Left eye left corner
                                (225.0, 170.0, -135.0),      # Right eye right corne
                                (-150.0, -150.0, -125.0),    # Left Mouth corner
                                (150.0, -150.0, -125.0)      # Right mouth corner
                            ], dtype='double')
    FACE_3D_NANE = ['Nose tip', 'Chin', 'Left eye left corner', 'Right eye right corne', 'Left Mouth corner', 'Right mouth corner']
    count = 0
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for element in FACE_3D_MODEL_POINT:
        ax.scatter(element[0], element[1], element[2], marker='o')
        ax.text(element[0], element[1], element[2], FACE_3D_NANE[count])
        count += 1

    # 鼻尖道下八
    ax.plot([0.0, 0.0], [0.0, -330], [0.0, -65.0])
    # 左眼到右眼
    ax.plot([-225.0, 225.0], [170, 170], [-135.0, -135.0])
    # 左眼到左嘴
    ax.plot([-225.0, -150.0,], [170, -150.0,], [-135.0, -125.0])
    # 右眼到右嘴
    ax.plot([225.0, 150.0,], [170, -150.0,], [-135.0, -125.0])
    # 左嘴到右嘴
    ax.plot([-150.0, 150.0,], [-150, -150.0,], [-125.0, -125.0])
    # 左嘴道下巴
    ax.plot([-150.0, 0.0,], [-150, -330.0,], [-125.0, -65.0])
    # 右嘴道下巴
    ax.plot([150.0, 0.0,], [-150, -330.0,], [-125.0, -65.0])
    # 左眼到鼻尖
    ax.plot([-225.0, 0.0], [170.0, 0.0], [-135.0, 0.0])
    # 右眼到鼻尖
    ax.plot([225.0, 0.0], [170.0, 0.0], [-135.0, 0.0])

    plt.show()