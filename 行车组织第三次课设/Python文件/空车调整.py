"""
# @author : 何俊锋
# @time : 2024/06/13 0:50
# @function: 此文件用于计算行车组织第三次课设最优空车调整方案.
"""


import pulp
import re


def solve(dist, loss):
    n = len(dist)  # number of intervals

    # 1.定义问题为最小值问题
    prob = pulp.LpProblem('Min_empty_distance', sense=pulp.LpMinimize)

    # 2.定义决策变量，即每个区间的上下行空车运送量
    x_up = [pulp.LpVariable(f'x_up{i+1}', lowBound=0, cat='Integer') for i in range(n)]
    x_down = [pulp.LpVariable(f'x_down{i+1}', lowBound=0, cat='Integer') for i in range(n)]

    # 3.定义目标函数，即空车走行公里最小
    total_distance = sum(dist[i] * (x_up[i] + x_down[i]) for i in range(len(dist)))
    prob += total_distance

    # 4.定义约束条件，即每个站不应有空车剩余或缺少
    prob += (loss[0] + x_up[0] + x_down[1] - x_up[1] - x_down[0] == 0)
    prob += (loss[1] + x_up[1] + x_down[2] - x_up[2] - x_down[1] == 0)
    prob += (loss[2] + x_up[2] + x_down[3] - x_up[3] - x_down[2] == 0)
    prob += (loss[3] + x_up[3] + x_down[4] - x_up[4] - x_down[3] == 0)
    prob += (loss[4] + x_up[4] + x_down[5] - x_up[5] - x_down[4] == 0)
    prob += (loss[5] + x_up[5] + x_down[6] - x_up[6] - x_down[5] == 0)
    prob += (loss[6] + x_up[6] + x_down[7] - x_up[7] - x_down[6] + x_up[11] - x_down[11] == 0)
    prob += (loss[7] + x_up[7] + x_down[8] - x_up[8] - x_down[7] == 0)
    prob += (loss[8] + x_up[8] + x_down[9] - x_up[9] - x_down[8] == 0)
    prob += (loss[9] + x_up[9] + x_down[10] - x_up[10] - x_down[9] == 0)
    prob += (loss[10] - x_up[11] - x_down[12] + x_up[12] + x_down[11] == 0)
    prob += (loss[11] - x_up[12] - x_down[13] + x_up[13] + x_down[12] == 0)
    prob += (loss[12] - x_up[13] - x_down[14] + x_up[14] + x_down[13] == 0)
    prob += (loss[13] + x_down[15] - x_up[15] == 0)
    prob += (loss[14] + x_up[15] + x_down[16] - x_up[16] - x_down[15] == 0)
    prob += (loss[15] + x_up[16] + x_down[17] - x_up[17] - x_down[16] == 0)
    prob += (loss[16] + x_up[17] + x_down[18] - x_up[18] - x_down[17] == 0)
    prob += (loss[17] + x_up[18] + x_up[19] + x_down[14] - x_down[18] - x_down[19] - x_up[14] == 0)
    prob += (loss[18] - x_up[19] - x_down[20] + x_up[20] + x_down[19] == 0)
    prob += (loss[19] - x_up[20] - x_down[21] + x_up[21] + x_down[20] + x_up[23] - x_down[23] == 0)
    prob += (loss[20] - x_up[21] - x_down[22] + x_up[22] + x_down[21] == 0)
    prob += (loss[21] - x_up[22] + x_down[22] == 0)
    prob += (loss[22] - x_up[23] - x_down[24] + x_up[24] + x_down[23] == 0)
    prob += (loss[23] - x_up[24] + x_down[24] == 0)

    # 5.求解并输出结果
    prob.solve()
    xu = [0 for _ in range(n)]
    xd = [0 for _ in range(n)]
    pattern = re.compile(r'[0-9]+')
    for v in prob.variables():
        id = pattern.findall(v.name)
        if 'up' in v.name:
            xu[int(id[0])-1] = v.varValue
        else:
            xd[int(id[0]) - 1] = v.varValue
    res = 0
    for i in range(n):
        if xu[i] == 0 and xd[i] == 0:
            print(f'区间{i+1}不运送空车')
            continue
        if i == 0:
            print(f'F分界站向M局运送{xu[i]+xd[i]}辆空车')
            continue
        if i == 10:
            print(f'A分界站向M局运送{xu[i] + xd[i]}辆空车')
            continue
        if xu[i] != 0:
            res += xu[i]*dist[i]
            print(f"区间{i+1}向[上行]方向运送空车{int(xu[i])}辆空车, 该区间长度为{dist[i]}, 当前总空车走行距离为{res}")
        else:
            res += xd[i] * dist[i]
            print(f"区间{i + 1}向[下行]方向运送空车{int(xd[i])}辆空车, 该区间长度为{dist[i]}, 当前总空车走行距离为{res}")
    print("最短空车走行距离为", pulp.value(prob.objective))  # 输出最优解的目标函数值
    

dist = [0, 70, 70, 75, 75, 77, 77, 85, 85, 105, 105,
        65, 65, 60, 60, 90, 90, 60, 60, 55, 55, 40, 40, 40, 40]
loss = [-6, -6, -39, 13, 11, -34, 12, -3, 64, -27, -125,
        -13, 73, 18, 16, 26, -79, 76, -25, 17, 2, 65, -10, -156]
solve(dist, loss)
