import cv2
import dlib
import numpy as np

# 用來顯示的函示庫
import matplotlib.pyplot as plt
import matplotlib.image as mpimg 


# 將特徵點的座標轉成陣列
def shape_to_np(shape, dtype = "int"):
	# initialize the list of (x, y)-coordinates
	coords = np.zeros((68, 2), dtype = dtype)
	# loop over the 68 facial landmarks and convert them
	# to a 2-tuple of (x, y)-coordinates
	for i in range(0, 68):
		coords[i] = (shape.part(i).x, shape.part(i).y)
	# return the list of (x, y)-coordinates
	return coords

# 建立眼球遮罩
def eye_on_mask(face_shape, mask, side):

    points = [face_shape[i] for i in side]

    points = np.array(points, dtype=np.int32)
    # 利用眼睛的特徵點，把眼睛部位框出（就白白的那塊）
    mask = cv2.fillConvexPoly(mask, points, 255)

    # 取得眼睛的相對位置
    l = points[0][0]
    t = (points[1][1]+points[2][1])//2
    r = points[3][0]
    b = (points[4][1]+points[5][1])//2

    return mask, [l, t, r, b]

# 尋找眼球的位置
def find_eyeball_position(end_points, cx, cy):
    """ 尋找眼球的位置，回傳 0 = left, 1 = right, 2 = top, 3 = normal"""
    x_ratio = (end_points[0] - cx)/(cx - end_points[2])
    y_ratio = (cy - end_points[1])/(end_points[3] - cy)
    if x_ratio > 3:
        return 1
    elif x_ratio < 0.33:
        return 2
    elif y_ratio < 0.33:
        return 3
    else:
        return 0

def contouring(thresh, mid, end_points, img, right=False):
    _, cnts, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    try:
        cnt = max(cnts, key = cv2.contourArea)
        M = cv2.moments(cnt)

        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        if right:
            cx += mid

        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 1)

        cv2.circle(img, (end_points[0], end_points[1]), 2, (0, 255, 0), 1)
        cv2.circle(img, (end_points[2], end_points[3]), 2, (255, 0, 0), 1)


        pos = find_eyeball_position(end_points, cx, cy)
        return pos
    except:
        pass

    
def print_eye_pos(img, left, right):
    """
    Print the side where eye is looking and display on image
    Parameters
    ----------
    img : Array of uint8
        Image to display on
    left : int
        Position obtained of left eye.
    right : int
        Position obtained of right eye.
    Returns
    -------
    None.
    """
    if left == right and left != 0:
        text = ''
        if left == 1:
            print('Looking left')
            text = 'Looking left'
        elif left == 2:
            print('Looking right')
            text = 'Looking right'
        elif left == 3:
            print('Looking up')
            text = 'Looking up'
        font = cv2.FONT_HERSHEY_SIMPLEX 
        cv2.putText(img, text, (30, 30), font,  1, (0, 255, 255), 1, cv2.LINE_AA) 

# 建立人臉偵測
detector = dlib.get_frontal_face_detector()
# 建立人臉細節偵測
predictor = dlib.shape_predictor('model/shape_predictor_68_face_landmarks.dat')

# 眼球的特徵點位置：參照 https://miro.medium.com/max/875/0*SgfJ7xl7QKZm037P.jpg
LEFT_EYE_EIGEN_POINT    = [36, 37, 38, 39, 40, 41]
RIGHT_EYE_EIGEN_POINT   = [42, 43, 44, 45, 46, 47]

# 開啟視訊鏡頭與讀取資料
webcam = cv2.VideoCapture(0)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
webcam.set(cv2.CAP_PROP_FPS, 60)

ret, img = webcam.read()

# 複製鏡頭錄製的圖片
thresh = img.copy()

# 開啟視窗叫 "image"
cv2.namedWindow('image')

# 建立一個 9x9 都為 1 的矩陣，其數值為正整數
kernel = np.ones((5, 5), np.uint8)

def nothing(x):
    pass
cv2.createTrackbar('threshold', 'image', 0, 255, nothing)

while(True):

    # 假如按下 Q 鍵就停止
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # 取得視訊時的圖片
    ret, img = webcam.read()
    # 轉成灰階圖
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 取得人臉位置
    rects = detector(gray)

    # 假如有多個人臉就迴圈判斷
    for rect in rects:

        # 找出人臉的眼睛、嘴吧、鼻子位置，並且加以標記
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)

        # 建立眼睛遮罩，利用特徵點取得遮罩
        mask = np.zeros( img.shape[:2], dtype = np.uint8 )
        mask, end_point_left    = eye_on_mask(shape, mask, LEFT_EYE_EIGEN_POINT )
        mask, end_point_right   = eye_on_mask(shape, mask, RIGHT_EYE_EIGEN_POINT )
        mask = cv2.dilate( mask, kernel, 5) # 將遮罩膨脹
        eyes = cv2.bitwise_and(img, img, mask = mask) # 人臉圖片與遮罩取交集(and)，來取得眼睛
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = (shape[42][0] + shape[39][0]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)

        # 取得判斷的閥值（這個適用另一個視窗設定的）
        threshold = cv2.getTrackbarPos('threshold', 'image')
        _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY) # 用來產生二值化圖
        thresh = cv2.erode(thresh, None, iterations=2)  #1  (影像侵蝕 [Erosion]，可以用來去噪，簡單來說就是減少影像中的小白點)
        thresh = cv2.dilate(thresh, None, iterations=4) #2 (影像膨脹 [Dilation]，通常與侵蝕一起使用，侵蝕完後在膨脹回來，簡單來說就是讓物品胖一圈)
        thresh = cv2.medianBlur(thresh, 3)  #3 中值濾波器，進行降噪處理
        thresh = cv2.bitwise_not(thresh)    #4 將遮罩反向，就是讓我們只看到白白的眼睛

        
        eyeball_pos_left    = contouring(thresh[:, 0:mid], mid, end_point_left , img, False)
        eyeball_pos_right   = contouring(thresh[:, mid:] , mid, end_point_right, img, True)
        print_eye_pos(img, eyeball_pos_left, eyeball_pos_right)

        #for (x, y) in shape[36:48]:
        #   cv2.circle(img, (x, y), 2, (255, 0, 0), -1)
    # show the image with the face detections + facial landmarks

    # 顯示偵測出的圖片 與 閥值設定遮照圖
    cv2.imshow('eyes', img)
    cv2.imshow("image", thresh)

    
webcam.release()
cv2.destroyAllWindows()
