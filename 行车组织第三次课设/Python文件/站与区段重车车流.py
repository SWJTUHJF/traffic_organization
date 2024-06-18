"""
整体思路：
1.对每个站创建Station类实例，用于存储不同类型流量及上下行节点
2.用Pandas读取重车车流信息：起始点，终到点及重车流
3.M铁路局的车站布局可以视为一个二叉树。两个站间的走行径路可以用最近公共祖先算法求解。
4.对径路上的每个站进行对应流量调整
"""
import re
import pandas as pd


class Station:
    def __init__(self, name, up_s=None):
        self.name = name  # name of the station
        self.upf = 0  # downstream pass flow
        self.dpf = 0  # upstream pass flow
        self.uaf = 0  # downstream arrive flow
        self.daf = 0  # upstream arrive flow
        self.usf = 0  # downstream start flow
        self.dsf = 0  # upstream start flow
        self.up_s = up_s  # upstream station name
        self.l_down_s = None  # downstream station name
        self.r_down_s = None
        # 定义半段全段的管内工作车和移交车流
        self.half_inner = 0
        self.whole_inner = 0
        self.half_to_a = 0
        self.half_to_f = 0
        self.whole_to_a = 0
        self.whole_to_f = 0

    def calc_heavy_flow(self):
        return self.upf+self.usf+self.uaf+self.daf+self.dsf+self.dpf

    def calc_interval_flow(self):
        return self.half_to_a+self.half_to_f+self.half_inner+self.whole_inner+self.whole_to_f+self.whole_to_a


# 将每个站的信息用对象存储起来，STATIONS列表存储所有站对象
def process(path):
    STATIONS = []
    with open(path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    lines = lines[1:]
    pattern = re.compile(r'[A-z-]+')
    for l in lines:
        temp = pattern.findall(l)
        name = temp[0]
        upstream = temp[1]
        if upstream == 'None':
            STATIONS.append(Station(name))
        else:
            ups = find_station(upstream, STATIONS)
            new_s = Station(name, ups)
            STATIONS.append(new_s)
            if ups.l_down_s:
                ups.r_down_s = new_s
            else:
                ups.l_down_s = new_s
    return STATIONS


# 找到一个站到另一个站的路径
def lca(ori, dest, root):
    up_ori = ori.up_s
    up_dest = dest.up_s
    ori_path = [ori]
    dest_path = [dest]
    path = []
    while up_ori:
        ori_path.append(up_ori)
        up_ori = up_ori.up_s
    while up_dest:
        dest_path.append(up_dest)
        up_dest = up_dest.up_s
    for ele in ori_path:
        if ele in dest_path:
            ori_loc = ori_path.index(ele)
            dest_loc = dest_path.index(ele)
            break
    path.extend(ori_path[:ori_loc+1])
    path.extend(dest_path[:dest_loc][::-1])
    return path


# 寻找站名对应的对象
def find_station(n, stations):
    for s in stations:
        if s.name == n:
            return s


def calc_flow(STATIONS, df):
    names = ['A-B', 'B', 'B-C', 'C', 'C-G', 'G', 'G-H', 'C-D', 'D', 'D-E', 'E', 'E-F', 'F', 'H',
             'H-I', 'I', 'I-J', 'J', 'H-K', 'K', 'K-R', 'R', 'K-L', 'L', 'N', 'O']
    # 遍历站与站之间的重车流
    for k in range(len(names)):
        for l in range(len(names)):
            ori = names[k]
            dest = names[l]
            flow = df.at[k, dest]
            # 如果流量为0，跳过
            if pd.isna(flow):
                continue
            ori = find_station(ori, STATIONS)
            dest = find_station(dest, STATIONS)
            # 考虑一个区段内的管内车流，该车流又是该区段的始发车流又是终到车流
            if k == l:
                flag = flow[-1]
                flow = int(flow[:-1])
                if flag == 'u':
                    ori.usf += flow
                    ori.uaf += flow
                else:
                    ori.dsf += flow
                    ori.daf += flow
                ori.half_inner += flow
                continue
            # 1.找到起点到终点的走行路径
            path = lca(ori, dest, STATIONS)
            n = len(path)
            # 2.分别对路径上的每个站进行对应车流量的修改
            for i in range(n):
                # 考虑始发车流
                if i == 0:
                    # 如果是发往上行方向
                    if path[i+1] == path[i].up_s:
                        path[i].usf += flow
                    # 如果是发往下行方向
                    else:
                        path[i].dsf += flow
                    if path[-1].name == 'O':
                        path[i].half_to_f += flow
                    elif path[-1].name == 'N':
                        path[i].half_to_a += flow
                    else:
                        path[i].half_inner += flow
                # 考虑到达车流
                elif i == n-1:
                    # 如果是下行方向发来
                    if path[i-1].up_s == path[i]:
                        path[i].uaf += flow
                    # 如果是上行方向发来
                    else:
                        path[i].daf += flow
                    path[i].half_inner += flow
                else:
                    # 如果往上行方向发
                    if path[i].up_s == path[i+1]:
                        path[i].upf += flow
                    # 如果是上行方向发来
                    else:
                        path[i].dpf += flow
                    if path[-1].name == 'O':
                        path[i].whole_to_f += flow
                    elif path[-1].name == 'N':
                        path[i].whole_to_a += flow
                    else:
                        path[i].whole_inner += flow
    print('********************重车车流数据********************')
    for s in STATIONS:
        if s.name == 'O' or s.name == 'N':
            continue
        print(f'站名：{s.name}，上行通过：{int(s.upf)},上行到达：{int(s.uaf)}，上行出发：{int(s.usf)},下行通过：{int(s.dpf)},下行到达：{int(s.daf)},下行出发:{int(s.dsf)}, 总:{s.calc_heavy_flow()}')
    print('********************区段重车车流********************')
    for s in STATIONS:
        if '-' in s.name:
            print(f'区段:{s.name}')
            print(f'半段——管内工作车:{s.half_inner}, 向A移交车:{s.half_to_a}, 向F移交车:{s.half_to_f}')
            print(f'全段——管内工作车:{s.whole_inner}, 向A移交车:{s.whole_to_a}, 向F移交车:{s.whole_to_f}')
            print(f'总计为{s.calc_interval_flow()}')


def main():
    STATIONS = process('station_location.txt')
    df = pd.read_excel('重车车流表.xlsx')
    calc_flow(STATIONS, df)


main()
