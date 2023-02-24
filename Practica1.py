from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


N = 10 #Num productos
K = 5 #tamano almacen
NPROD = 3 #numpero productores
NCONS = 1 #numero consumidores
NumCons = NPROD * N #numero de consumiciones que hacen los consumidores

def delay(factor = 3):
    sleep(random()/factor)


def add_data(storage_prod, in_prod,  mutex_prod, n):
    mutex_prod.acquire()
    try:
        storage_prod[in_prod.value] = n.value
        delay(6)
        in_prod.value = in_prod.value + 1
    finally:
        mutex_prod.release()

# def eliminardato(storage, indice, index):
#         index[indice].value -= 1
#         for i in range(index[indice].value):
#             storage[indice][i] = storage[indice][i + 1]
#         storage[indice][index[indice].value] = -2

# def get_data(storage, index, mutex):
#     for mut in mutex:
#         mut.acquire()
#     try:
#         indice =-1
#         dato = -1
#         for i in range(len(storage)):
#             print([j for j in storage[i]])
#             if (storage[i][0] < dato and storage[i][0]>=0) or (dato < 0 and storage[i][0] >= 0):
#                 indice = i
#                 dato = storage[i][0]
#         if (indice!=-1):
#             eliminardato(storage, indice, index)
#         else:
#             pass 
#         delay()
        
#     finally:
#        for mut in mutex:
#            mut.release()
#     return (dato, indice)

def elim_data(storage, index):
    index.value -= 1
    for i in range(index.value):
        storage[i] = storage[i+1]
    storage[index.value] = -2
    print([i for i in storage])


def get_data(storages, index, mutex):
    for mut in mutex:
        mut.acquire()
    ind = -1
    data = -1
    try:
        for i in range(len(storages)):
            if (data>0) and (storages[i][0]< data):
                data = storages[i][0]
                ind = i
            elif (storages[i][0] > data) and (data < 0):
                data = storages[i][0]
                ind = i 
        delay()
        elim_data(storages[ind], index[ind])
    finally:
        for mut in mutex:
            mut.release()
        return (data, ind)

def producer(storage, index, valor,empty, non_empty, mutex):
    for v in range(N):
        print (f"producer {current_process().name} produciendo")
        delay(6)
        valor.value += randint(0,10)
        empty.acquire()
        add_data(storage, index, mutex, valor)
        non_empty.release()
        print (f"producer {current_process().name} almacenado {valor.value}")


def consumer(storage, index, empty, non_empty, mutex, consum):
    for v in range(NumCons):
        for i in range(NPROD):
            non_empty[i].acquire()
        (dato, indice) = get_data(storage, index, mutex)
        empty[indice].release()
        print(dato)
        consum[v]=dato
        delay()

def main():
    consum=Array('i',NumCons)
    storage = [Array('i', K) for _ in range(NPROD)]
    index = [Value('i', 0)  for _ in range(NPROD)]
    for i in range(NPROD):
        for j in range(K):
            storage[i][j] = -2

    non_empty = [Semaphore(0) for _ in range(NPROD)]
    empty = [BoundedSemaphore(K) for _ in range(NPROD)]
    mutex = [Lock() for _ in range(NPROD)]

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage[i], index[i], Value('i',0),empty[i],  non_empty[i], mutex[i]))
                for i in range(NPROD) ]

    cons = Process(target=consumer,
                      name="Consumidor",
                      args=(storage, index, empty, non_empty, mutex, consum))

    for p in prodlst:
        p.start()
    cons.start()
    for p in prodlst:
        p.join()
    cons.join()
    print([i for i in consum])

if __name__ == '__main__':
    main()
