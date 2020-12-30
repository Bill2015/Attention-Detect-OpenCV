import cv2
import numpy as np
import dlib as dlib
import math

from HistoryDict import *
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

def get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val):
    """Return the 3D points present as 2D for making annotation box"""
    point_3d = []
    dist_coeffs = np.zeros((4,1))
    rear_size = val[0]
    rear_depth = val[1]
    point_3d.append((-rear_size, -rear_size, rear_depth))
    point_3d.append((-rear_size, rear_size, rear_depth))
    point_3d.append((rear_size, rear_size, rear_depth))
    point_3d.append((rear_size, -rear_size, rear_depth))
    point_3d.append((-rear_size, -rear_size, rear_depth))
    
    front_size = val[2]
    front_depth = val[3]
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d.append((-front_size, front_size, front_depth))
    point_3d.append((front_size, front_size, front_depth))
    point_3d.append((front_size, -front_size, front_depth))
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d = np.array(point_3d, dtype=np.float).reshape(-1, 3)
    
    # Map to 2d img points
    (point_2d, _) = cv2.projectPoints(point_3d,
                                      rotation_vector,
                                      translation_vector,
                                      camera_matrix,
                                      dist_coeffs)
    point_2d = np.int32(point_2d.reshape(-1, 2))
    return point_2d
def draw_annotation_box(img, rotation_vector, translation_vector, camera_matrix,
                        rear_size=100, rear_depth=0, front_size=500, front_depth=100,
                        color=(255, 255, 0), line_width=2):
    """
    Draw a 3D anotation box on the face for head pose estimation
    Parameters
    ----------
    img : np.unit8
        Original Image.
    rotation_vector : Array of float64
        Rotation Vector obtained from cv2.solvePnP
    translation_vector : Array of float64
        Translation Vector obtained from cv2.solvePnP
    camera_matrix : Array of float64
        The camera matrix
    rear_size : int, optional
        Size of rear box. The default is 300.
    rear_depth : int, optional
        The default is 0.
    front_size : int, optional
        Size of front box. The default is 500.
    front_depth : int, optional
        Front depth. The default is 400.
    color : tuple, optional
        The color with which to draw annotation box. The default is (255, 255, 0).
    line_width : int, optional
        line width of lines drawn. The default is 2.
    Returns
    -------
    None.
    """
    
    rear_size = 1
    rear_depth = 0
    front_size = img.shape[1]
    front_depth = front_size*2
    val = [rear_size, rear_depth, front_size, front_depth]
    point_2d = get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val)
    # # Draw all the lines
    cv2.polylines(img, [point_2d], True, color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[1]), tuple(
        point_2d[6]), color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[2]), tuple(
        point_2d[7]), color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[3]), tuple(
        point_2d[8]), color, line_width, cv2.LINE_AA)

def head_pose_points(img, rotation_vector, translation_vector, camera_matrix):
    """
    Get the points to estimate head pose sideways    
    Parameters
    ----------
    img : np.unit8
        Original Image.
    rotation_vector : Array of float64
        Rotation Vector obtained from cv2.solvePnP
    translation_vector : Array of float64
        Translation Vector obtained from cv2.solvePnP
    camera_matrix : Array of float64
        The camera matrix
    Returns
    -------
    (x, y) : tuple
        Coordinates of line to estimate head pose
    """
    rear_size = 1
    rear_depth = 0
    front_size = img.shape[1]
    front_depth = front_size*2
    val = [rear_size, rear_depth, front_size, front_depth]
    point_2d = get_2d_points(img, rotation_vector, translation_vector, camera_matrix, val)
    y = (point_2d[5] + point_2d[8])//2
    x = point_2d[2]
    
    return (x, y)
    

# 建立人臉偵測
FACE_DETECTOR = dlib.get_frontal_face_detector()
# 建立人臉細節偵測
FACE_PREDICTOR = dlib.shape_predictor('model/shape_predictor_68_face_landmarks.dat')

# 建立臉部 3D 模型位置.
FACE_3D_MODEL_POINT = np.array([
                            (0.0, 0.0, 0.0),             # Nose tip
                            (0.0, -330.0, -65.0),        # Chin
                            (-225.0, 170.0, -135.0),     # Left eye left corner
                            (225.0, 170.0, -135.0),      # Right eye right corne
                            (-150.0, -150.0, -125.0),    # Left Mouth corner
                            (150.0, -150.0, -125.0)      # Right mouth corner
                        ], dtype='double')

# 攝像頭
WEBCAM = cv2.VideoCapture(0)
WEBCAM.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
WEBCAM.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
WEBCAM.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
ret, img = WEBCAM.read()
size = img.shape



# 取得鏡頭焦距
focal_length = size[1]
center = (size[1]/2, size[0]/2)
CAMERA_MATRIX = np.array(
                            [
                                [focal_length, 0, center[0]],
                                [0, focal_length, center[1]],
                                [0, 0, 1]
                            ], dtype='double'
                        )

def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    # return a tuple of (x, y, w, h)
    return (x, y, w, h)

# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( roll and yaw are swapped ).
def get_angles_eular(rvec, tvec):
    rmat = cv2.Rodrigues(rvec)[0]
    P = np.hstack((rmat, tvec)) # projection matrix [R | t]
    degrees = -cv2.decomposeProjectionMatrix(P)[6]
    rx, ry, rz = degrees[:, 0]
    return [rx, ry, rz]

def get_angles_gerneal(image_points, rvec, tvec):
    dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
    # 將 3D 座標點，投影至 2D 圖片面板上
    (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rvec, tvec, CAMERA_MATRIX, dist_coeffs, cv2.SOLVEPNP_AP3P)

    # --------------------------------------------------------------------------------------
    # 取得垂直角度
    # 取得鼻尖座標 (臉部直接投影位置)
    p1 = ( int(image_points[0][0]), int(image_points[0][1]))
    # 取得鼻尖座標 (臉部 3D 投影後的座標)
    p2 = ( int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

    cv2.line(img, p1, p2, (0, 255, 0), 2)
    try:
        m = (p2[1] - p1[1])/(p2[0] - p1[0])
        vertical_angle = int(math.degrees(math.atan(m)))
    except:
        vertical_angle = 0
    
    # cv2.putText(img, str(vertical_angle), tuple(p1), font, 2, (128, 255, 255), 3)
    # --------------------------------------------------------------------------------------
    # 取得水平角度
    x1, x2 = head_pose_points(img, rvec, tvec, CAMERA_MATRIX)

    cv2.line(img, tuple(x1), tuple(x2), (255, 255, 0), 2)
    # for (x, y) in marks:
    #     cv2.circle(img, (x, y), 4, (255, 255, 0), -1)
    # cv2.putText(img, str(p1), p1, font, 1, (0, 255, 255), 1)
    try:
        if (x2[0] - x1[0]) != 0:
            m = (x2[1] - x1[1])/(x2[0] - x1[0])
            horizon_angle = int(math.degrees(math.atan(-1/m)))
        else: 
            horizon_angle = 0
    except:
        horizon_angle = 0
    # cv2.putText(img, str(horizon_angle), tuple(x1), font, 2, (255, 255, 128), 3)
    return (horizon_angle, vertical_angle)


# ==================== 偵測函式 ====================

Pnp_History = History( 2 )
Dib_History = History( 6 )

def detect():

    vertical_angle = 0
    horizon_angle  = 0
    # 讀取攝像頭圖片
    ret, img = WEBCAM.read()

    if ret == True:
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 轉成灰階圖
        # 開始判斷人臉
        faces = FACE_DETECTOR(img, 0) # 取得人臉
        

        for face in faces:       # 取得多張人臉

            (x, y, w, h) = rect_to_bb(face)
            # cv2.rectangle(img,(x, y),(x + w, y + h),(255,0,0),2)

            marks = FACE_PREDICTOR(img, face)    # 使用 dlib 模型，將臉部位置標記出
            marks = shape_to_np(marks)

            # mark_detector.draw_marks(img, marks, color=(0, 255, 0))

            # 儲存 dlib 標記結果取平均，讓整體更滑順
            landmark = [marks[30], marks[8], marks[36], marks[45], marks[48], marks[54]]
            Dib_History.add( landmark )
            if( Dib_History.is_full() ):
                landmark = Dib_History.get_average()
                Dib_History.pop()


            # 建立特徵點陣列 (點由 Dlib 產生)
            image_points = np.array([
                                    landmark[0],     # 取得鼻尖點
                                    landmark[1],      # 取得下巴點
                                    landmark[2],     # 取得左眼左眼角
                                    landmark[3],     # 取得右眼右眼角
                                    landmark[4],     # 取得左嘴角
                                    landmark[5]      # 取得右嘴角
                                ], 
                                dtype='double')



            dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
            # 取得在 3D 投影至 2D 畫面時的座標運算，用來計算 3D 位置標定的移動情況
            (success, rotation_vector, translation_vector) = cv2.solvePnP(FACE_3D_MODEL_POINT, image_points, CAMERA_MATRIX, dist_coeffs)
            

            # 儲存 pnp 運算結果取平均，讓整體更滑順
            Pnp_History.add( [rotation_vector, translation_vector] )
            if( Pnp_History.is_full() ):
                [rotation_vector, translation_vector] = Pnp_History.get_average()
                Pnp_History.pop()


            draw_annotation_box(img, rotation_vector, translation_vector, CAMERA_MATRIX)
            # Project a 3D point (0, 0, 1000.0) onto the image plane.
            # We use this to draw a line sticking out of the nose
            

            # 將臉部的點標記出至圖片上
            for p in image_points:
                cv2.circle(img, (int(p[0]), int(p[1])), 3, (0,0,255), -1)
            
            (horizon_angle, vertical_angle) = get_angles_gerneal(image_points, rotation_vector, translation_vector) 

        # 顯示影像
        # cv2.imshow('img', img)

    # 回傳角度以及圖片
    return (horizon_angle, vertical_angle, img)

# 頭部方向
NONE    = 0
LEFT    = 1
RIGHT   = 2
UP      = 3
DOWN    = 4
GONE    = 5

# 判斷頭部目前的轉向
def judge_look(horizon_angle, vertical_angle, horizon_threshold, vertical_threshold):
    head_direction      = 0
    head_direction_str  = ['      ','      '] 

    # print('div by zero error')
    if abs(vertical_angle) <= 45 - (vertical_threshold / 2) :
        # print('Head down')
        head_direction = UP
        head_direction_str[1] = ' 向下 '

    elif abs(vertical_angle) >= 45 + (vertical_threshold / 2):
        # print('Head up')
        head_direction = DOWN
        head_direction_str[1] = ' 向上 '

    if horizon_angle >= horizon_threshold:
        # print('Head right')
        head_direction = RIGHT
        head_direction_str[0] = ' 向右 '

    elif horizon_angle <= -horizon_threshold:
        # print('Head left')
        head_direction = LEFT
        head_direction_str[0] = ' 向左 '

    if horizon_angle == 0 and vertical_angle == 0:
        head_direction = GONE

    return (head_direction, head_direction_str)

def destroy():
    WEBCAM.release()
    