import os
import pickle
from tqdm import tqdm

import pdfplumber

# folder_path의 모든 파일 이름을 확장자 포함하여 리스트로 추출
def get_file_names(folder_path):
    if not os.path.exists(folder_path):
        folder_name = folder_path.split('/')[-1]
        exit(f'FolderNotExistError: There is no [{folder_name}] folder')

    ## list file name
    pdf_file_lists = os.listdir(folder_path)
    if not pdf_file_lists:
        exit('FileNotExistError: There are no files in the folder')
    
    return pdf_file_lists

# folder_path의 모든 파일 path를 리스트로 추출
def get_file_paths(folder_path):

    ## list file name
    pdf_file_lists = get_file_names(folder_path=folder_path)

    pdf_file_paths = [folder_path + '/' + file_name for file_name in pdf_file_lists]

    return pdf_file_paths

# path로부터 파일 이름 구하기(path 맨 마지막 문자열 추출)
def path_to_name(path):
    name = path.split('/')[-1]
    return name

# bbox 'list'의 모든 bbox에 padding을 적용하여 리스트로 추출
def bbox_padding(bbox_list, padding=0):
    new_bbox = []
    for bbox in bbox_list:
        new_bbox.append((bbox[0], max(bbox[1]-padding, 0), bbox[2], min(bbox[3]+padding, 842)))
    return new_bbox

# 파일 path의 파일을 pdfplumber의 pdf 형식으로 반환
def get_pdf(path):
    pdf = pdfplumber.open(path)
    return pdf

# pdf의 모든 page를 pdfplumber의 page 형식으로, 리스트로 반환
def get_pages(pdf):
    pages = pdf.pages
    return pages

# pdfplumber의 page 객체 내 text 객체를 추출
def get_text(page):
    text = page.extract_words()
    return text

# pdfplumber의 page 객체 내 tableobject 객체를 리스트로 추출
def get_table(page):
    table = page.find_tables()
    return table

# pdfplumber의 page 객체 내 image 객체를 추출
def get_image(page):
    image = page.images
    return image

# pdfplumber의 tableobject 객체를 dict형식으로 바꾸어 추출(cells, bbox, extract)
def table_object_to_dict(table_object):
    table_dict = {}
    table_dict['cells'] = table_object.cells
    table_dict['bbox'] = table_object.bbox
    table_dict['extract'] = table_object.extract()
    return table_dict

# 저장 path와 파일이름을 받고 해당 save_path에 file_name 명의 디렉토리 생성
def make_pdf_dir(save_path, file_name):
    pdf_save_directory = save_path + '/' + file_name[:-4]

    ## make directory for file
    if not os.path.exists(pdf_save_directory):
        os.makedirs(pdf_save_directory)

# data와 저장경로, 해당 data가 유래한 pdf의 파일면, data_type(text, image, table)을 인수로 받아 저장
def save_pickle_file(data, save_path, file_name, data_type):
    with open(f'{save_path}/{file_name[:-4]}/{file_name[:-4]}_{data_type}.pickle', 'wb') as fw:
        pickle.dump(data, fw)






if __name__ == '__main__':

    ''' 
    경로는 다음과 같이 지정합니다
    
    1. folder_path
    해당 변수의 경로(추출경로)에 변환하려는 pdf를 모아 모두 저장하여 둡니다
    2. save_path
    해당 변수의 경로에 pdf의 파일 명으로 하위 폴더가 만들어진 뒤, 해당 하위 폴더에 text, image, table의
    pickle 파일이 저장됩니다
    '''

    # 경로 지정
    folder_path = 'sample_pdf_file' # 변환하려는 pdf가 저장된 폴더
    save_path = 'sample_img_file' # 변환하려는 pdf를 저장하기 위한 폴더

    # 파일명, 파일 경로 추출
    pdf_file_lists = get_file_names(folder_path=folder_path)
    pdf_file_paths = get_file_paths(folder_path=folder_path)

    '''
    아래 루프는 다음의 순서로 진행됩니다
    
    1. 저장경로 내 pdf를 순차적으로 선택합니다
    2. pdf 파일의 이름을 지정한 뒤, pdf 객체를 지정하고, 각 page객체를 list로 추출합니다
    3. 해당 pdf 파일의 이름으로 하위 폴더를 생성한 뒤, 각 페이지의 객체를 추출하여 dictionary[페이지번호] = List[dictionary1, dictionary2,...] 형태로 pickle로 저장합니다
    
    주의할 점은 다음과 같습니다
    
    1. 파일 형태
    저장된 pickle 파일의 경우 딕셔너리-리스트-딕셔너리 형태의 3중 구조입니다
    첫번째 딕셔너리의 key값은 0부터 구성된 페이지 번호이며, item은 list입니다
    두번째 리스트의 요소는 해당 페이지의 text/image/table 딕셔너리를 순차적으로 배치한 것입니다
    세번째 딕셔너리는 각각 text/image/table의 속성을 key값으로 가지며, 해당 딕셔너리는 각각 text/iamge/table 하나씩을 의미합니다. 각 object의 속성은 dict.keys()로 확인 바랍니다
    
    2. table 파일 
    table 객체의 경우, pdfplumber에서 제공하는 형태가 pickle을 지원하지 않았습니다.
    따라서 해당 객체의 요소를 딕셔너리 형태로 가공하여 pickle 파일로 변환하였습니다.
    이 중 pdfplumber의 "rows"는 불필요할 것으로 판단하여 포함하지 않았습니다
    '''

    
    # pdf별 루프
    for path in pdf_file_paths:
        # 파일 이름 지정
        file_name = path_to_name(path)
        # pdf 객체 정의
        pdf = get_pdf(path)
        # page 리스트 추출
        pages = get_pages(pdf)

        # 저장용 pdf 별 object dictionary 생성
        text_dict = {}
        image_dict = {}
        table_dict = {}

        # pdf파일명 하위 폴더가 없을 경우 생성
        make_pdf_dir(save_path, file_name)

        # 각 page 루프
        for i, page in tqdm(enumerate(pages)):
            # text, image 객체 추출
            text = get_text(page)
            image = get_image(page)
            # tableobject 객체 딕셔너리로 변환
            table_obj = get_table(page)
            table = []
            for tboj in table_obj:
                table.append(table_object_to_dict(tboj))

            # page 별로 저장
            text_dict[i] = text
            image_dict[i] = image
            table_dict[i] = table
        # 해당 pdf의 pickle 파일 저장
        save_pickle_file(text_dict, save_path, file_name, data_type='text')
        save_pickle_file(image_dict, save_path, file_name, data_type='image')
        save_pickle_file(table_dict, save_path, file_name, data_type='table')



