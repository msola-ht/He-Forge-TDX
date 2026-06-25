import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取跟踪指数的ETF信息")
parser.add_argument(
    "--zs_code",
    required=True,
    help="指数代码，如: 950162.CSI；000300.CSI 在部分客户端样例下可能返回空结果",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_trackzs_etf_info(zs_code=args.zs_code),
)
print_output(data, args.output)
