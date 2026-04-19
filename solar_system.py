import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse
from matplotlib.patheffects import withStroke
import random

import matplotlib.pyplot as plt
# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 用黑体，Mac 用 'PingFang SC'
plt.rcParams['axes.unicode_minus'] = False    # 解决负号 '-' 显示为方块的问题

#全局配置字典 
CONFIG = {
    # 画布
    "figsize": (12, 9),
    "xlim": (-5.8, 5.8),
    "ylim": (-4, 4),
    # 太阳
    "sun_color": "#FDB813",
    "sun_size": 0.22,
    # 行星数据 (名称, 轨道半径, 颜色, 半径尺寸, 标签额外偏移)
    "planets": [
        ('水星', 0.8, '#8C7853', 0.06, (0.15, 0.1)),
        ('金星', 1.2, '#FFC649', 0.09, (0.15, 0.1)),
        ('地球', 1.6, '#1E90FF', 0.09, (0.15, 0.1)),
        ('火星', 2.2, '#CD5C5C', 0.07, (0.15, 0.1)),
        ('木星', 3.2, '#D2B48C', 0.22, (0.2, 0.15)),
        ('土星', 4.0, '#F0E68C', 0.20, (0.2, 0.15)),
        ('天王星', 4.6, '#4FD0E7', 0.14, (0.15, 0.1)),
        ('海王星', 5.0, '#4169E1', 0.14, (0.15, 0.1)),
    ],
    # 月球
    "moon_distance": 0.25,
    "moon_size": 0.04,
    "moon_color": "#C0C0C0",
    # 土星光环
    "ring_tilt": 27,
    "ring_inner_size": (0.55, 0.18),
    "ring_outer_size": (0.62, 0.13),
    # 小行星带
    "asteroid_r_min": 2.2,
    "asteroid_r_max": 3.0,
    "asteroid_count": 1200,
    # 哈雷彗星
    "comet_a": 4.0,  # 半长轴
    "comet_b": 2.0,  # 半短轴
    "comet_tilt": 30,  # 轨道倾角(度)
    "comet_angle": 120,  # 真近点角(度)，可随机
    # 星星
    "star_count": 450,
    # 轨道箭头
    "arrow_base_angles": [30, 120, 210, 300],
    "arrow_head_width": 0.08,
    "arrow_head_length": 0.1,
}

# 随机种子：设为 None 则每次运行画面不同，固定数字可复现
RANDOM_SEED = 42  # 改为 None 获得完全随机
if RANDOM_SEED is not None:
    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)

# 绘图设置 
plt.rcParams['figure.facecolor'] = 'black'
plt.rcParams['axes.facecolor'] = 'black'

fig, ax = plt.subplots(figsize=CONFIG["figsize"])
ax.set_xlim(CONFIG["xlim"])
ax.set_ylim(CONFIG["ylim"])
ax.set_aspect('equal')
ax.axis('off')

# 标签描边样式（统一管理）
label_style = {
    "color": "white",
    "fontsize": 10,
    "path_effects": [withStroke(linewidth=2, foreground="black")]
}
small_label_style = {
    "color": "white",
    "fontsize": 8,
    "path_effects": [withStroke(linewidth=1, foreground="black")]
}

# 背景星星 
x_stars = np.random.uniform(*CONFIG["xlim"], CONFIG["star_count"])
y_stars = np.random.uniform(*CONFIG["ylim"], CONFIG["star_count"])
star_sizes = np.random.uniform(1, 10, CONFIG["star_count"])
star_colors = np.random.choice(['white', 'lightblue', 'lightyellow', 'pink'],
                               CONFIG["star_count"])
star_alphas = np.random.uniform(0.5, 1, CONFIG["star_count"])
ax.scatter(x_stars, y_stars, s=star_sizes, c=star_colors,
           alpha=star_alphas, zorder=0)

# 太阳与光晕
sun = Circle((0, 0), CONFIG["sun_size"], color=CONFIG["sun_color"],
             zorder=10, ec='orange', linewidth=1)
ax.add_patch(sun)
for rad, alpha in [(0.3, 0.2), (0.4, 0.1), (0.5, 0.05)]:
    glow = Circle((0, 0), rad, color=CONFIG["sun_color"], alpha=alpha, zorder=9)
    ax.add_patch(glow)
ax.text(0.3, 0, '太阳', **label_style)

# 行星与轨道 
# 为每颗行星生成随机角度（弧度）
planet_angles = np.random.uniform(0, 2 * np.pi, len(CONFIG["planets"]))
planet_positions = []  # 存储位置用于后续箭头避让

for i, (name, r, color, size, offset) in enumerate(CONFIG["planets"]):
    angle = planet_angles[i]
    x = r * np.cos(angle)
    y = r * np.sin(angle)
    planet_positions.append((r, angle))  # 记录轨道半径和角度

    # 轨道（正圆）
    orbit = Circle((0, 0), r, fill=False, linewidth=1,
                   edgecolor='yellow', alpha=0.5)
    ax.add_patch(orbit)

    # 行星
    planet = Circle((x, y), size, color=color, zorder=10,
                    ec='white', linewidth=0.5)
    ax.add_patch(planet)

    # 标签智能放置：始终放在行星外侧（远离太阳的方向）
    label_dir = np.arctan2(y, x)  # 行星方位角
    label_r = r + 0.25  # 标签距离太阳稍远
    label_x = label_r * np.cos(label_dir)
    label_y = label_r * np.sin(label_dir)
    # 微调避免与轨道线重叠
    if x >= 0:
        label_x += offset[0]
        label_y += offset[1]
    else:
        label_x -= offset[0]
        label_y -= offset[1]
    ax.text(label_x, label_y, name, **label_style)

#月球（绕地球）
# 地球位置从上面获取
earth_idx = [p[0] for p in CONFIG["planets"]].index('地球')
earth_angle = planet_angles[earth_idx]
earth_r = CONFIG["planets"][earth_idx][1]
earth_x = earth_r * np.cos(earth_angle)
earth_y = earth_r * np.sin(earth_angle)

# 月球随机角度
moon_angle = np.random.uniform(0, 2 * np.pi)
moon_x = earth_x + CONFIG["moon_distance"] * np.cos(moon_angle)
moon_y = earth_y + CONFIG["moon_distance"] * np.sin(moon_angle)

moon = Circle((moon_x, moon_y), CONFIG["moon_size"], color=CONFIG["moon_color"],
              zorder=11, ec='white', linewidth=0.3)
ax.add_patch(moon)
# 月球轨道（极细虚线）
moon_orbit = Circle((earth_x, earth_y), CONFIG["moon_distance"],
                    color='gray', fill=False, linewidth=0.6,
                    linestyle=':', alpha=0.6)
ax.add_patch(moon_orbit)
ax.text(moon_x + 0.1, moon_y + 0.05, '月球', **small_label_style)

# 土星光环（更真实倾角）
saturn_idx = [p[0] for p in CONFIG["planets"]].index('土星')
saturn_angle = planet_angles[saturn_idx]
saturn_r = CONFIG["planets"][saturn_idx][1]
saturn_x = saturn_r * np.cos(saturn_angle)
saturn_y = saturn_r * np.sin(saturn_angle)
#内层主环：更粗、更亮
ring1 = Ellipse((saturn_x, saturn_y), *CONFIG["ring_inner_size"],
                angle=CONFIG["ring_tilt"], color='#F0E68C',
                fill=False, linewidth=3.0, alpha=0.9)
ax.add_patch(ring1)
#外层次光环：颜色对比更强
ring2 = Ellipse((saturn_x, saturn_y), *CONFIG["ring_outer_size"],
                angle=CONFIG["ring_tilt"], color='#DAA520',
                fill=False, linewidth=2.0, alpha=0.7)
ax.add_patch(ring2)


# 小行星带（均匀半径 + 密度渐变） 
n_ast = CONFIG["asteroid_count"]
r_ast = np.random.uniform(CONFIG["asteroid_r_min"], CONFIG["asteroid_r_max"], n_ast)
theta_ast = np.random.uniform(0, 2 * np.pi, n_ast)
x_ast = r_ast * np.cos(theta_ast)
y_ast = r_ast * np.sin(theta_ast)

# 径向密度权重：中心最密，边缘渐疏
density_weight = 1 - (r_ast - CONFIG["asteroid_r_min"]) / \
                 (CONFIG["asteroid_r_max"] - CONFIG["asteroid_r_min"])
ax.scatter(x_ast, y_ast, s=1.0, c='white', alpha=density_weight * 0.5)

# 小行星带标签（放在右半侧空白处）
ax.text(3.0, -0.5, '小行星带', **label_style)

# 哈雷彗星（太阳为焦点）
# 椭圆参数：半长轴 a，半短轴 b，焦点在 (0,0)
a = CONFIG["comet_a"]
b = CONFIG["comet_b"]
c = np.sqrt(a ** 2 - b ** 2)  # 焦距
center_x = -c  # 椭圆中心 x 坐标（太阳在右焦点）

# 彗星轨道（椭圆，中心在 (-c, 0)）
comet_orbit = Ellipse((center_x, 0), 2 * a, 2 * b, angle=CONFIG["comet_tilt"],
                      color='lightblue', fill=False, linewidth=1, alpha=0.5)
ax.add_patch(comet_orbit)

# 彗星位置：真近点角 f（从焦点出发的角度）
f_deg = CONFIG["comet_angle"] if not None else np.random.uniform(0, 360)
f = np.radians(f_deg)
# 以焦点为原点的极坐标方程 r = a(1-e^2)/(1+e*cos(f))，e = c/a
e = c / a
r_comet = a * (1 - e ** 2) / (1 + e * np.cos(f))
x_focus = r_comet * np.cos(f)  # 相对于焦点(0,0)
y_focus = r_comet * np.sin(f)
# 旋转轨道倾角
x_comet = x_focus * np.cos(np.radians(CONFIG["comet_tilt"])) - \
          y_focus * np.sin(np.radians(CONFIG["comet_tilt"]))
y_comet = x_focus * np.sin(np.radians(CONFIG["comet_tilt"])) + \
          y_focus * np.cos(np.radians(CONFIG["comet_tilt"]))

# 彗星本体
ax.scatter(x_comet, y_comet, s=40, color='white', edgecolor='lightblue',
           linewidth=0.5, zorder=15)

# 彗尾：粒子尾迹（背离太阳方向）
tail_dir = np.array([x_comet, y_comet])  # 从太阳指向彗星
tail_dir = tail_dir / np.linalg.norm(tail_dir)
for i in range(20):
    dist = i * 0.08
    alpha = 0.2 * (1 - i / 20)  # 逐渐透明
    size = 8 * (1 - i / 20) + 2
    tx = x_comet + tail_dir[0] * dist
    ty = y_comet + tail_dir[1] * dist
    ax.scatter(tx, ty, s=size, c='white', alpha=alpha, linewidth=0)

ax.text(x_comet + 0.2, y_comet + 0.2, '哈雷彗星', **label_style)


# 轨道方向箭头（智能避让行星） 
def draw_orbit_arrow(ax, r, angle_deg, head_width, head_length):
    """在半径为 r 的圆轨道上 angle_deg 处画逆时针箭头"""
    x = r * np.cos(np.radians(angle_deg))
    y = r * np.sin(np.radians(angle_deg))
    dx = -0.15 * np.sin(np.radians(angle_deg))
    dy = 0.15 * np.cos(np.radians(angle_deg))
    ax.arrow(x, y, dx, dy,
             head_width=head_width, head_length=head_length,
             fc='white', ec='white', alpha=0.6, width=0.003)


# 为每个轨道半径画箭头
for r in [p[1] for p in CONFIG["planets"]]:
    # 找出这个轨道上行星的角度（如果有）
    planet_angles_on_this_r = [ang for rad, ang in planet_positions if abs(rad - r) < 0.01]
    # 生成基础角度列表，避开行星 ±30 度
    safe_angles = []
    for base_ang in CONFIG["arrow_base_angles"]:
        # 检查是否与任何行星角度冲突
        conflict = False
        for p_ang in planet_angles_on_this_r:
            p_deg = np.degrees(p_ang) % 360
            diff = abs((base_ang - p_deg + 180) % 360 - 180)
            if diff < 30:
                conflict = True
                break
        if not conflict:
            safe_angles.append(base_ang)
    # 如果全部冲突，回退到基础角度（但偏移15度）
    if not safe_angles:
        safe_angles = [(a + 15) % 360 for a in CONFIG["arrow_base_angles"]]

    hw = CONFIG["arrow_head_width"] * (0.6 if r < 2.5 else 1.0)
    hl = CONFIG["arrow_head_length"] * (0.6 if r < 2.5 else 1.0)
    for ang in safe_angles[:4]:  # 最多4个箭头
        draw_orbit_arrow(ax, r, ang, head_width=hw, head_length=hl)

# 标题与比例说明 
ax.text(0, -3.8, '太阳系示意图（大小与距离未按实际比例）',
        color='gray', fontsize=11, ha='center',
        path_effects=[withStroke(linewidth=1, foreground='black')])

plt.tight_layout()

# 如需保存高清图
plt.savefig('solar_system_optimized.png', dpi=300, bbox_inches='tight', facecolor='black')

plt.show()