# -*- coding: utf-8 -*-
"""Copy of Geneticooo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OZOTwteni8bzpVUzzcT2KnVFW9yKY_Jp

Importowanie bibliotek
"""

import numpy as np
import matplotlib.pyplot as plt
import math
from numpy import arange
from numpy import meshgrid
import sympy as smp
import scipy
from scipy.misc import derivative
import jax.numpy as jnp
from jax import grad, jit, vmap, random
import datetime
from statistics import mean

"""Definica funkcji optymalizacji"""

def rastrigin(*X):
    A = 10
    n=len(X)
    f = A*n + sum([(x*x - A * jnp.cos(2 * math.pi * x)) for x in X])
    return f

def Rastrigin(X):
    A = 10
    n=len(X)
    f = A*n + sum([(x*x - A * jnp.cos(2 * math.pi * x)) for x in X])
    return f



def sphere(*X):
    return sum([(x*x) for x in X])

def Sphere(X):
    return sum([(x*x) for x in X])



def rosenbrock(*X):
   sum=0
   n=len(X)
   for i in range(n-1):
    sum=sum+(100.0*(X[i+1] - X[i]**2.0)**2.0 + ((1 - X[i])**2.0))
   return sum

def Rosenbrock(X):
   sum=0
   n=len(X)
   for i in range(n-1):
    sum=sum+(100.0*(X[i+1] - X[i]**2.0)**2.0 + ((1 - X[i])**2.0))
   return sum

def inicjalizacja(xn,K,L):
  sum_L=L*xn
  pop_gen_list = [np.random.randint(0, 2, sum_L) for i in range(K)]
  # print(pop)
  pop_gen = np.array(pop_gen_list)
  #[print(pop_gen_np[i,:])for i in range(K)]

  return pop_gen,pop_gen_list

def bin2dec(pop_gen,L,xn):
  dec=[0]*xn
  for j in range(xn):
    for i in range(L):
      dec[j] = dec[j]+pop_gen[i+(j-1)*L]*2**i 
    #print(dec)

  return dec

def fenotyp(pop_gen,xn,K,L,F_min,F_max):

  pop_fen=[bin2dec(pop_gen[i,:],L,xn) for i in range(K)]
  pop_fen_np= np.array(pop_fen)
  pop_fen_float=F_min+((F_max-F_min)/((2**L)-1))*pop_fen_np
  return pop_fen_float

def tournament_selection(pop_adapt,pop_gen,K):
  index123=[i for i in range(K)]
  index_alfa=[0 for i in range(K)]

  np.random.shuffle(index123)
  index11=index123[0:int(K/2)]
  index21=index123[int(K/2):K]
  
  np.random.shuffle(index123)
  index12=index123[0:int(K/2)]
  index22=index123[int(K/2):K]

  index1=index11+index12
  index2=index21+index22

  for i in range(K):
    if pop_adapt[index1[i]]<pop_adapt[index2[i]]:
      index_alfa[i]=index1[i]
    else:
      index_alfa[i]=index2[i]

  new_pop_gen_list=[[0]*L*xn for i in range(K)]

  for i in range(K):
      new_pop_gen_list[i]=pop_gen[index_alfa[i]]

  return new_pop_gen_list

def crossing(parents_gen_list,xn,L,K):
  children = [[0]*L*xn for i in range(K)]

  for j in range(int(K/2)):
    child1=[]
    child2=[]
    if pc>(np.random.uniform(0,1)):
      cpoint=[np.random.randint(1,L) for i in range(xn)]

      for i in range(xn):

        child1.extend(parents_gen_list[j*2][L*i:L*i+cpoint[i]])
        child1.extend(parents_gen_list[1+j*2][L*i+cpoint[i]:L*(i+1)])
        child2.extend(parents_gen_list[1+j*2][L*i:L*i+cpoint[i]])
        child2.extend(parents_gen_list[j*2][L*i+cpoint[i]:L*(i+1)])

      children[j*2]=child1
      children[1+j*2]=child2
    else:
      children[j*2]=parents_gen_list[j*2]
      children[1+j*2]=parents_gen_list[1+j*2]
      
    
  children_np = np.array(children)
  return children_np,children

def mutation(pop_gen_list,pm,K,L,xn):
  for i in range(K):
    for j in range(L*xn):
      if pm>(np.random.uniform(0,1)):
        # print('mutacja')
        # print(pop_gen_list[i][j])
        pop_gen_list[i][j]=abs(pop_gen_list[i][j]-1)
        # print(pop_gen_list[i][j])
  pop_gen=np.array(pop_gen_list)
  return pop_gen,pop_gen_list

def elityzm (pop_gen,pop_adapt,pop_gen_list,pop_adapt_min_p,best_pop_gen_p):
  index_best=pop_adapt.index(min(pop_adapt))
  index_worst=pop_adapt.index(max(pop_adapt))

  pop_adapt_min=(min(pop_adapt))
  if pop_adapt_min>pop_adapt_min_p:
    pop_gen_list[index_worst]=best_pop_gen_p
    pop_gen=np.array(pop_gen_list)
    return pop_gen,pop_gen_list,best_pop_gen_p,pop_adapt_min_p

  else:
    pop_adapt_min_p=pop_adapt_min
    best_pop_gen_p=pop_gen_list[pop_adapt.index(min(pop_adapt))]
  

    return pop_gen,pop_gen_list,best_pop_gen_p,pop_adapt_min_p

def algorytm_genetyczny(Funckja,xn,K,L,F_min,F_max,pc,epoch,precision,stop_cndition):

  Tstart = datetime.datetime.now()

  counter=0
  pop_adapt_min_p=100

  pop_gen,pop_gen_list=inicjalizacja(xn,K,L) # inicjalizacja genotypu
  pop_fen=fenotyp(pop_gen,xn,K,L,F_min,F_max) # obliczanie fenotypu
  pop_adapt=[Funckja(pop_fen[i,:]) for i in range(K)] # liczenie przystosowania
  #print(pop_adapt)
  pop_adapt_min_pp=(min(pop_adapt))
  best_pop_gen_pp=pop_gen[pop_adapt.index(min(pop_adapt))]


  for e in range(epoch):
    #print('Epoka',e)
    parents_gen_list=tournament_selection(pop_adapt,pop_gen,K) # Selekcja populacji
    pop_gen,pop_gen_list=crossing(parents_gen_list,xn,L,K) #krzyżowanie
    pop_gen,pop_gen_list=mutation(pop_gen_list,pm,K,L,xn) #mutacja
    pop_fen=fenotyp(pop_gen,xn,K,L,F_min,F_max) # obliczanie fenotypu
    #print('obecne pop_fen',pop_fen)
    pop_adapt=[Funckja(pop_fen[i,:]) for i in range(K)] # liczenie przystosowania
    pop_gen,pop_gen_list,best_pop_gen_pp,pop_adapt_min_pp=elityzm(pop_gen,pop_adapt,pop_gen_list,pop_adapt_min_pp,best_pop_gen_pp) # elityzm
    pop_fen=fenotyp(pop_gen,xn,K,L,F_min,F_max) # obliczanie fenotypu
    pop_adapt=[Funckja(pop_fen[i,:]) for i in range(K)] # liczenie przystosowania
    #print('obecne pop_adapt',pop_adapt)
  
    #pop_adapt_mean = mean(pop_adapt)
    pop_adapt_min=min(pop_adapt)
    
    #print(pop_adapt_min_p-pop_adapt_min)
    if abs(pop_adapt_min_p-pop_adapt_min)<precision:
      counter=counter+1
      #print('Brak zmiany najlepiej przystosowanego osobnika')
      if counter>=stop_cndition:
        #print('Algorytm zatrzymany z powodu ujednolicenia populacji')
        Tstop = datetime.datetime.now()
        Total_time = (Tstop.hour*3600+Tstop.minute*60+Tstop.second)-(Tstart.hour*3600+Tstart.minute*60+Tstart.second)
        print('Finalny pop_adapt',pop_adapt)
        return Total_time,pop_fen[pop_adapt.index(min(pop_adapt))]
    else:
      counter=0

    pop_adapt_min_p=pop_adapt_min

  Tstop = datetime.datetime.now()
  Total_time = (Tstop.hour*3600+Tstop.minute*60+Tstop.second)-(Tstart.hour*3600+Tstart.minute*60+Tstart.second)
  print('Finalny pop_adapt',pop_adapt)
  return Total_time,pop_fen[pop_adapt.index(min(pop_adapt))]

"""**PĘTLA GŁÓWNA**

"""

#Parametry
K=8*2 # liczba chromosomów w populacji ( wielkość populajci)
L=15 # długość wektora binarnego 
F_min=-3 # dolne ograniczenie przestrzeni decyzyjnej
F_max=3 # górne ograniczenie przestrzeni decyzyjnej
pc=0.95 # prawdopodobieństwo krzyżowania
pm=0.005 # prawdopodobieństwo mutacji

#Warunki stopu
epoch=200 # Liczba epok
precision=0.001 # 
stop_cndition=15 # liczba epok do zatrzymania po braku zmian

czas_1_total = [[0]*5 for i in range(11)] #inicjalizacja tablic
czas_2_total = [[0]*5 for i in range(11)]
czas_3_total = [[0]*5 for i in range(11)]
best_1 = [[0] for i in range(11)]
mean_1 = [[0] for i in range(11)]
best_x1 = [[0] for i in range(11)]
best_2 = [[0] for i in range(11)]
mean_2 = [[0] for i in range(11)]
best_x2 = [[0] for i in range(11)]
best_3 = [[0] for i in range(11)]
mean_3 = [[0] for i in range(11)]
best_x3 = [[0] for i in range(11)]

for xi in range(11):
  xn=2**(xi+1) #liczba zmiennych decyzyjnych
  f1_celu = [] #inicjalizacja tablic
  f2_celu = []
  f3_celu = []
  print('Liczba zmiennych dezycyjnych',xn)
  print('\n')
  #print(xi) 
  temp_suma=0
  
  for i in range(5):
    start_x = np.random.uniform(0,1,xn) #inicjalizacja początkowych wartości zmiennych decyzyjnych
    czas_1 = 0
    czas_2 = 0
    czas_3 = 0

    x_1 = 0
    x_2 = 0
    x_3 = 0


    czas_1_total[xi][i],x_1=algorytm_genetyczny(Rastrigin,xn,K,L,F_min,F_max,pc,epoch,precision,stop_cndition)
    czas_2_total[xi][i],x_2=algorytm_genetyczny(Sphere,xn,K,L,F_min,F_max,pc,epoch,precision,stop_cndition)
    czas_3_total[xi][i],x_3=algorytm_genetyczny(Rosenbrock,xn,K,L,F_min,F_max,pc,epoch,precision,stop_cndition)

    if i<1:
      all_x1 = x_1
      all_x2 = x_2
      all_x3 = x_3
    else:
      all_x1 = np.vstack((all_x1, x_1)) #generowanie wektora wartości
      all_x2 = np.vstack((all_x2, x_2))
      all_x3 = np.vstack((all_x3, x_3))

    f1_celu.append(Rastrigin(x_1)) #generowanie listy wartości funkcji celu
    f2_celu.append(Sphere(x_2))
    f3_celu.append(Rosenbrock(x_3))
  best_1[xi] = min(f1_celu) #najlepsza wartosc funkcji celu
  mean_1[xi] = mean(np.array(f1_celu)) #średnia wartość funckji celu
  best_x1[xi] = all_x1[f1_celu.index(best_1[xi]),:] #zwracanie najlepszych wartości zmiennych decyzyjnych

  best_2[xi] = min(f2_celu)
  mean_2[xi] = mean(np.array(f2_celu))
  best_x2[xi] = all_x2[f2_celu.index(best_2[xi]),:]

  best_3[xi] = min(f3_celu)
  mean_3[xi] = mean(np.array(f3_celu))
  best_x3[xi] = all_x3[f3_celu.index(best_3[xi]),:]

"""**Wyświetlanie wyników**"""

srednia_czas_1=[[0] for i in range(11)]
srednia_czas_2=[[0] for i in range(11)]
srednia_czas_3=[[0] for i in range(11)]
for j in range(11):
  temp_suma_1=0
  temp_suma_2=0
  temp_suma_3=0
  for i in range(5):
    temp_suma_1=temp_suma_1+czas_1_total[j][i]
    temp_suma_2=temp_suma_2+czas_2_total[j][i]
    temp_suma_3=temp_suma_3+czas_3_total[j][i]
  srednia_czas_1[j]=temp_suma_1/5
  srednia_czas_2[j]=temp_suma_2/5
  srednia_czas_3[j]=temp_suma_3/5
#print(srednia_czas_1)
#print(srednia_czas_2)
#print(srednia_czas_3)

hist1 = best_x1[10]
hist2 = best_x2[10]
hist3 = best_x3[10]

os_x=[[2**(i+1)] for i in range(11)]
plt.plot(os_x,srednia_czas_1)
plt.ylabel('Czas wykonywania algorytmu')
plt.xlabel('liczba zmiennych')
plt.title('Czas wykonywania algorytmu od\nzmiennych decyzyjnych dla funkcji Rastrigin')
plt.grid()
plt.show()

plt.plot(os_x,srednia_czas_2)
plt.ylabel('Czas wykonywania algorytmu')
plt.xlabel('liczba zmiennych')
plt.title('Czas wykonywania algorytmu od\nzmiennych decyzyjnych dla funkcji Shpere')
plt.grid()
plt.show()

plt.plot(os_x,srednia_czas_3)
plt.ylabel('Czas wykonywania algorytmu')
plt.xlabel('liczba zmiennych')
plt.title('Czas wykonywania algorytmu od\nzmiennych decyzyjnych dla funkcji Rosenbrock')
plt.grid()
plt.show()

plt.plot(os_x,best_1)
plt.ylabel('Wartość funkcji celu')
plt.xlabel('liczba zmiennych')
plt.title('Najlepsza wart. f. celu od liczby\nzm. decyzyjnych (Rastrigin)')
plt.grid()
plt.show()
plt.plot(os_x,best_2)
plt.ylabel('Wartość funkcji celu')
plt.xlabel('liczba zmiennych')
plt.title('Najlepsza wart. f. celu od liczby\nzm. decyzyjnych (Shpere)')
plt.grid()
plt.show()
plt.plot(os_x,best_3)
plt.ylabel('Wartość funkcji celu')
plt.xlabel('liczba zmiennych')
plt.title('Najlepsza wart. f. celu od liczby\nzm. decyzyjnych (Rosenbrock)')
plt.grid()
plt.show()

plt.plot(os_x,mean_1)
plt.ylabel('Wartość funkcji celu')
plt.xlabel('liczba zmiennych')
plt.title('Średnia wart. f. celu od liczby\nzm. decyzyjnych (Rastrigin)')
plt.grid()
plt.show()
plt.plot(os_x,mean_2)
plt.ylabel('Wartość funkcji celu')
plt.xlabel('liczba zmiennych')
plt.title('Średnia wart. f. celu od liczby\nzm. decyzyjnych (Shpere)')
plt.grid()
plt.show()
plt.plot(os_x,mean_3)
plt.ylabel('Wartość funkcji celu')
plt.xlabel('liczba zmiennych')
plt.title('Średnia wart. f. celu od liczby\nzm. decyzyjnych (Rosenbrock)')
plt.grid()
plt.show()

plt.hist(hist1)
plt.ylabel('Liczba zmiennych decyzyjnych')
plt.xlabel('Wartość zmiennej decyzyjnej')
plt.title('Rozkład wart. najlepszych zmiennych\ndec. dla 2048 zmiennych (Rastrigin)')
plt.show()
plt.hist(hist2)
plt.ylabel('Liczba zmiennych decyzyjnych')
plt.xlabel('Wartość zmiennej decyzyjnej')
plt.title('Rozkład wart. najlepszych zmiennych\ndec. dla 2048 zmiennych (Sphere)')
plt.show()
plt.hist(hist3)
plt.ylabel('Liczba zmiennych decyzyjnych')
plt.xlabel('Wartość zmiennej decyzyjnej')
plt.title('Rozkład wart. najlepszych zmiennych\ndec. dla 2048 zmiennych (Rosenbrock)')
plt.show()

rate = 0.01
beta1 = 0.9
beta2 = 0.99
max_iters = 10000

xn=2 # liczba zmiennych
K=8*2 # liczba chromosomów w populacji ( wielkość populajci)
L=15 # długość wektora binarnego 
F_min=-3 # dolne ograniczenie przestrzeni decyzyjnej
F_max=3 # górne ograniczenie przestrzeni decyzyjnej
pc=0.9 # prawdopodobieństwo krzyżowania
pm=0.05 # prawdopodobieństwo mutacji
epoch=200 # Liczba epok
precision=0.001 # 
stop_cndition=5 # liczba epok do zatrzymania po braku zmian

Total_time,pop_fen=algorytm_genetyczny(Rastrigin,xn,K,L,F_min,F_max,pc,epoch,precision,stop_cndition)
print(Total_time,pop_fen)

def algorytm_genetyczny_rysuj(funkcja,Funckja,xn,K,L,F_min,F_max,pc,epoch,precision,stop_cndition):

  Tstart = datetime.datetime.now()

  counter=0
  pop_adapt_min_p=100

  pop_gen,pop_gen_list=inicjalizacja(xn,K,L) # inicjalizacja genotypu
  pop_fen=fenotyp(pop_gen,xn,K,L,F_min,F_max) # obliczanie fenotypu
  pop_adapt=[Funckja(pop_fen[i,:]) for i in range(K)] # liczenie przystosowania
  print(pop_adapt)
  pop_adapt_min_pp=(min(pop_adapt))
  best_pop_gen_pp=pop_gen[pop_adapt.index(min(pop_adapt))]

  X = np.linspace(F_min, F_max, 200)    
  Y = np.linspace(F_min, F_max, 200)    

  X, Y = np.meshgrid(X, Y)

  Z = funkcja(X, Y)
  Z = np.array(Z)
  Z = Z.reshape((len(X), len(Y)))

  plt.contour(X,Y,Z, 10)

  for e in range(epoch):
    print('Epoka',e)
    plt.scatter(pop_fen[pop_adapt.index(min(pop_adapt))][0], pop_fen[pop_adapt.index(min(pop_adapt))][1])
    parents_gen_list=tournament_selection(pop_adapt,pop_gen,K) # Selekcja populacji
    pop_gen,pop_gen_list=crossing(parents_gen_list,xn,L,K) #krzyżowanie
    pop_gen,pop_gen_list=mutation(pop_gen_list,pm,K,L,xn) #mutacja
    pop_fen=fenotyp(pop_gen,xn,K,L,F_min,F_max) # obliczanie fenotypu
    print('obecne pop_fen',pop_fen)
    pop_adapt=[Funckja(pop_fen[i,:]) for i in range(K)] # liczenie przystosowania
    pop_gen,pop_gen_list,best_pop_gen_pp,pop_adapt_min_pp=elityzm(pop_gen,pop_adapt,pop_gen_list,pop_adapt_min_pp,best_pop_gen_pp) # elityzm
    pop_fen=fenotyp(pop_gen,xn,K,L,F_min,F_max) # obliczanie fenotypu
    pop_adapt=[Funckja(pop_fen[i,:]) for i in range(K)] # liczenie przystosowania
    print('obecne pop_adapt',pop_adapt)
  
    #pop_adapt_mean = mean(pop_adapt)
    pop_adapt_min=min(pop_adapt)
    
    print(pop_adapt_min_p-pop_adapt_min)
    if abs(pop_adapt_min_p-pop_adapt_min)<precision:
      counter=counter+1
      print('Brak zmiany najlepiej przystosowanego osobnika')
      if counter>=stop_cndition:
        print('Algorytm zatrzymany z powodu ujednolicenia populacji')
        Tstop = datetime.datetime.now()
        Total_time = (Tstop.hour*3600+Tstop.minute*60+Tstop.second)-(Tstart.hour*3600+Tstart.minute*60+Tstart.second)
        return Total_time,pop_fen[pop_adapt.index(min(pop_adapt))]
    else:
      counter=0

    pop_adapt_min_p=pop_adapt_min

  Tstop = datetime.datetime.now()
  Total_time = (Tstop.hour*3600+Tstop.minute*60+Tstop.second)-(Tstart.hour*3600+Tstart.minute*60+Tstart.second)
  plt.scatter(pop_fen[pop_adapt.index(min(pop_adapt))][0], pop_fen[pop_adapt.index(min(pop_adapt))][1])
  return Total_time,pop_fen[pop_adapt.index(min(pop_adapt))]

xn=2 # liczba zmiennych
K=8*2 # liczba chromosomów w populacji ( wielkość populajci)
L=15 # długość wektora binarnego 
F_min=-3 # dolne ograniczenie przestrzeni decyzyjnej
F_max=3 # górne ograniczenie przestrzeni decyzyjnej
pc=0.9 # prawdopodobieństwo krzyżowania
pm=0.05 # prawdopodobieństwo mutacji
epoch=200 # Liczba epok
precision=0.001 # 
stop_cndition=5 # liczba epok do zatrzymania po braku zmian

Total_time,pop_fen=algorytm_genetyczny_rysuj(rosenbrock,Rosenbrock,xn,K,L,F_min,F_max,pc,epoch,precision,stop_cndition)
print(Total_time,pop_fen)

xD=Rosenbrock(x_2)
print(xD)