###
# 说明：这个文件生成的xml导入进去是item卡，可直接进行测试使用。
# 
# 
# 
# 
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import glob
import logging
import time
import uuid
logging.basicConfig(level=logging.INFO)

from datetime import datetime

time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logging.info(f"time_string: {time_string}")

def create_supermemo_xml(folder_path, output_file):

    lrc_files = glob.glob(r'*.lrc')

    lrc_file_count = len(lrc_files)
    logging.info(f"lrc_file_count: {lrc_file_count}")
    
    flist_mp3 = glob.glob(r'*.mp3')

    # Create the root element
    root = ET.Element("SuperMemoCollection")
    ET.SubElement(root, "Count").text =  str(lrc_file_count)
    
    secondRoot =  ET.SubElement(root, "SuperMemoElement")
    ET.SubElement(secondRoot, "Type").text = "Topic"
    ET.SubElement(secondRoot, "Title").text = time_string
    # random_id = str(uuid.uuid4())
    ET.SubElement(secondRoot, "ID").text = "111"
                



    # Get all LRC files in the folder
    


    for lrc_file in lrc_files:
        logging.info(f"lrc_file: {lrc_file}")
        # Find the corresponding MP3 file
        mp3_file = lrc_file.replace('.lrc', '.mp3')
        logging.info(mp3_file)
        if not os.path.exists(os.path.join(folder_path, mp3_file)):
            print(f"Warning: No matching MP3 file found for {lrc_file}")
            continue

        # Parse the LRC file
        with open(os.path.join(folder_path, lrc_file), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            logging.info(f"lines: {lines}")

        # Process each line in the LRC file
        for line in lines:
            logging.info(f"line: {line}")
            # if line.strip() :  # Ignore empty lines and time stamps
            # if line.strip() and not line.startswith('['):  # Ignore empty lines and time stamps
                # Create a new SuperMemoElement
                
            element = ET.SubElement(secondRoot, "SuperMemoElement")
            
            # Set the Type
            ET.SubElement(element, "Type").text = "Item"
         
            filename_without_extension = os.path.splitext(lrc_file)[0]
            ET.SubElement(element, "ID").text = filename_without_extension
            
            # Create the Content element
            content = ET.SubElement(element, "Content")
            
            # Set Question and Answer (assuming the line contains both, separated by a delimiter)
            parts = line.strip().split('|')  # Adjust the delimiter as needed
            logging.info(f"len(parts): {len(parts)}")
            ####
            ### 对英文和翻译的部分进行处理
            # 使用split()方法
            # 获得英文和翻译部分
            text = line.split(']', 1)[1]  # 去掉时间轴部分
            logging.info(f"text: {text}")
            # 分割后取第二部分
            english_text = text.split('\t\t')[0]

            chinese_text = text.split('\t\t')[1]
            logging.info(f"english_text: {english_text}")
            logging.info(f"chinese_text: {chinese_text}")

            ET.SubElement(content, "Question").text = english_text # 分割后取第二部分
            ET.SubElement(content, "Answer").text = chinese_text  # 分割后取第二部分
            
            # Add Sound element
            sound = ET.SubElement(content, "Sound")
            ET.SubElement(sound, "Text").text = os.path.splitext(mp3_file)[0]
            ET.SubElement(sound, "URL").text = os.path.abspath(os.path.join(folder_path, mp3_file))
            ET.SubElement(sound, "Name").text = mp3_file
            # ET.SubElement(sound, "Answer").text = "T"

    # Create a formatted XML string
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    # Write to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

# Example usage
folder_path = ''
output_file = 'output.xml'

create_supermemo_xml(folder_path, output_file)
print(f"XML file has been created: {output_file}")
