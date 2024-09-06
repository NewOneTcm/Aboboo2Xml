print("Script started")

try:
    print("Importing required modules")
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from bs4 import BeautifulSoup
    import os
    import time
    import random
    import requests
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    print("All modules imported successfully")

    print("Setting up Firefox options")
    firefox_options = Options()
    firefox_path = r"d:\Program Files\Mozilla Firefox\firefox.exe"
    firefox_options.binary_location = firefox_path
    print(f"Firefox path set to: {firefox_path}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    geckodriver_path = os.path.join(current_dir, "geckodriver.exe")
    print(f"Geckodriver path: {geckodriver_path}")

    print("Setting up Service")
    service = Service(geckodriver_path)
    print("Service set up successfully")

    print("Initializing Firefox driver")
    driver = webdriver.Firefox(service=service, options=firefox_options)
    print("Firefox driver initialized successfully")

    # 在脚本开始处创建一个会话
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.lingohut.com/'
    })

    def download_audio(url, filename):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()
                
                # 检查内容类型
                content_type = response.headers.get('Content-Type', '')
                if 'audio' in content_type or 'application/octet-stream' in content_type:
                    # 如果是音频文件或二进制流，保存它
                    with open(filename, 'wb') as file:
                        file.write(response.content)
                    print(f"Downloaded audio: {filename}")
                    return
                else:
                    print(f"Unexpected content type: {content_type} for URL: {url}")
                    return
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed to download audio {url}: {e}")
                if attempt == max_retries - 1:
                    print(f"Failed to download audio after {max_retries} attempts")
                else:
                    time.sleep(2)  # 在重试之前等待 2 秒

    def scrape_lesson_content(lesson_url):
        driver.get(lesson_url)
        time.sleep(2)  # 等待页面加载
        lesson_soup = BeautifulSoup(driver.page_source, 'html.parser')
        vocab_list = lesson_soup.find('div', class_='vocab-list')
        lesson_content = []
        
        if vocab_list:
            vocab_items = vocab_list.find_all('div', class_=['col-xs-12', 'col-sm-12', 'col-md-6', 'col-lg-6'])
            for item in vocab_items:
                vocab_box = item.find('button', class_='vocab-box')
                if vocab_box:
                    chinese = vocab_box.find('span', class_='vocab-box-english').text.strip()
                    english = vocab_box.find('span', class_='vocab-box-spalan').text.strip()
                    mp3_name = vocab_box.get('data-mp3-name')
                    if chinese and english and mp3_name:
                        # 更新音频 URL 格式，使用 "290130" 目录
                        audio_url = f"https://www.lingohut.com/flash/lht/mp3/290170/{mp3_name}.ogg"
                        lesson_content.append((f"{english} - {chinese}", audio_url))
        
        return lesson_content

    def create_lesson_topic(lesson_title):
        topic = ET.Element("topic")
        name = ET.SubElement(topic, "name")
        name.text = lesson_title
        return topic

    def create_word_topic(text, audio_filename):
        topic = ET.Element("topic")
        q = ET.SubElement(topic, "question")
        q.text = text
        sound = ET.SubElement(topic, "sound")
        sound.text = audio_filename
        return topic

    def prettify(elem):
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def create_supermemo_xml(lessons_content):
        root = ET.Element("SuperMemoCollection")
        ET.SubElement(root, "Count").text = str(len(lessons_content))
        
        second_root = ET.SubElement(root, "SuperMemoElement")
        ET.SubElement(second_root, "Type").text = "Topic"
        ET.SubElement(second_root, "Title").text = time.strftime("%Y-%m-%d %H:%M:%S")
        ET.SubElement(second_root, "ID").text = "1"

        lesson_id = 2  # 从2开始，因为1已经用于second_root

        for lesson_title, lesson_words in lessons_content:
            lesson_element = ET.SubElement(second_root, "SuperMemoElement")
            ET.SubElement(lesson_element, "Type").text = "Topic"
            ET.SubElement(lesson_element, "Title").text = lesson_title
            ET.SubElement(lesson_element, "ID").text = str(lesson_id)
            lesson_id += 1

            # 从lesson_title中提取课程编号
            lesson_number = lesson_title.split('_')[0]
            lesson_name = '_'.join(lesson_title.split('_')[1:])
            lesson_folder = f'lesson_{lesson_number}_{lesson_name}'
            lesson_folder = lesson_folder.rstrip('_')  # 移除末尾的下划线

            for text, audio_filename in lesson_words:
                word_element = ET.SubElement(lesson_element, "SuperMemoElement")
                ET.SubElement(word_element, "Type").text = "Topic"
                ET.SubElement(word_element, "ID").text = str(lesson_id)
                lesson_id += 1

                content = ET.SubElement(word_element, "Content")
                ET.SubElement(content, "Question").text = text

                sound = ET.SubElement(content, "Sound")
                ET.SubElement(sound, "Text").text = os.path.splitext(audio_filename)[0]
                ET.SubElement(sound, "URL").text = os.path.abspath(os.path.join('lingohut_content', lesson_folder, audio_filename))
                ET.SubElement(sound, "Name").text = audio_filename

        return root

    def scrape_lingohut(start_lesson=1, end_lesson=None):
        base_url = "https://www.lingohut.com"
        list_url = f"{base_url}/zh/l1/%E5%AD%A6%E4%B9%A0%E8%8B%B1%E8%AF%AD"
        
        print(f"Navigating to {list_url}")
        driver.get(list_url)
        print("Page loaded")

        print("Parsing page content")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        print("Finding lesson links")
        lesson_links = soup.find_all('div', class_='lesson-index-link')
        
        if lesson_links:
            print(f"Found {len(lesson_links)} lesson links")
            lessons_content = []  # 初始化 lessons_content 列表
            
            for index, link in enumerate(lesson_links, start=1):
                if index < start_lesson:
                    continue
                if end_lesson and index > end_lesson:
                    break

                lesson_numbers = link.find_all('span', class_='lesson-number')
                lesson_name = link.find('span', class_='lesson-name')
                
                if lesson_numbers and lesson_name:
                    lesson_number = '_'.join([num.text.strip() for num in lesson_numbers])
                    lesson_title = f"{lesson_number}_{lesson_name.text.strip()}"
                    
                    parent_a = link.find_parent('a')
                    if parent_a and 'href' in parent_a.attrs:
                        lesson_url = parent_a['href']
                        if not lesson_url.startswith('http'):
                            lesson_url = base_url + lesson_url
                        
                        print(f"Scraping Lesson {index}: {lesson_title}, URL: {lesson_url}")
                        
                        lesson_content = scrape_lesson_content(lesson_url)
                        
                        if lesson_content:
                            lesson_dir = f'lingohut_content/lesson_{lesson_number}_{lesson_name.text.strip().replace(" ", "_")}'
                            lesson_dir = lesson_dir.rstrip('_')  # 移除末尾的下划线
                            os.makedirs(lesson_dir, exist_ok=True)
                            
                            lesson_words = []
                            for j, (text, audio_url) in enumerate(lesson_content, 1):
                                audio_filename = f'audio_{lesson_number}{j:03d}.mp3'
                                
                                # 下载音频
                                download_audio(audio_url, os.path.join(lesson_dir, audio_filename))
                                
                                lesson_words.append((text, audio_filename))
                            
                            lessons_content.append((lesson_title, lesson_words))
                        else:
                            print(f"No content found for lesson: {lesson_title}")
                    else:
                        print(f"No parent <a> tag found for lesson: {lesson_title}")
                    
                    # 添加随机延迟，避免被网站封锁
                    time.sleep(random.uniform(2, 5))
        else:
            print("No lesson links found with class 'lesson-index-link'")

        # 生成 XML 文件
        root = create_supermemo_xml(lessons_content)
        xml_string = prettify(root)
        file_name = f'lingohut_english_lessons_{start_lesson}_to_{end_lesson or "end"}.xml'
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        print(f"XML file '{file_name}' generated successfully")

        print("Quitting driver")
        driver.quit()
        print("Driver quit successfully")

    # 在主函数中调用 scrape_lingohut 时，你可以指定开始和结束的课程编号
    if __name__ == "__main__":
        try:
            # 例如，下载第 1 课到第 10 课
            # scrape_lingohut(start_lesson=1, end_lesson=3)
            scrape_lingohut()
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            print(traceback.format_exc())

    print("Script ended")

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    print(traceback.format_exc())

print("Script ended")