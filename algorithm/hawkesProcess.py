import numpy as np
import scipy.stats


# 使用指数核计算时间衰减的影响
def kernel(current_time, history_time, omega):
    return omega * np.exp(-omega * (current_time - history_time))


# 从参数为namuta的指数分布中进行采样
def samplefromExponential(namuta):
    C = scipy.stats.expon(scale=namuta)
    rv = C.rvs()
    return rv


# 计算t时刻第i维的强度
def cal_natmuta_i_sum(mu, alpha, omega, history, ajacencymatrix, t, i):
    namutai = mu[i]
    '''his=(retweeter,tweeter,time)'''
    for his in history:
        if ajacencymatrix[i][his[0]] == 1:
            namutai += alpha[his[0]][i] * kernel(t, his[2], omega)
    return namutai


# 计算t时刻所有维度强度之和
def cal_namutastarsum(mu, alpha, omega, history, ajacencymatrix, t):
    dim = mu.shape[0]
    sum = 0.0
    for i in range(dim):
        sum += cal_natmuta_i_sum(mu, alpha, omega, history, ajacencymatrix, t, i)
    return sum


# 基于霍克斯过程的预测
def multidimensional_sim(mu, alpha, omega, T, ajacencymatrix, numEvents):
    history = []
    hiswithouttime = []
    dim = mu.shape[0]
    t = 0.0
    # 由于数据中节点总数只有100个，这里选择pagerank值最高的节点作为初始节点
    n0 = 65
    namutahat = 0.0
    namutastarsum = 0.0
    history.append((n0, n0, t))
    count = 1
    quit=False
    while count <= numEvents:
        '''begin sample nextevent'''
        namutastarsum = cal_namutastarsum(mu, alpha, omega, history, ajacencymatrix, t)
        namutahat = namutastarsum
        # s：从namutahat的指数分布中采样得到：
        s = samplefromExponential(namutahat)
        t += s
        if t >= T:
            break
        '''start rejection test'''
        namutapingjun = cal_namutastarsum(mu, alpha, omega, history, ajacencymatrix, t)  # 这里的t是t‘
        d = np.random.uniform(0, 1, 1)
        if d * namutahat > namutapingjun:
            continue
        '''start attribution test'''
        d = np.random.uniform(0, 1, 1)
        capital_S = 0.0
        for i in range(dim):
            quit=False
            capital_S += cal_natmuta_i_sum(mu, alpha, omega, history, ajacencymatrix, t, i)
            if capital_S >= d:
                for j in range(len(history) - 1, -1, -1):
                    retw = [(x[0]) for x in history]
                    if (ajacencymatrix[i][history[j][0]] == 1) and i not in retw:  # 转发过一次就不能在转发第二次了
                        history.append((i, history[j][0], t))
                        count += 1
                        quit=True
                        break
            if  quit:
                break

    his = []
    #print(count)

    for i in range(len(history)):
        his.append((history[i][0], history[i][1], i))

    return his