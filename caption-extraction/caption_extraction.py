import os
import pandas as pd
import pickle
import pdfplumber
from math import dist
from tqdm.notebook import tqdm


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

# 캡션을 추출하는 함수
# to-do: image에 대한 것도 추가하기 (일단 table에 대해서만 진행함)
def caption_detector(pages, corp_image, corp_table, corp_text, corp, threshold_caption=30, threshold_chunk=15, threshold_line=8, resolution=150):
   '''
   pages: get_pages(pdf)의 결과물
   corp_image, corp_table, corp_text: pdfplumber로 추출한 image, table, text 정보
   corp: 결과를 저장할 폴더 이름 (str)
   threshold_caption: 해당 텍스트가 표/이미지의 캡션에 해당하는지 아닌지 구분하는 threshold (거리)
   threshold_chunk: 같은 줄에 있을 때 같은 chunk인지 아닌지 구분하는 threshold (거리)
   threshold_line: 한 문장이 다음 줄로 이어지는 것인지 아닌지 구분하는 threshold (y값 거리)
   output: 페이지별로 캡션의 bounding box가 표시된 이미지 파일이 저장됨
   '''
   for p in tqdm(range(len(pages))):
        if len(corp_table[p]) != 0:
            table_data = corp_table[p]
            text_data = corp_text[p]
            table_bb_to_draw = []
            text_bb_to_draw = []

            for table in table_data:
                table_bb_to_draw.append(table['bbox'])
                caption_for_this_table = []

                i = 0
                while i < len(text_data):
                    # print('loop 1:', i)

                    # 특정 키워드를 포함 + table과의 거리가 threshold_caption 이내 + 텍스트가 표에 포함되지 않음(캡션의 시작점)
                    if rect_distance(table['bbox'], get_bbox(text_data[i])) <= threshold_caption \
                    and any(x in ['※', '*', '■', '☞', '[', '(', '<', '단위', '기준일', '주'] for x in text_data[i]['text']) \
                    and contains(table['bbox'], get_bbox(text_data[i])) == False:
                        # print('detected start of caption')
                        caption_for_this_table.append(get_bbox(text_data[i]))
                        i += 1

                        while True:
                            # print('loop 2:', i)
                            # 앞 토큰과 같은 줄 + 거리가 threshold_chunk 이내
                            if get_bbox(text_data[i])[1] == get_bbox(text_data[i-1])[1] and get_bbox(text_data[i])[3] == get_bbox(text_data[i-1])[3] \
                            and rect_distance(get_bbox(text_data[i]), get_bbox(text_data[i-1])) <= threshold_chunk:
                                # print('case 1 - same line, same chunk')
                                caption_for_this_table.append(get_bbox(text_data[i]))
                                i += 1

                            # 줄이 바뀌지만 높이 차이가 threshold_line 이내 (이어지는 문장으로 판단)
                            elif diff_height(get_bbox(text_data[i]), get_bbox(text_data[i-1])) <= threshold_line:
                                # print('case 2 - different line, same chunk')
                                # print(get_bbox(text_data[i])[1], get_bbox(text_data[i-1])[1])
                                # print(get_bbox(text_data[i])[3], get_bbox(text_data[i-1])[3])
                                # print(rect_distance(get_bbox(text_data[i]), get_bbox(text_data[i-1])))
                                caption_for_this_table.append(get_bbox(text_data[i]))
                                i += 1

                            else:
                                # print('case 3 - end of caption')
                                i += 1
                                break
                    else:
                        i += 1

                text_bb_to_draw.append(caption_for_this_table)

            im = pages[p].to_image(resolution=resolution)
            im.reset()
            for j in range(len(table_bb_to_draw)):
                im.draw_rect(table_bb_to_draw[j], fill=(255, 0, 0, 30))
                im.draw_rects(text_bb_to_draw[j])
                
            # 결과를 저장할 디렉터리가 없으면 디렉터리 생성
            if not os.path.exists(f'result/{corp}'):
                os.makedirs(f'result/{corp}') 

            im.save(f'result/{corp}/{p+1}.png', format="PNG")