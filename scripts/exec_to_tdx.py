import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="调用通达信客户端功能或URL")
parser.add_argument(
    "--url",
    required=True,
    help="客户端功能或URL，如: http://www.treeid/MAINQH 或 http://www.treeid/dlghttp://www.tdx.com.cn",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.exec_to_tdx(url=args.url),
)
print_output(data, args.output)
