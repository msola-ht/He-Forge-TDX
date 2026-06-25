import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="发送文件到客户端展示")
parser.add_argument(
    "--file_path",
    required=True,
    help="文件名或相对路径，文件需位于通达信 PYPlugins/file 目录",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.send_file(file_path=args.file_path),
)
print_output(data, args.output)
