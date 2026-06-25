import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="发送消息到客户端")
parser.add_argument(
    "--msg_str",
    required=True,
    help='消息内容，如: "MSG,策略运行中|买入信号数：3"',
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.send_message(msg_str=args.msg_str),
)
print_output(data, args.output)
