from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


N = 5
K = 10
NPROD = 3
NCONS = 1

def delay(factor = 3):
    sleep(random()/factor)


def add_data(storage_prod, in_prod,  mutex_prod, n):
    mutex_prod.acquire()
    n += randint(0,10) 
    try:
        storage_prod[in_prod.value] = n
        delay(6)
        in_prod.value = in_prod.value + 1
    finally:
        mutex_prod.release()
        return n

def eliminardato(storage, indice, index):
        for i in range(index[indice].value):
            storage[indice][i] = storage[indice][i + 1]
        storage[index[indice].value] = -1

def get_data(storage, index, mutex):
    for mut in mutex:
        mut.acquire()
    try:
        indice =-1
        dato = -1
        for i in range(len(storage)):
            print(1)
            if storage[i][0] < dato or (dato < 0 and storage[i][0] >= 0):
                indice = i
                dato = storage[i][0]
        if (indice!=-1):
            eliminardato(storage, indice, index)
        else:
            pass 
        delay()
        
    finally:
       for mut in mutex:
           mut.release()
    return (dato, indice)


def producer(storage, index, empty, non_empty, mutex):
    for v in range(N):
        print (f"producer {current_process().name} produciendo")
        n=0
        delay(6)
        empty.acquire()
        n = add_data(storage, index, mutex, n)
        non_empty.release()
        print (f"producer {current_process().name} almacenado {n}")


def consumer(storage, index, empty, non_empty, mutex, consum):
    for v in range(N):
        for i in range(NPROD):
            non_empty[i].acquire()
        (dato, indice) = get_data(storage, index, mutex)
        empty[indice].release()
        consum.append(dato)
        delay()

def main():
    consum=[]
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
                        args=(storage[i], index[i], empty[i], non_empty[i], mutex[i]))
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
    print(consum)

if __name__ == '__main__':
    main()
