import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="下载特定数据文件")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
parser.add_argument("--down_time", default="", help="指定日期，格式如: 20241231")
parser.add_argument(
    "--down_type",
    type=int,
    required=True,
    choices=[1, 2, 3, 4],
    help="下载类型: 1=十大股东, 2=ETF申赎, 3=舆情, 4=综合信息",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.download_file(
        stock_code=args.stock_code,
        down_time=args.down_time,
        down_type=args.down_type,
    ),
)
print_output(data, args.output)
