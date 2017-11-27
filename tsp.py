from random import *
import numpy as np
##import matplotlib.pyplot as plt
##from scipy.interpolate import spline
import sys
import csv
import time
# initial matrix
def initial(size,method,data):
    P = []
    if method:
        for i in range(size):
            temp = [1.0/size]*i
            temp2 = [0.0]*(size-i)
            P.append(temp+temp2)
    else:
        P = [[0 for x in range(size)] for y in range(size)] 
        L_max = []
        L_min = []
        for i in range(size):
            L_max.append(0)
##            L_min.append(sys.float_info.max)
            for j in range(size):
                if i != j :
                    L_max[i] = L_max[i]+data[i][j]
##                    L_min[i] = min(L_min[i],data[i][j])
        
        for i in range(size):
            for j in range(size):
                if i == j :
                    P[i][j] = 0.0
                else:
                    P[i][j] = 1 - (float(data[i][j])/float(L_max[i]))

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
        if check[b] == 1 or P[start][b]+P[b][start] < 0.5:
            check_inner = []
            for j in range(len(check)):
                if check[j] == 0:
                    check_inner.append(j)
            while (check[b] == 1 or P[start][b]+P[b][start] < 0.5) and len(check_inner) > 0:
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
                P[i][j] -= 1.0/(n)
            if P[i][j] > 0.099995 :
                P[i][j] = 0.099995
            elif P[i][j] < 0.000005:
                P[i][j] = 0.000005 
    # print("--- %s Update seconds ---" % (time.time() - start_time))
    return P




def TSP_Cga(size,data,pop_size,expect,limit):
    # for graph
    value = []

    start_time = time.time()
    P = initial(size,False,data)
    # T_best = np.arange(0,size)
    # shuffle(T_best)
    # F_best = Tour_Length(T_best,data)
    T_best = np.arange(0,size)
    F_best = sys.maxsize
    count = 0
    num_fitness = 0
    while(True):
        Tours = []
        Scores = []
        Tours.append(Generate(size,data,P))
        Scores.append(Tour_Length(Tours[0],data))
        idx_best = 0

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
                            # if Scores[idx_best] < Scores[i]:
            #     P = Update(P,Tours[idx_best],Tours[i],pop_size)

        # V = Child(pop_best,T_best,data)
        # score = Tour_Length(V,data)
        # if score < F_best:
        #     # P = Update(P,V,T_best,pop_size)
        #     count = 0
        #     F_best = score
        #     T_best = V

        # else:
        #     P = Update(P,T_best,V,pop_size)
        #     count += 1
        if pop_best_score < F_best:
            count = 0
            F_best = pop_best_score
            T_best = pop_best
            print(pop_best_score)
            print(T_best)
            print(num_fitness)
            print("--- %s TSP local min seconds ---" % (time.time() - start_time))

        else:
            P = Update(P,T_best,pop_best,size,pop_size)
            count += 1
        num_fitness += 1
        value.append((expect*100)/F_best)


        if F_best == expect or count == limit:
            print("--- %s TSP seconds ---" % (time.time() - start_time))
            return F_best,T_best,value,num_fitness

data = []
# with open('fri26_d.txt', 'r') as csvfile:
# with open('gr17_d.txt', 'r') as csvfile:
# with open('11_d.txt', 'r') as csvfile:
with open('11_city_1.txt', 'r') as csvfile:
# with open('15_dd.txt', 'r') as csvfile:
# with open('15_sd.txt', 'r') as csvfile:
# with open('P01_d.txt', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for r in reader:
        r = r[0].strip()
        r = [float(x) for x in r.split()]
        data.append(r)
# data = [[0,36,32,54,20,40],[36,0,22,58,54,67],[32,22,0,36,42,71],[54,58,36,0,50,92],[20,54,42,50,0,45],[40,67,71,92,45,0]]
pop_size = 8
expect = 263
limit = 500000
result = [0,12,1,14,8,4,6,2,11,13,9,7,5,3,10]
# print(Tour_Length(result,data))
best_value = sys.maxsize
best_array = []
times_ = []
time_ave = []
ave = [0]*1500
print("-----------1-----------")
print(expect)

cal_fitness = 0

# for test
ave_length = 0
best_length = sys.maxsize

for i in range(10):
    best,path,values,num_fitness = TSP_Cga(len(data),data,pop_size,expect,limit)
    print([best,path,num_fitness])
    cal_fitness = cal_fitness + num_fitness
    # times = np.array(np.arange(len(values)))
    # if best_value > best:
    #     best_value = best
    #     best_array = values
    #     times_ = times
    # temp = [x + y for x, y in zip(ave, values)]
    # if len(ave) < len(values):
    #     temp = [ave[len(ave)-1]]*(len(values)-len(ave))
    #     ave = list(ave) + list(temp)

    # elif len(ave) > len(values):
    #     temp = [values[len(values)-1]]*(len(ave)-len(values))
    #     values = list(values) + list(temp)

    # ave = [x + y for x, y in zip(ave, values)]
    # time_ave = np.array(np.arange(len(ave)))


    # plt.plot(np.array(times),np.array(values), '-o')
    # values = np.array(values)
    # xnew = np.linspace(values.min(),values.max(),10) #300 represents number of points to make between T.min and T.max
    # power_smooth = spline(values,times,xnew)
    # plt.plot(xnew,power_smooth) 

#plt.plot(np.array(time_ave),np.array([x / (10.0) for x in ave]), '-o')
#plt.plot(np.array(times_),np.array(best_array), '-o')
#plt.show()

print(cal_fitness/10.0)

# second dataset
print
print("-----------2-----------")
data = []
expect = 548
print(expect)
cal_fitness = 0
with open('11_city_2.txt', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for r in reader:
        r = r[0].strip()
        r = [float(x) for x in r.split()]
        data.append(r)

for i in range(10):
    best,path,values,num_fitness = TSP_Cga(len(data),data,pop_size,expect,limit)
    print([best,path,num_fitness])
    cal_fitness = cal_fitness + num_fitness

print(cal_fitness/10.0)

# third dataset
print
print("-----------3-----------")
data = []
expect = 419
print(expect)
cal_fitness = 0
with open('11_city_3.txt', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for r in reader:
        r = r[0].strip()
        r = [float(x) for x in r.split()]
        data.append(r)

for i in range(10):
    best,path,values,num_fitness = TSP_Cga(len(data),data,pop_size,expect,limit)
    print([best,path,num_fitness])
    cal_fitness = cal_fitness + num_fitness

print(cal_fitness/10.0)

# fourth dataset
print
print("-----------4-----------")
data = []
expect = 402
print(expect)
cal_fitness = 0
with open('11_city_4.txt', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for r in reader:
        r = r[0].strip()
        r = [float(x) for x in r.split()]
        data.append(r)

for i in range(10):
    best,path,values,num_fitness = TSP_Cga(len(data),data,pop_size,expect,limit)
    print([best,path,num_fitness])
    cal_fitness = cal_fitness + num_fitness

print(cal_fitness/10.0)

# fifth dataset
print
print("-----------5-----------")
data = []
expect = 253
print(expect)
cal_fitness = 0
with open('11_city_5.txt', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for r in reader:
        r = r[0].strip()
        r = [float(x) for x in r.split()]
        data.append(r)

for i in range(10):
    best,path,values,num_fitness = TSP_Cga(len(data),data,pop_size,expect,limit)
    print([best,path,num_fitness])
    cal_fitness = cal_fitness + num_fitness

print(cal_fitness/10.0)
