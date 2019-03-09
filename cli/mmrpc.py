#! /usr/bin/env python

from concurrent import futures
import json
import multiprocessing
import signal
import sys
import time

import grpc
import mmbot as mmb

import mmbot_pb2
import mmbot_pb2_grpc


class MmbotServicer(mmbot_pb2_grpc.MmbotServicer):
    def __init__(self):
        self.mmb = mmb.MaliciousMacroBot()
        self.mmb.mmb_init_model()

    def SendVba(self, request, context):
        response = mmbot_pb2.Prediction()
        pred = self.mmb.mmb_predict(request.vba, datatype='vba')
        response.prediction = json.dumps(self.mmb.mmb_prediction_to_json(pred)[0])
        return response


RUN = 1


def main():
    def handler(sig, frame):
        global RUN
        RUN = 0

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    parser = argparse.ArgumentParser(prog='mmrpc.py',
                                     description='runs Mmbot RPC server',
                                     usage='%(prog)s [options]')
    parser.add_argument('-a', '--address',
                        action='store',
                        dest='address',)
    parser.add_argument('-t', '--threads',
                        action='store',
                        dest='threads',)
    parser.add_argument('-r', '--rpcs',
                        action='store',
                        dest='rpcs',)
    args = parser.parse_args()

    if not args.address:
        sys.exit('no address provided')
    adddress = args.address
    threads = args.threads or multiprocessing.cpu_count() * 2
    rpcs = args.rpcs or None

    executor = futures.ThreadPoolExecutor(max_workers=threads)
    server = grpc.server(executor,
                         maximum_concurrent_rpcs=rpcs)
    mmbot_pb2_grpc.add_MmbotServicer_to_server(MmbotServicer(), server)
    server.add_insecure_port(address)
    server.start()
    while RUN:
        time.sleep(5)
    stop = server.stop(5)
    stop.wait()


if __name__ == '__main__':
    main()
