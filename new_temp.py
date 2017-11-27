from random import *
import os
import numpy as np
##import matplotlib.pyplot as plt
##from scipy.interpolate import spline
import sys
import csv
import time
import multiprocessing as mp
import ctypes as c
import threading

# initial matrix
def initial(size,method,data):
    P = []
    if method:
        for i in range(size):
            temp = [0.5]*i
            temp2 = [0.0]*(size-i)
            P.append(temp+temp2)
    else:
        P = [[0 for x in range(size)] for y in range(size)] 
        L_max = []
        L_min = []
        for i in range(size):
            L_max.append(sys.float_info.min)
            L_min.append(sys.float_info.max)
            for j in range(size):
                if i != j :
                    L_max[i] = max(L_max[i],data[i][j])
                    L_min[i] = min(L_min[i],data[i][j])
        
        for i in range(size):
            for j in range(i+1):
                if i == j :
                    P[i][j] = 0.0
                else:
                    P[i][j] = float(L_max[i]-data[i][j])/float(L_max[i]-L_min[i])
    return P

# generate from random and P
def find_max_prop(city,P,data,check):
    max_value = 0
    des = []

    for i in range(city):
        if check[i] == 0:
            if max_value < P[city][i]:
                des = [i]
                max_value = P[city][i]
            elif max_value == P[city][i]:   
                des.append(i) 
    
    for i in range(city+1,len(P[city])):
        if check[i] == 0:
            if max_value < P[i][city]:
                des = [i]
                max_value = P[i][city]
            elif max_value == P[i][city]:   
                des.append(i)
    
    min_len = sys.float_info.max
    result = 0
    for i in des:
        if data[city][i] < min_len and i != city:
            result = i
    
    return result

def Generate(size,data,P):
    start_time = time.time()
    V = []
    check = [0]*size

    start = randint(0,size-1)
    V.append(start)
    check[start] = 1
    for i in range(size-1):
        b = randint(0,size-1)
        if check[b] == 1 or P[start][b]+P[b][start] < 0.9:
            check_inner = []
            for j in range(len(check)):
                if check[j] == 0:
                    check_inner.append(j)
            while (check[b] == 1 or P[start][b]+P[b][start] < 0.9) and len(check_inner) > 0:
                b = randint(0,size-1)
                if b in check_inner :
                    check_inner.remove(b)
            if len(check_inner) == 0:
                b = find_max_prop(start,P,data,check)
            check[b] = 1
            V.append(b)
            start = b
        else:
            V.append(b)
            check[b] = 1
            start = b
    # print("--- %s Generate seconds ---" % (time.time() - start_time))
    return V

def Tour_Length(tour,data):
    start = tour[0]
    length = 0
    for i in tour:
        length += data[start][i]
        start = i
    length += data[tour[0]][tour[len(tour)-1]]
    
    return length

def encode(vector):
    result = [0]*len(vector)
    prev = vector[0]
    for i in range(len(vector)):
        if i != 0:
            prev = vector[i-1]
            result[prev] = vector[i]        
        else:
            prev = vector[len(vector)-1]
            result[prev] = vector[i]
    return result

def Child(better,worse,data):
    better_e = encode(better)
    worse_e = encode(worse)
    size = len(better)
    check = [0]*size
    V = []
    start = randint(0,size-1)
    V.append(start)
    check[start] = 1
    for i in range(1,len(better_e)):
        choose = 0
        if data[start][better_e[start]] < data[start][worse_e[start]]:
            choose = better_e[start]
        else:
            choose = worse_e[start]
        
        if check[choose] == 1:
            while(check[choose] == 1):
                choose = randint(0,size-1)

        start = choose
        check[choose] = 1
        V.append(start)
    
    return V

def Update(P,better,worse,n,pop_size):
    start_time = time.time()
    better_e = encode(better)
    worse_e = encode(worse)
    for i in range(len(P)):
        for j in range(i+1):
            B1 = better_e[i]
            B2 = better_e[j]
            W1 = worse_e[i]
            W2 = worse_e[j]
            if (B1 == j or B2 == i) and (W1 != j and W2 != i) :
                P[i][j] += 1.0/(n*pop_size)
            elif (B1!= j and B2 != i) and (W1 == j or W2 == i) :
                P[i][j] -= 1.0/(n*pop_size)
            if P[i][j] > 1 :
                P[i][j] = 1
            elif P[i][j] < 0:
                P[i][j] = 0 
    # print("--- %s Update seconds ---" % (time.time() - start_time))
    return P




def TSP_Cga(size,data,pop_size,expect,limit,shared_pop,result,check,effort,compete):
    # for graph
    value = []

    start_time = time.time()
    P = initial(size,False,data)
    T_best = np.arange(0,size)
    F_best = sys.maxsize
    count = 0
    num_fitness = 0
    prev_recieve = []
    reverse = 3500
    while(True):

        Tours = []
        Scores = []
        idx_best = 0
        if effort.value <= reverse or (effort.value > reverse and effort.value <= compete.value):
            for idx ,n in enumerate(shared_pop):
                P[idx] = n
            prev_recieve = P
            Tours.append(Generate(size,data,P))
            Scores.append(Tour_Length(Tours[0],data))   

        if effort.value > reverse and effort.value > compete.value:
            print("-----reverse----")
            print(num_fitness)
            # reverse = reverse + 1000
            # reverse = randint(1500,4000)
            for idx ,n in enumerate(shared_pop):
                a = ([1]*idx)+([0]*(size-idx))
                P[idx] = list(np.array(a)-np.array(n))
            prev_recieve = P
            Tours.append(Generate(size,data,P))
            Scores.append(Tour_Length(Tours[0],data))  
            print(Tours)
            effort.value = 0 
            compete.value = 0

        # select from population
        for i in range(1,pop_size):
            Tours.append(Generate(size,data,P))
            Scores.append(Tour_Length(Tours[i],data))
            if Scores[i] < Scores[idx_best] :
                idx_best = i

        # update 
        pop_best_score = Scores[idx_best]
        pop_best = Tours[idx_best]
        for i in range(pop_size):
            V = Child(Tours[idx_best],Tours[i],data)
            score = Tour_Length(V,data)
            if pop_best_score < score:
                P = Update(P,pop_best,V,size,pop_size)
            else:
                pop_best_score = score
                pop_best = V
                P = Update(P,V,pop_best,size,pop_size)

        if pop_best_score < F_best:
            count = 0
            effort.value = 0
            F_best = pop_best_score
            T_best = pop_best
            print(pop_best_score)
            print(num_fitness)
            print(pop_best)
            print("--- %s TSP local min seconds ---" % (time.time() - start_time))

        else:
            P = Update(P,T_best,pop_best,size,pop_size)
            count += 1
            effort.value += 1
        value.append((expect*100)/F_best)
        num_fitness += 1

        # update shared_main_population
        if num_fitness%(10) == 0:
            constant = 1.0
            if effort.value < 500:
                constant = 0.1
            elif effort.value < 1000:
                constant = 0.5
            for idx,n in enumerate(shared_pop):
                n = list(np.array(n)- (constant*np.array(prev_recieve[idx])+np.array(P[idx])))

        if F_best == expect or count == limit or check.value == 1:
            # print(P)
            check.value = 1
            print("--- %s TSP seconds ---" % (time.time() - start_time))
            result['F_best'] = F_best
            result['T_best'] = T_best
            result['num_fitness'] = num_fitness
            # result['value'] = value
            return result

# data = []
# with open('fri26_d.txt', 'r') as csvfile:
# # with open('gr17_d.txt', 'r') as csvfile:
# # with open('P01_d.txt', 'r') as csvfile:
#     reader = csv.reader(csvfile)
#     for r in reader:
#         r = r[0].strip()
#         r = [float(x) for x in r.split()]
#         data.append(r)
# # data = [[0,36,32,54,20,40],[36,0,22,58,54,67],[32,22,0,36,42,71],[54,58,36,0,50,92],[20,54,42,50,0,45],[40,67,71,92,45,0]]
# pop_size = 16
# expect = 937
# limit = 1500
# result = [0,12,1,14,8,4,6,2,11,13,9,7,5,3,10]
# # print(Tour_Length(result,data))
# best_value = sys.maxsize
# best_array = []
# times_ = []
# time_ave = []
# ave = [0]*1500
# print(2085)

# for i in range(10):
#     best,path,values = TSP_Cga(26,data,pop_size,expect,limit)
#     print([best,path])
#     times = np.array(np.arange(len(values)))
#     if best_value > best:
#         best_value = best
#         best_array = values
#         times_ = times
#     temp = [x + y for x, y in zip(ave, values)]
#     if len(ave) < len(values):
#         temp = [ave[len(ave)-1]]*(len(values)-len(ave))
#         ave = list(ave) + list(temp)

#     elif len(ave) > len(values):
#         temp = [values[len(values)-1]]*(len(ave)-len(values))
#         values = list(values) + list(temp)

#     ave = [x + y for x, y in zip(ave, values)]
#     time_ave = np.array(np.arange(len(ave)))


#     # plt.plot(np.array(times),np.array(values), '-o')
#     # values = np.array(values)
#     # xnew = np.linspace(values.min(),values.max(),10) #300 represents number of points to make between T.min and T.max
#     # power_smooth = spline(values,times,xnew)
#     # plt.plot(xnew,power_smooth) 

# plt.plot(np.array(time_ave),np.array([x / (10.0) for x in ave]), '-o')
# plt.plot(np.array(times_),np.array(best_array), '-o')
# plt.show()

def cube(i):
    while 1:
        time.sleep(1)
        print(i.value)
        i.value = 1234
    return i

if __name__ == '__main__':
    m = mp.Manager()
    data = []
    # with open('fri26_d.txt', 'r') as csvfile:
    # with open('gr17_d.txt', 'r') as csvfile:
    # with open('11_d.txt', 'r') as csvfile:
    with open('17_city_1.txt', 'r') as csvfile:
    # with open('15_dd.txt', 'r') as csvfile:
    # with open('15_dd.txt', 'r') as csvfile:
    # with open('15_sd.txt', 'r') as csvfile:
    # with open('P01_d.txt', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for r in reader:
            r = r[0].strip()
            r = [float(x) for x in r.split()]
            data.append(r)

    pop_size = 8
    expect = 319
    limit = 200000
    result = [0,12,1,14,8,4,6,2,11,13,9,7,5,3,10]
    best_value = sys.maxsize
    best_array = []
    times_ = []
    time_ave = []
    ave = [0]*1500
    print("----------1---------")
    print(expect)
    cal_fitness = 0
    
    for i in range(10):
        result1 = m.dict()
        result2 = m.dict()
        check = m.Value('i',0)
        effort1 = m.Value('i',0)
        effort2 = m.Value('i',0)
        shared_pop = m.list()
        P = initial(len(data),False,data)
        for i in range(len(data)):
            shared_pop.append(P[i])
        processes = [mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result1,check,effort1,effort2)),mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result2,check,effort2,effort1))]
        [process.start() for process in processes]
        [process.join() for process in processes]
        print(result1)
        print(result2)
        cal_fitness = cal_fitness+ result1['num_fitness'] + result2['num_fitness']
##        cal_fitness = cal_fitness+ min(result1['num_fitness'],result2['num_fitness'])


    print(cal_fitness/10.0)

    # second
    print
    print("----------2---------")
    data = []
    with open('17_city_2.txt', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for r in reader:
            r = r[0].strip()
            r = [float(x) for x in r.split()]
            data.append(r)
    expect = 1376
    cal_fitness = 0
    for i in range(10):
        result1 = m.dict()
        result2 = m.dict()
        check = m.Value('i',0)
        effort1 = m.Value('i',0)
        effort2 = m.Value('i',0)
        shared_pop = m.list()
        P = initial(len(data),False,data)
        for i in range(len(data)):
            shared_pop.append(P[i])
        processes = [mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result1,check,effort1,effort2)),mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result2,check,effort2,effort1))]
        [process.start() for process in processes]
        [process.join() for process in processes]
        print(result1)
        print(result2)
        cal_fitness = cal_fitness+ result1['num_fitness'] + result2['num_fitness']
##        cal_fitness = cal_fitness+ min(result1['num_fitness'],result2['num_fitness'])
    print(cal_fitness/10.0)
    
##    # third
##    print
##    print("----------3---------")
##    data = []
##    with open('17_city_3.txt', 'r') as csvfile:
##        reader = csv.reader(csvfile)
##        for r in reader:
##            r = r[0].strip()
##            r = [float(x) for x in r.split()]
##            data.append(r)
##    expect = 1687
##    cal_fitness = 0
##    for i in range(10):
##        result1 = m.dict()
##        result2 = m.dict()
##        check = m.Value('i',0)
##        effort1 = m.Value('i',0)
##        effort2 = m.Value('i',0)
##        shared_pop = m.list()
##        P = initial(len(data),False,data)
##        for i in range(len(data)):
##            shared_pop.append(P[i])
##        processes = [mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result1,check,effort1,effort2)),mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result2,check,effort2,effort1))]
##        [process.start() for process in processes]
##        [process.join() for process in processes]
##        print(result1)
##        print(result2)
##        cal_fitness = cal_fitness+ result1['num_fitness'] + result2['num_fitness']
####        cal_fitness = cal_fitness+ min(result1['num_fitness'],result2['num_fitness'])
##    print(cal_fitness/10.0)
##
##    # fourth
##    print
##    print("----------4---------")
##    data = []
##    with open('17_city_4.txt', 'r') as csvfile:
##        reader = csv.reader(csvfile)
##        for r in reader:
##            r = r[0].strip()
##            r = [float(x) for x in r.split()]
##            data.append(r)
##    expect = 592
##    cal_fitness = 0
##    for i in range(10):
##        result1 = m.dict()
##        result2 = m.dict()
##        check = m.Value('i',0)
##        effort1 = m.Value('i',0)
##        effort2 = m.Value('i',0)
##        shared_pop = m.list()
##        P = initial(len(data),False,data)
##        for i in range(len(data)):
##            shared_pop.append(P[i])
##        processes = [mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result1,check,effort1,effort2)),mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result2,check,effort2,effort1))]
##        [process.start() for process in processes]
##        [process.join() for process in processes]
##        print(result1)
##        print(result2)
##        cal_fitness = cal_fitness+ result1['num_fitness'] + result2['num_fitness']
####        cal_fitness = cal_fitness+ min(result1['num_fitness'],result2['num_fitness'])
##    print(cal_fitness/10.0)
##
####    fifth
##    print
##    print("----------5---------")
##    data = []
##    with open('17_city_5.txt', 'r') as csvfile:
##        reader = csv.reader(csvfile)
##        for r in reader:
##            r = r[0].strip()
##            r = [float(x) for x in r.split()]
##            data.append(r)
##    expect = 2085
##    cal_fitness = 0
##    for i in range(10):
##        result1 = m.dict()
##        result2 = m.dict()
##        check = m.Value('i',0)
##        effort1 = m.Value('i',0)
##        effort2 = m.Value('i',0)
##        shared_pop = m.list()
##        P = initial(len(data),False,data)
##        for i in range(len(data)):
##            shared_pop.append(P[i])
##        processes = [mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result1,check,effort1,effort2)),mp.Process(target=TSP_Cga, args=(len(data),data,pop_size,expect,limit,shared_pop,result2,check,effort2,effort1))]
##        [process.start() for process in processes]
##        [process.join() for process in processes]
##        print(result1)
##        print(result2)
##        cal_fitness = cal_fitness+ result1['num_fitness'] + result2['num_fitness']
##        cal_fitness = cal_fitness+ min(result1['num_fitness'],result2['num_fitness'])
##    print(cal_fitness/10.0)
##
##
