# Aboboo2Xml
将Aboboo中导出的文件，合并成xml文件，供SuperMemo导入使用。
详细操作说明见：[如何批量将音频和字幕导入到SuperMemo中.md](如何批量将音频和字幕导入到SuperMemo中.md)

将文件放在aboboo导出的文件夹里面。

双击执行本文件，可生成一个xml文件，在SuperMemo中导入本文件即可。

目前可实现将mp3导入SuperMemo中，将字幕也添加过来，

[aboboo2xml.py](aboboo2xml.py)  是将转为摘录卡片，可以自行手动进行挖空的操作。有一个小问题时，目前添加过来的卡片模板仍然是item的样式，就是带有问答部分的部分，需要手动删除一下。

[supermemo-xml-item.py](supermemo-xml-item.py)  是将转为测试卡片，问题是英文，答案是翻译这样的。



