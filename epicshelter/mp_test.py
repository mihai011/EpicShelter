from multiprocessing import Pool

def f(x):
    while True:
        x = x + 1

if __name__ == '__main__':
    p = Pool(12)
    print(p.map(f, [1, 2, 3,2,3,4,5,6]))