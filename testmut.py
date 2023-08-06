from multiprocessing import Process

def pt1():
    while True:
        print("am spongebob")

Process(target=pt1).start()
