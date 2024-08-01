import pandas as pd
import json

# 指定Excel文件路径
excel_path = 'data.xlsx'
# 指定工作表名称，默认为第一个工作表
sheet_name = 'Sheet1'
# 指定输出的JSON文件路径
output_json_path = 'vocalbList.json'

# 使用pandas读取Excel文件
df = pd.read_excel(excel_path, sheet_name=sheet_name)

# 将DataFrame转换为JSON格式
json_data = df.to_json(orient='records', force_ascii=False)

# 将JSON数据写入到文件
with open(output_json_path, 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

print(f"数据已成功转换并保存到 {output_json_path}")