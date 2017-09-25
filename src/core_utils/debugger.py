from sys import stdout


def debug_core_print_d(worker_name, worker_number, message):
    print("[{}::{}] Debug: {}".format(worker_name, worker_number, message))
    stdout.flush()
