from math import dist

# 2개의 직사각형 사이의 최단거리 계산
# rotation은 고려 x
# https://stackoverflow.com/questions/4978323/how-to-calculate-distance-between-two-rectangles-context-a-game-in-lua
def rect_distance(RectA, RectB):
    
    A_x0, A_y0, A_x1, A_y1 = RectA
    B_x0, B_y0, B_x1, B_y1 = RectB
    
    # 변수명: A 기준
    left = B_x1 < A_x0 
    right = A_x1 < B_x0
    bottom = B_y1 < A_y0
    top = A_y1 < B_y0
    
    if top and left:
        return dist((A_x0, A_y1), (B_x1, B_y0))
    elif left and bottom:
        return dist((A_x0, A_y0), (B_x1, B_y1))
    elif bottom and right:
        return dist((A_x1, A_y0), (B_x0, B_y1))
    elif right and top:
        return dist((A_x1, A_y1), (B_x0, B_y0))
    elif left:
        return A_x0 - B_x1
    elif right:
        return B_x0 - A_x1
    elif bottom:
        return A_y0 - B_y1
    elif top:
        return B_y0 - A_y1
    else:             # rectangles intersect
        return 0.0

# y값의 차이만 계산 (수직 거리)
# rect_distance에서 A와 B의 x0과 x1은 같은 경우
def diff_height(RectA, RectB):

    _, A_y0, _, A_y1 = RectA
    _, B_y0, _, B_y1 = RectB

    # 변수명: A 기준
    bottom = B_y1 < A_y0
    top = A_y1 < B_y0

    if bottom:
        return A_y0 - B_y1
    elif top:
        return B_y0 - A_y1
    else:
        return 0.0

# RectA가 RectB를 포함하는지 체크
# https://stackoverflow.com/questions/21275714/check-rectangle-inside-rectangle-in-python
def contains(RectA, RectB):

    A_x0, A_y0, A_x1, A_y1 = RectA
    B_x0, B_y0, B_x1, B_y1 = RectB

    return A_x0 < B_x0 < B_x1 < A_x1 and A_y0 < B_y0 < B_y1 < A_y1

# image, text에서 사용
def get_bbox(obj):
    bbox = (round(obj['x0'], 2), round(obj['top'], 2), round(obj['x1'], 2), round(obj['bottom'], 2))
    return bbox


