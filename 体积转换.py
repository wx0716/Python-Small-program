# 体积单位转换系数（以升为基准）
conversion_to_l = {
    # 公制单位
    '立方米': 1000, 'm³': 1000, 'm3': 1000, 'cubic meter': 1000,
    '升': 1, 'l': 1, 'liter': 1, 'litre': 1,
    '毫升': 0.001, 'ml': 0.001, 'milliliter': 0.001,

    # 美制单位
    '美制加仑': 3.78541, 'us gallon': 3.78541, 'gal': 3.78541,
    '品脱': 0.473176, 'us pint': 0.473176, 'pt': 0.473176,
    '夸脱': 0.946353, 'us quart': 0.946353, 'qt': 0.946353,

    # 英制单位
    '英制加仑': 4.54609, 'imperial gallon': 4.54609,

    # 其他单位
    '立方英尺': 28.3168, 'cubic foot': 28.3168, 'ft³': 28.3168,
    '立方英寸': 0.0163871, 'cubic inch': 0.0163871, 'in³': 0.0163871
}

print("欢迎使用体积转换器！")
print("支持的单位示例：")
print("- 立方米 (m³, m3, cubic meter)")
print("- 升 (L, liter, litre)")
print("- 毫升 (mL, milliliter)")
print("- 美制加仑 (gal, us gallon)")
print("- 英制加仑 (imperial gallon)")
print("- 立方英尺 (ft³, cubic foot)")
print("- 立方英寸 (in³, cubic inch)")
print("- 品脱 (pt, us pint)")
print("- 夸脱 (qt, us quart)")

try:
    value = float(input("\n请输入要转换的数值："))
except ValueError:
    print("错误：请输入有效的数字。")
    exit()

from_unit = input("请输入原单位：").strip()
to_unit = input("请输入目标单位：").strip()

if from_unit not in conversion_to_l:
    print(f"错误：原单位 '{from_unit}' 不支持。")
    exit()

if to_unit not in conversion_to_l:
    print(f"错误：目标单位 '{to_unit}' 不支持。")
    exit()

# 执行单位转换计算
base_liters = value * conversion_to_l[from_unit]
result = base_liters / conversion_to_l[to_unit]

# 输出结果（自动控制小数位数）
print(f"\n转换结果：{value} {from_unit} = {result:.6g} {to_unit}")