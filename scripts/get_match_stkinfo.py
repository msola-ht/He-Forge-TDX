import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="按名称/拼音/代码模糊检索证券信息")
parser.add_argument("--key_word", required=True, help="检索关键字，如: 财富 688318 CFQS")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_match_stkinfo(key_word=args.key_word),
)
print_output(data, args.output)
