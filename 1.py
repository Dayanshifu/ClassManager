from pypinyin import lazy_pinyin  
  
# 原始数据加上新增的数据  
data = {  
    '张三': 0,  
    '李四': 0,  
    '王五': 0,  
    '赵六': 0,  
    '孙七': 0,  
    '周八': 0,  
    '吴九': 0,  
    '郑十': 0,  
    '陈十一': 0,  
    '蒋十二': 0,  
    '沈十三': 0,  
    '韩十四': 0,  
}  
  
# 使用lazy_pinyin将中文名字转换为拼音列表，并排序  
sorted_keys = sorted(data.keys(), key=lambda x: ''.join(lazy_pinyin(x)))  
  
# 根据排序后的键重建一个有序字典  
sorted_data = {k: data[k] for k in sorted_keys}  
  
# 打印排序后的数据  
print(sorted_data)