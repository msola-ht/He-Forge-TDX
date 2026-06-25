import argparse
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from lib.cli.runtime import add_output_argument, print_output, tq_session


def load_dataframe(path_str: str) -> pd.DataFrame:
    path = Path(path_str)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)

    if suffix == ".json":
        text = path.read_text(encoding="utf-8")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return pd.read_json(path)
        return pd.DataFrame(data)

    raise ValueError(f"暂不支持的文件类型: {path}")


parser = argparse.ArgumentParser(description="导出数据到通达信界面")
parser.add_argument(
    "--df_file",
    nargs="+",
    required=True,
    help="DataFrame 输入文件列表，支持 .csv 或 .json，第一列应为日期列",
)
parser.add_argument("--sp_name", default="", help="因子名称，用于生成 .sp 文件名")
parser.add_argument(
    "--xml_filename",
    required=True,
    help="生成的 XML 文件名，需包含 .xml 后缀",
)
parser.add_argument(
    "--jsn_filenames",
    nargs="+",
    required=True,
    help="JSON 文件名列表，数量必须与 df_file 一致",
)
parser.add_argument("--vertical", type=int, default=None, help="纵向排列的表格组数")
parser.add_argument("--horizontal", type=int, default=None, help="横向排列的表格组数")
parser.add_argument(
    "--height",
    nargs="*",
    default=None,
    help='各 gridctrl 高度列表，如: 0.4 0.6',
)
parser.add_argument(
    "--table_names",
    nargs="*",
    default=None,
    help="各组表格标题列表，数量需与 df_file 一致",
)
add_output_argument(parser)

args = parser.parse_args()

df_list = [load_dataframe(path) for path in args.df_file]

with tq_session(__file__) as tq:
    result = tq.print_to_tdx(
        df_list=df_list,
        sp_name=args.sp_name,
        xml_filename=args.xml_filename,
        jsn_filenames=args.jsn_filenames,
        vertical=args.vertical,
        horizontal=args.horizontal,
        height=args.height,
        table_names=args.table_names,
    )
    output = {
        "df_file": args.df_file,
        "sp_name": args.sp_name,
        "xml_filename": args.xml_filename,
        "jsn_filenames": args.jsn_filenames,
        "vertical": args.vertical,
        "horizontal": args.horizontal,
        "height": args.height,
        "table_names": args.table_names,
        "result": result,
    }
    print_output(output, args.output)
