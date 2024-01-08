import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3
import scipy.spatial as sp  # For ConvexHull, SphericalVoronoi
from pyroomacoustics.doa import GridSphere


# 簡単なテスト関数を定義
def test_func(x, y, z):
    return z


# GridSphere クラスをインスタンス化
grid_sphere = GridSphere()

# テスト関数を適用
# grid_sphere.valuesに値が格納される
# grid_sphere.valuesを後ろのプロットで使用するため
grid_sphere.apply(test_func)

# プロット用の準備
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.set_box_aspect([1,1,1])

# grid_sphere.cartesian.shape = (3, n_points)
# x,y,zの3次元座標が格納されている
voronoi = sp.SphericalVoronoi(grid_sphere.cartesian.T)
voronoi.sort_vertices_of_regions()

# 点の値に応じた色を決定
col_max = grid_sphere.values.max()
col_min = grid_sphere.values.min()
col_map = (grid_sphere.values - col_min) / (col_max - col_min) if col_min != col_max else grid_sphere.values / col_max
cmap = plt.get_cmap("coolwarm")

# Voronoi領域をプロット
for v_ind, col in zip(voronoi.regions, col_map):
    triangle = a3.art3d.Poly3DCollection([voronoi.vertices[v_ind]], alpha=0.5, linewidth=1.0)
    triangle.set_color(cmap(col))
    triangle.set_edgecolor("k")
    ax.add_collection3d(triangle)

# 軸ラベルと範囲を設定
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])

# プロットを表示
plt.show()
