import argparse
import json

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="发送回测数据到客户端")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
parser.add_argument(
    "--time_list",
    nargs="+",
    required=True,
    help="时间列表，格式: YYYYMMDD 或 YYYYMMDDHHMMSS",
)
parser.add_argument(
    "--data_list_json",
    default="",
    help='二维数组 JSON 字符串，如: \'[["136.60","131.74","1","0"],["135.30","131.48","0","1"]]\'',
)
parser.add_argument(
    "--data_row",
    action="append",
    default=[],
    help='单行数据，支持多次传入，如: --data_row "136.60,131.74,1,0" --data_row "135.30,131.48,0,1"',
)
parser.add_argument("--count", type=int, default=1, help="数据条数，必须大于 0")
add_output_argument(parser)

args = parser.parse_args()

if args.data_list_json:
    data_list = json.loads(args.data_list_json)
elif args.data_row:
    data_list = [row.split(",") for row in args.data_row]
else:
    raise ValueError("必须提供 --data_list_json 或至少一个 --data_row")

data = run_tq_call(
    __file__,
    lambda tq: tq.send_bt_data(
        stock_code=args.stock_code,
        time_list=args.time_list,
        data_list=data_list,
        count=args.count,
    ),
)
print_output(data, args.output)
