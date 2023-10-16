import requests
import newspaper
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.request
import cv2
import os
import re
import sys


def remove_files_in_folder(folder_path):
    # Lấy danh sách tệp tin trong thư mục
    file_list = os.listdir(folder_path)

    # Xóa từng tệp tin trong thư mục
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print("Đã xóa:", file_path)

def download_and_parse_article(url):
    article = newspaper.Article(url, language='vi')
    article.download()
    article.parse()
    return article

def get_content(title, content):
    with open('./vietTTS/assets/transcript.txt', 'w', encoding='utf-8') as f:
        f.write('{}\n\n{}'.format(title, content))

def resize_and_blur(image_path, new_width, new_height):
    # Đọc hình ảnh từ đường dẫn
    image = cv2.imread(image_path)

    # Lấy kích thước gốc của hình ảnh
    original_height, original_width, _ = image.shape

    # Tính tỷ lệ giữa chiều rộng mới và chiều rộng gốc
    width_ratio = new_width / original_width

    # Tính chiều cao tương ứng để giữ nguyên tỷ lệ
    resized_height = int(original_height * width_ratio)

    # Thay đổi kích thước hình ảnh
    resized_image = cv2.resize(image, (new_width, resized_height))

    # Tính kích thước của phần ảnh mờ cần thêm vào trên và dưới hình ảnh
    blur_height_top = (new_height - resized_height) // 2 - 150
    blur_height_bottom = new_height - resized_height - blur_height_top

    # Cắt phần ảnh mờ ở trên và dưới hình ảnh
    top_blur = resized_image[:blur_height_top, :]
    bottom_blur = resized_image[-blur_height_bottom:, :]

    # Làm mờ ảnh
    top_blur = cv2.GaussianBlur(top_blur, (101, 101), 30)
    bottom_blur = cv2.GaussianBlur(bottom_blur, (101, 101), 30)

    # Ghép ảnh mờ vào trên và dưới hình ảnh
    final_image = cv2.vconcat([top_blur, resized_image, bottom_blur])

    return final_image

def download_and_process_images(url):
    with open('./vietTTS/assets/transcript.txt', "r") as file:
        content = file.read()
        start_phrase = "https://img-s-msn-com."
        end_phrase = ".img"

        image_files = []  # Danh sách để lưu các kết quả

        start_index = content.find(start_phrase)
        while start_index != -1:
            end_index = content.find(end_phrase, start_index)
            if end_index != -1:
                substring = content[start_index:end_index + len(end_phrase)]
                image_files.append(substring)
                start_index = content.find(start_phrase, end_index)
            else:
                break

        new_image_files = []  # Danh sách mới để lưu các kết quả

        for i, img in enumerate(image_files):
            parsed_url = urlparse(img)
            img_url_without_params = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            img_filename = "./vietTTS/assets/images/image_{}.jpg".format(i)
            urllib.request.urlretrieve(img_url_without_params, img_filename)
            print("Đã tải về ảnh:", img_filename)

            image = cv2.imread(img_filename)
            height, width, _ = image.shape
            if width > height:  # Nếu hình ảnh ngang
                # Thay đổi kích thước và thêm hiệu ứng mờ
                new_image = resize_and_blur(img_filename, 1080, 1390)

                # Lưu hình ảnh mới
                new_img_filename = "./vietTTS/assets/images/image_{}.jpg".format(i)
                cv2.imwrite(new_img_filename, new_image)
                print("Đã tải về và chỉnh sửa ảnh:", new_img_filename)
                new_image_files.append(new_img_filename)
            else:  # Nếu hình ảnh dọc
                new_image_files.append(img_filename)

        return new_image_files

def add_space_between_numbers(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    result = ''
    i = 0
    while i < len(content):
        if content[i].isdigit():
            j = i + 1
            while j < len(content) and content[j].isdigit():
                j += 1
            result += content[i:j] + ' '
            i = j
        else:
            result += content[i]
            i += 1

    with open(file_path, 'w') as file:
        file.write(result)

def process_article(url):
    article = download_and_parse_article(url)
    if len(article.text.split()) < 100:
        print("độ dài bài viết không phù hợp, bỏ qua!")
    else:
        remove_files_in_folder('./vietTTS/assets/images/')
        get_content(article.title, article.text)
        image_files = download_and_process_images(url)

    # Xoá dòng bắt đầu bằng '©'
        with open('./vietTTS/assets/transcript.txt', "r") as file:
            lines = file.readlines()
        filtered_lines = [line for line in lines if not line.startswith("©")]
        with open('./vietTTS/assets/transcript.txt', "w") as file:
            file.writelines(filtered_lines)
        print("Xoá dòng bắt đầu bằng '{}' thành công!".format("©"))

    with open('./vietTTS/assets/transcript.txt', 'r') as file:
        content = file.read()
        result = ''
        for index, char in enumerate(content):
            if char.isdigit():
                if index < len(content) - 1 and content[index + 1].isdigit():
                    result += char + ' '
                else:
                    result += char
            else:
                result += char
    with open('./vietTTS/assets/transcript.txt', 'w') as file:
        file.write(result)

    with open('./vietTTS/assets/transcript.txt', 'r') as file:
        content = file.read()
        result = ''
        for index, char in enumerate(content):
            if char in ('/', '-', '.'):
                if index < len(content) - 1 and (
                        content[index - 4] in ('/', '-', '.') or content[index - 2] in ('/', '-', '.')) and content[index + 1].isdigit():
                    result += ' năm '

                elif index < len(content) - 1 and content[index + 1].isdigit():
                    result += ' tháng '
                else:
                    result += char
            else:
                result += char
    with open('./vietTTS/assets/transcript.txt', 'w') as file:
        file.write(result)

    with open('./vietTTS/assets/transcript.txt', 'r') as file:
        content = file.read()
        transformed_content = re.sub(r'[fF]', 'ph', content)
        transformed_content = re.sub(r'[zZ]', 'd', transformed_content)
        transformed_content = re.sub(r'[jJ]', 'd', transformed_content)
        transformed_content = re.sub(r'[wW]', 'g', transformed_content)
        transformed_content = re.sub(r'[0]', 'không', transformed_content)
        transformed_content = re.sub(r'[1]', 'một', transformed_content)
        transformed_content = re.sub(r'[2]', 'hai', transformed_content)
        transformed_content = re.sub(r'[3]', 'ba', transformed_content)
        transformed_content = re.sub(r'[4]', 'bốn', transformed_content)
        transformed_content = re.sub(r'[5]', 'năm', transformed_content)
        transformed_content = re.sub(r'[6]', 'sáu', transformed_content)
        transformed_content = re.sub(r'[7]', 'bảy', transformed_content)
        transformed_content = re.sub(r'[8]', 'tám', transformed_content)
        transformed_content = re.sub(r'[9]', 'chín', transformed_content)
        transformed_content = re.sub(r'[10]', 'mười', transformed_content)
        transformed_content = re.sub(r'[11]', 'mười một', transformed_content)
        transformed_content = re.sub(r'[12]', 'mười hai', transformed_content)
    with open('./vietTTS/assets/transcript.txt', 'w') as file:
        file.write(transformed_content)

    with open('./vietTTS/assets/transcript.txt', 'r') as file:
        content = file.read()

        start_phrase0 = ',"title":"'
        end_phrase0 = '","sourceHreph"'

        start_index0 = content.find(start_phrase0)
        end_index0 = content.find(end_phrase0, start_index0)

        if start_index0 != -1 and end_index0 != -1:
            substring0 = content[start_index0 + len(start_phrase0):end_index0]

        start_phrase1 = '{"abstract":"'
        end_phrase1 = ',"body":"'

        start_index1 = content.find(start_phrase1)
        end_index1 = content.find(end_phrase1, start_index1)

        substring1 = content[start_index1:end_index1 + 9]

        # Xoá substring1 ra khỏi content
        content = content.replace(substring1, "")

        # Đặt substring0 lên đầu nội dung content
        content = substring0 + content

    with open('./vietTTS/assets/transcript.txt', 'w') as file:
        file.write(content)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        process_article(url)
    else:
        print("Vui lòng cung cấp URL:")


