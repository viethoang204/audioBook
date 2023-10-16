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

    substring1 = content[start_index1:end_index1+9]

    # Xoá substring1 ra khỏi content
    content = content.replace(substring1, "")

    # Đặt substring0 lên đầu nội dung content
    content = substring0 + content

    # In ra nội dung đã chỉnh sửa
    print(content)
