# 脚本命令说明

这里先收基础接口和基础诊断命令，不展开组合模块工作流。

统一入口优先使用：

```bash
python tdx.py <command> [args]
```

如果已安装 console script，也可直接使用 `tdx <command> [args]`。
如需直接调用单脚本，现有 `python scripts/<script>.py ...` 用法继续保留。

详细文档见：

- [通达信常用参数与枚举](../docs/interfaces/PARAMETERS.md)
- [基础接口测试状态](../docs/interfaces/TEST_STATUS.md)

## 通用规则

- 查看单个脚本参数：`python scripts/<脚本名>.py --help`
- 所有对外命令脚本统一支持：`--output raw|json|table`
- 所有走 TQ 的 Python 脚本启动前都会先做一次基础连通性检测
- 如果基础检测失败，先运行 `python scripts/diagnose_tdx_path.py --probe stock_list --market 5 --output json`
- 通用基础接口不只支持 A 股；大多数 `--stock_code` / `--stock_list` 参数都直接传“代码.市场”即可，例如 `000001.SZ`、`600000.SH`、`00700.HK`、`AAPL.US`
- 不同市场优先通过代码后缀区分，不要把美股、港股代码按 A 股格式传入
- 需要按市场枚举传参的脚本，例如 `get_stock_list`、`diagnose_tdx_path --probe stock_list`，可参考 [通达信常用参数与枚举](../docs/interfaces/PARAMETERS.md)；例如 `.US=74`、`.HK=31`

### 非 A 股使用方式

- 美股快照：`python scripts/get_market_snapshot.py --stock_code AAPL.US --output json`
- 美股 K 线：`python scripts/get_market_data.py --stock_list AAPL.US --period 1d --count 5 --output json`
- 港股快照：`python scripts/get_market_snapshot.py --stock_code 00700.HK --output json`
- 港股 K 线：`python scripts/get_market_data.py --stock_list 00700.HK --period 1d --count 5 --output json`
- 如果不确定证券代码，可先模糊检索：`python scripts/get_match_stkinfo.py --key_word AAPL --output json`

## 路径配置与诊断

- 选择通达信目录：`python scripts/setup_tdx_path.py --output table`
- 查看全部候选：`python scripts/setup_tdx_path.py --show-all --output table`
- 诊断当前生效路径：`python scripts/diagnose_tdx_path.py --output json`
- 一次跑完整体基础冒烟：`python scripts/diagnostics/run_basic_tq_smoke.py --output table`
- 如果要连订阅、自定义板块、消息发送、公式写入等副作用命令一起跑：`python scripts/diagnostics/run_basic_tq_smoke.py --include-write-ops --output table`
- Windows 交互式路径配置入口：`setup_tdx_path.bat`

## 行情与基础数据

- 最新快照：`python scripts/get_market_snapshot.py --stock_code 000001.SZ --output json`
- K 线数据：`python scripts/get_market_data.py --stock_list 000001.SZ --period 1d --count 5 --output json`
- 股票列表：`python scripts/get_stock_list.py --market 5 --list_type 1 --output json`
- 板块列表：`python scripts/get_sector_list.py --list_type 1 --output json`
- 板块成分：`python scripts/get_stock_list_in_sector.py --block_code 881001.SH --output json`
- 板块关系：`python scripts/get_relation.py --stock_code 000001.SZ --output json`
- 交易日历：`python scripts/get_trading_calendar.py --market SH --start_time 20260601 --end_time 20260630 --output json`

## 扩展资料

- 扩展字段：`python scripts/get_more_info.py --stock_code 000001.SZ --field_list Name Zjl --output json`
- 财务数据：`python scripts/get_financial_data.py --stock_list 000001.SZ --field_list FN1 FN8 FN134 --output json`
- 指定报告期财务数据：`python scripts/get_financial_data_by_date.py --stock_list 000001.SZ --year 2024 --mmdd 1231 --output json`
- 分红送转：`python scripts/get_divid_factors.py --stock_code 000001.SZ --output json`
- 股本信息：`python scripts/get_gb_info.py --stock_code 000001.SZ --date_list 20250624 --output json`
- 区间股本信息：`python scripts/get_gb_info_by_date.py --stock_code 000001.SZ --start_date 20240101 --end_date 20250624 --output json`

## 订阅与客户端操作

- 订阅行情：`python scripts/subscribe_hq.py --stock_list 000001.SZ --output json`
- 纯透传订阅列表：`python scripts/get_subscribe_hq_stock_list.py --output json`
- 带缓存回退的订阅列表：`python scripts/get_subscribe_hq_stock_list_cached.py --output json`
- 取消订阅：`python scripts/unsubscribe_hq.py --stock_list 000001.SZ --output json`
- 发送客户端消息：`python scripts/send_message.py --msg_str "MSG,策略运行中|买入信号数：3" --output json`
- 发送文件：`python scripts/send_file.py --file_path demo.txt --output json`
- 发送预警：`python scripts/send_warn.py --stock_list 000001.SZ --price_list 10.5 --close_list 10.2 --volum_list 123456 --output json`
- 推送自定义板块：`python scripts/send_user_block.py --block_code TST001 --stocks 000001.SZ --output json`

## 公式基础接口

- 指标公式：`python scripts/formula_zb.py --formula_name MACD --formula_arg 12,26,9 --prepare_stock_code 000001.SZ --prepare_stock_period 1d --prepare_count 120 --output json`
- 表达式公式：`python scripts/formula_exp.py --formula_name MACD --formula_arg 12,26,9 --prepare_stock_code 000001.SZ --prepare_stock_period 1d --prepare_count 120 --output json`
- 读取当前公式数据：`python scripts/formula_get_data.py --formula_kind exp --formula_name MACD --formula_arg 12,26,9 --prepare_stock_code 000001.SZ --prepare_stock_period 1d --prepare_count 120 --output json`
- 批量公式选股：`python scripts/formula_process_mul_xg.py --formula_name UPN --formula_arg 3 --stock_list 000001.SZ 600000.SH --output json`
- 批量公式指标：`python scripts/formula_process_mul_zb.py --formula_name MACD --formula_arg 12,26,9 --stock_list 000001.SZ 600000.SH --output json`

## 说明

- 当前公开仓库只保留基础接口和基础诊断命令。
- 组合模块、持续监控和相关工作流不在本仓库维护。
