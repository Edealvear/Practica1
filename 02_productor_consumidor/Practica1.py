from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


N = 10
K = 5
NPROD = 3
NCONS = 1

def delay(factor = 3):
    sleep(random()/factor)


def add_data(storage, index, value, mutex):
    mutex.acquire()
    try:
        storage[index.value] = value.value
        delay(6)
        index.value = index.value + 1
    finally:
        mutex.release()


# def get_data(storage, index, mutex):
#     mutex.acquire()
#     try:
#         data = storage[0]
#         index.value = index.value - 1
#         delay()
#         for i in range(index.value):
#             storage[i] = storage[i + 1]
#         storage[index.value] = -1
#     finally:
#         mutex.release()
#     return data

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
            

def producer(storage, index, empty, non_empty, mutex, value):
    for v in range(N):
        print (f"producer {current_process().name} produciendo")
        
        print(f"almacen de producer {current_process().name}: {[i for i in storage]}")
        delay(6)
        empty.acquire()
        value.value += randint(0,10)
        add_data(storage, index,
                 value, mutex)
        non_empty.release()
        print (f"producer {current_process().name} almacenado {v} producto")
    print(f"producer {current_process().name} HA TERMINADO DE PRODUCIR")
    add_data(storage , index, -1, mutex)



def consumer(storage, index, empty, non_empty, mutex, consum):
    for v in range(N):
        for nonempty in non_empty:
            nonempty.acquire()
        print (f"consumer {current_process().name} desalmacenando")
        (dato, i) = get_data(storage, index, mutex)
        print(dato)
        empty[i].release()
        consum[v] = dato
        print (f"consumer {current_process().name} consumiendo {dato} de producer {i}")
        print([j for j in consum])
        delay()

def main():
    consum=Array('i',NPROD * N)
    storages = [Array('i', K) for _ in range(NPROD)]
    index = [Value('i', 0)  for _ in range(NPROD)]
    for i in range(NPROD):
        for j in range(K):
            storages[i][j] = -2

    non_empty = [Semaphore(0) for _ in range(NPROD)]
    empty = [BoundedSemaphore(K) for _ in range(NPROD)]
    mutex = [Lock() for _ in range(NPROD)]

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storages[i], index[i], empty[i], non_empty[i], mutex[i], Value('i',0)))
                for i in range(NPROD) ]

    conslst = [ Process(target=consumer,
                      name=f"cons_{i}",
                      args=(storages, index, empty, non_empty, mutex, consum))
                for i in range(NCONS) ]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()


if __name__ == '__main__':
    main()

"""

Para el yo del futuro que intente leer este código
El problema que tiene es que se queda en un bucle en el que todos los procesos se quedan esperando algo, el consumidor no consume, los productores se quedan con todo el almacén lleno y no
sé por qué supongo que me falta hacer algún non_empty.release() 

Almacenan bien, parece que el consumidor consume bien, al menos lo hace en orden ,y los productores prodicen en orden

El problema es cuando los productores producen más de lo que consume el consumidor, cuando tienen los almacenes llenos el empty.acquire() bloquea la producción, lo que no entiendo es por que 
se bloquea la consumicion

"""