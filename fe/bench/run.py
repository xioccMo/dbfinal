from fe.bench.workload import Workload
from fe.bench.session import Session


def run_bench():
    wl = Workload() # 初始workload对象
    wl.gen_database() # 生成一系列数据

    sessions = [] # 生成一系列的session
    for i in range(0, wl.session):
        ss = Session(wl)
        sessions.append(ss)

    for ss in sessions:
        ss.start() # 启动线程

    for ss in sessions:
        ss.join()


if __name__ == "__main__":
   run_bench()