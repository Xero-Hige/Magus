import os

from m_cores import tweets_fetcher

CORES = {
    "fectcher": tweets_fetcher.main
}


def main():
    pid = os.fork()
    if pid == 0:
        result = CORES["fectcher"]()
        exit(result)

    else:
        os.wait()

    print ("Ended")


if __name__ == '__main__':
    main()
