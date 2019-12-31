from fe.bench.workload import Workload
from fe.bench.workload import NewOrder
from fe.bench.workload import Payment
import time
import threading


class Session(threading.Thread):
    def __init__(self, wl: Workload):
        threading.Thread.__init__(self)
        self.workload = wl
        self.new_order_request = []
        self.payment_request = []
        self.payment_i = 0
        self.new_order_i = 0
        self.payment_ok = 0
        self.new_order_ok = 0
        self.time_new_order = 0
        self.time_payment = 0
        self.thread = None
        self.gen_procedure()

    def gen_procedure(self):
        for i in range(0, self.workload.procedure_per_session):
            new_order = self.workload.get_new_order()
            self.new_order_request.append(new_order)

    def run(self):
        self.run_gut()

    def run_gut(self):
        for new_order in self.new_order_request:
            before = time.time()
            ok, order_id = new_order.run()
            after = time.time()
            self.time_new_order = self.time_new_order + after - before  # 前后时间
            self.new_order_i = self.new_order_i + 1
            if ok: # 如果订单请求ok，则发送付款请求
                self.new_order_ok = self.new_order_ok + 1
                payment = Payment(new_order.buyer, order_id)
                self.payment_request.append(payment)
            if self.new_order_i % 100 or self.new_order_i == len(self.new_order_request):# d order_i不整除100 或 新的单数 不等于 新的单数请求
                self.workload.update_stat(self.new_order_i, self.payment_i, self.new_order_ok, self.payment_ok,
                                          self.time_new_order, self.time_payment)
                for payment in self.payment_request:
                    before = time.time()
                    ok = payment.run()
                    after = time.time()
                    self.time_payment = self.time_payment + after - before
                    self.payment_i = self.payment_i + 1
                    if ok:
                        self.payment_ok = self.payment_ok + 1
                self.payment_request = []
