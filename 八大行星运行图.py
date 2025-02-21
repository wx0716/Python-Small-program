import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import font_manager

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体为 SimHei（黑体）
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 设置行星的轨道半径（相对值）和运行速度
planet_radius = [0.39, 0.72, 1.0, 1.52, 5.20, 9.58, 19.22, 30.05]  # 行星轨道半径（天文单位）
planet_speed = [4.74, 3.50, 2.98, 2.41, 1.31, 0.97, 0.68, 0.54]      # 行星运行速度（相对值）

# 行星名称
planet_names = ["水星", "金星", "地球", "火星", "木星", "土星", "天王星", "海王星"]

# 行星颜色（根据实际行星颜色调整）
planet_colors = [
    "gray",    # 水星
    "gold",    # 金星
    "blue",    # 地球
    "red",     # 火星
    "orange",  # 木星
    "yellow",  # 土星
    "cyan",    # 天王星
    "navy"     # 海王星
]

# 行星大小（根据实际行星大小调整）
planet_sizes = [0.38, 0.95, 1.0, 0.53, 11.2, 9.45, 4.0, 3.88]  # 行星大小（相对地球大小）

# 创建画布和子图
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_xlim(-35, 35)
ax.set_ylim(-35, 35)
ax.set_aspect("equal")
ax.axis("off")  # 隐藏坐标轴

# 设置背景颜色（模拟星空）
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

# 绘制太阳
sun = plt.Circle((0, 0), 2.0, color="yellow", label="太阳")
ax.add_patch(sun)

# 绘制行星轨道
for radius in planet_radius:
    orbit = plt.Circle((0, 0), radius, color="white", fill=False, linestyle="--", linewidth=0.5)
    ax.add_patch(orbit)

# 初始化行星的位置
planets = [plt.Circle((radius, 0), size * 0.1, color=color) for radius, size, color in zip(planet_radius, planet_sizes, planet_colors)]
for planet in planets:
    ax.add_patch(planet)

# 添加行星名称标签
labels = [ax.text(radius, 0, name, fontsize=10, ha="center", color="white") for radius, name in zip(planet_radius, planet_names)]

# 更新函数，用于动态更新行星位置
def update(frame):
    for i, (planet, speed) in enumerate(zip(planets, planet_speed)):
        angle = 2 * np.pi * (frame * speed / 200)  # 计算行星的角度
        x = planet_radius[i] * np.cos(angle)       # 计算行星的x坐标
        y = planet_radius[i] * np.sin(angle)       # 计算行星的y坐标
        planet.center = (x, y)                     # 更新行星位置
        labels[i].set_position((x, y + 1.5))       # 更新标签位置
    return planets + labels

# 创建动画
ani = animation.FuncAnimation(fig, update, frames=400, interval=20, blit=True)

# 添加标题
plt.title("八大行星运行图", fontsize=16, color="white", pad=20)

# 显示动画
plt.show()