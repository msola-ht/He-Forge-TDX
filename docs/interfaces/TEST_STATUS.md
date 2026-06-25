# 基础接口测试记录

更新日期：2026-06-24

## 说明

- 当前文档只记录基础接口、公式基础接口和基础诊断工具。
- 当前脚本默认输出为原始输出（`raw`）。
- 状态定义：
  - `通过`：脚本可运行，返回结果符合当前预期。
  - `部分通过`：脚本可运行，但存在特定参数组合未稳定返回有效值。
  - `待确认`：脚本可运行，但当前测试样例不足以确认行为。
  - `不支持`：当前测试环境中的 `tqcenter.py` 未提供该接口。
  - `未测试`：当前尚未执行，或因环境条件不足未进入实际验证。

## 已测试基础接口

| 序号 | 接口名 | 脚本文件 | 状态 | 备注 |
|---|---|---|---|---|
| 01 | `get_sector_list` | `scripts/get_sector_list.py` | 通过 | `--list_type 1` 正常返回板块代码和名称 |
| 02 | `get_market_snapshot` | `scripts/get_market_snapshot.py` | 通过 | `688318.SH` 快照正常返回 |
| 03 | `get_market_data` | `scripts/get_market_data.py` | 通过 | `688318.SH` 最近 5 条日线正常返回 |
| 04 | `get_stock_info` | `scripts/get_stock_info.py` | 通过 | `Name`、`Unit` 字段正常返回 |
| 05 | `get_more_info` | `scripts/get_more_info.py` | 通过 | 扩展字段正常返回 |
| 06 | `get_trading_dates` | `scripts/get_trading_dates.py` | 通过 | 交易日列表正常返回 |
| 07 | `get_stock_list` | `scripts/get_stock_list.py` | 通过 | `--market 31 --list_type 1` 正常返回 |
| 08 | `get_stock_list_in_sector` | `scripts/get_stock_list_in_sector.py` | 通过 | 板块成分股正常返回 |
| 09 | `get_user_sector` | `scripts/get_user_sector.py` | 通过 | 自定义板块列表正常返回 |
| 10 | `get_divid_factors` | `scripts/get_divid_factors.py` | 通过 | 分红配送数据正常返回 |
| 11 | `get_gb_info` | `scripts/get_gb_info.py` | 通过 | 指定日期股本数据正常返回 |
| 12 | `get_kzz_info` | `scripts/get_kzz_info.py` | 通过 | 使用当前 `market=32` 可返回的可转债代码测试通过 |
| 13 | `get_ipo_info` | `scripts/get_ipo_info.py` | 通过 | 新股/新债申购信息正常返回 |
| 14 | `get_trackzs_etf_info` | `scripts/get_trackzs_etf_info.py` | 通过 | 指数跟踪 ETF 列表正常返回 |
| 15 | `get_financial_data` | `scripts/get_financial_data.py` | 通过 | `FN1`、`FN8`、`FN134` 正常返回 |
| 16 | `get_financial_data_by_date` | `scripts/get_financial_data_by_date.py` | 部分通过 | `--year 0 --mmdd 0` 正常；`--year 2024 --mmdd 1231` 返回 `--` |
| 17 | `get_gpjy_value` | `scripts/get_gpjy_value.py` | 通过 | 股票交易数据正常返回 |
| 18 | `get_gpjy_value_by_date` | `scripts/get_gpjy_value_by_date.py` | 通过 | 按日期股票交易数据正常返回 |
| 19 | `get_bkjy_value` | `scripts/get_bkjy_value.py` | 通过 | 板块交易数据正常返回 |
| 20 | `get_bkjy_value_by_date` | `scripts/get_bkjy_value_by_date.py` | 通过 | 按日期板块交易数据正常返回 |
| 21 | `create_sector` | `scripts/create_sector.py` | 通过 | 使用测试板块 `TST001` 创建成功 |
| 22 | `delete_sector` | `scripts/delete_sector.py` | 通过 | 测试板块 `TST001` 删除成功 |
| 23 | `rename_sector` | `scripts/rename_sector.py` | 通过 | `TST001` 重命名为“测试板块2”成功 |
| 24 | `clear_sector` | `scripts/clear_sector.py` | 通过 | `TST001` 清空成分股成功 |
| 25 | `refresh_cache` | `scripts/refresh_cache.py` | 通过 | `AG` 市场在 `force=false` 和 `force=true` 下均返回成功 |
| 26 | `refresh_kline` | `scripts/refresh_kline.py` | 通过 | `688318.SH` 日线缓存刷新成功 |
| 27 | `subscribe_hq` | `scripts/subscribe_hq.py` | 通过 | 订阅成功；脚本内置最小空回调用于兼容部分客户端签名 |
| 28 | `get_subscribe_hq_stock_list` | `scripts/get_subscribe_hq_stock_list.py` | 部分通过 | 独立进程 CLI 场景下原始接口返回空列表 |
| 29 | `unsubscribe_hq` | `scripts/unsubscribe_hq.py` | 通过 | 取消订阅成功；取消后列表为空 |
| 30 | `download_file` | `scripts/download_file.py` | 通过 | `down_type=4` 下载成功 |
| 31 | `send_message` | `scripts/send_message.py` | 通过 | 客户端消息发送成功 |
| 32 | `send_file` | `scripts/send_file.py` | 通过 | 文件发送成功 |
| 33 | `send_warn` | `scripts/send_warn.py` | 通过 | 单条预警信号发送成功 |
| 34 | `send_bt_data` | `scripts/send_bt_data.py` | 通过 | 使用 `--data_row` 方式发送回测数据成功 |
| 35 | `send_user_block` | `scripts/send_user_block.py` | 通过 | 不传 `block_code` 时发送到“临时条件股”成功 |
| 36 | `print_to_tdx` | `scripts/print_to_tdx.py` | 通过 | 使用 `samples/print_to_tdx_sample.csv` 成功生成并移动 XML/SP 文件 |
| 37 | `formula_format_data` | `scripts/formula_format_data.py` | 通过 | 日线 `count=10` 可正常格式化并输出 JSON 文件 |
| 38 | `formula_set_data` | `scripts/formula_set_data.py` | 通过 | 读取格式化结果后成功写入公式数据 |
| 39 | `formula_set_data_info` | `scripts/formula_set_data_info.py` | 通过 | `688318.SH` + `count=10` 成功写入公式数据信息 |
| 40 | `formula_get_data` | `scripts/formula_get_data.py` | 通过 | 单命令预载并执行 `MACD` 后可正常返回当前公式上下文数据 |
| 41 | `formula_zb` | `scripts/formula_zb.py` | 通过 | `MACD` + `688318.SH` + `prepare_count=120` 正常返回 `DEA/DIF/MACD` |
| 42 | `formula_xg` | `scripts/formula_xg.py` | 通过 | 改用真实公式代码 `UPN` 后可正常返回 |
| 43 | `formula_exp` | `scripts/formula_exp.py` | 部分通过 | 基础调用通过，但部分客户端不接受 `xsflag` 参数 |
| 44 | `formula_process_mul_xg` | `scripts/formula_process_mul_xg.py` | 通过 | 批量返回正常 |
| 45 | `formula_process_mul_zb` | `scripts/formula_process_mul_zb.py` | 通过 | 批量调用正常返回 |
| 46 | `formula_process_mul_exp` | `scripts/formula_process_mul_exp.py` | 通过 | 批量返回 `ENTERLONG/EXITLONG` |
| 47 | `formula_get_all` | `scripts/formula_get_all.py` | 通过 | 在 1.0.12 mock 客户端环境下可正常返回技术指标公式列表 |
| 48 | `formula_get_info` | `scripts/formula_get_info.py` | 通过 | `MACD` 公式详情正常返回，包含参数和输出线定义 |
| 49 | `get_gb_info_by_date` | `scripts/get_gb_info_by_date.py` | 通过 | 区间股本数据正常返回 `Date/Ltgb/Zgb` 序列 |
| 50 | `get_scjy_value` | `scripts/get_scjy_value.py` | 部分通过 | 当前样例可运行，但未返回有效数值 |
| 51 | `get_scjy_value_by_date` | `scripts/get_scjy_value_by_date.py` | 部分通过 | 当前样例返回 `['--','--']` |
| 52 | `exec_to_tdx` | `scripts/exec_to_tdx.py` | 通过 | 调用成功，返回 `ErrorId=0` |
| 53 | `get_match_stkinfo` | `scripts/get_match_stkinfo.py` | 通过 | 关键字 `财富` 可正常返回匹配证券列表 |
| 54 | `get_gp_one_data` | `scripts/get_gp_one_data.py` | 通过 | `GO1/GO3/GO10` 正常返回 |
| 55 | `get_pricevol` | `scripts/get_pricevol.py` | 通过 | 正常返回 `LastClose/Now/Volume` |
| 56 | `get_relation` | `scripts/get_relation.py` | 通过 | 正常返回所属行业/地区/概念/指数等板块信息 |
| 57 | `subscribe_quote` | `scripts/subscribe_quote.py` | 部分通过 | 已绕过上游脚本缺陷，但当前客户端仍返回 `server return none` |
| 58 | `get_trading_calendar` | `scripts/get_trading_calendar.py` | 通过 | `SH 20260601-20260630` 正常返回交易日列表 |
| 59 | `get_subscribe_hq_stock_list_cached` | `scripts/get_subscribe_hq_stock_list_cached.py` | 通过 | 原始接口返回空列表时，可正确回退到本地订阅状态缓存 |
| 60 | `diagnose_tdx_path` | `scripts/diagnose_tdx_path.py` | 通过 | 可正确显示当前命中路径、模块加载状态，并通过探针验证基础连通性 |

## 当前结论

- `01` 到 `15`：通过
- `16`：部分通过
- `17` 到 `27`：通过
- `28`：部分通过
- `29` 到 `42`：通过
- `43`：部分通过
- `44` 到 `49`：通过
- `50` 到 `51`：部分通过
- `52` 到 `56`：通过
- `57`：部分通过（当前按客户端未实装处理）
- `58` 到 `60`：通过

## 备注

- `get_kzz_info` 测试前，优先先跑 `python scripts/get_stock_list.py --market 32 --list_type 1`，再从结果里挑当前实际存在的可转债代码测试。
- `get_financial_data_by_date` 当前不做语义修正，保持原始接口行为；后续如需深入排查，应单独针对年份/报告期组合测试。
- `subscribe_hq` 在部分 `tqcenter.py` 版本中必须传合法回调函数，当前脚本已内置最小空回调用于命令行测试。
- `subscribe_hq`、`subscribe_quote` 现已补 `keep_alive` 运行模式；默认仍是“发起订阅并立即返回结果”的测试方式，如需持续接收回调，需显式传 `--keep_alive true`。
- `get_subscribe_hq_stock_list.py` 保持纯透传包装；在独立进程 CLI 场景下，即使订阅成功，原始接口也可能返回空列表。
- `get_subscribe_hq_stock_list_cached.py` 为增强版包装；当真实接口无返回时，会额外回退读取本地订阅状态缓存。
- `diagnose_tdx_path.py` 会列出配置文件、环境变量、注册表、常见目录四类候选路径，显示当前实际命中的 `PYPlugins/user`，并可选调用 `get_stock_list` 或 `get_market_snapshot` 验证基础连通性。
- `setup_tdx_path.py` 支持先列出自动找到的候选路径，再用 `--pick <序号>` 保存；如果自动候选不对，可继续用 `--user-dir <路径>` 手动指定并持久化。
- `formula_exp.py` 的 `--xsflag` 存在版本差异：脚本当前按“支持则透传，不支持则在显式传参时报错”处理。
- `formula_zb`、`formula_xg`、`formula_exp` 已按“可直接使用”处理：可直接传 `--prepare_stock_code` 等参数，由脚本先调用 `formula_set_data_info` 再执行公式；若已有 `formula_format_data` 输出文件，也可通过 `--prepare_stock_data_file` 先走 `formula_set_data`。
- `formula_get_data` 在当前环境的实测返回值为当前公式上下文里的 K 线数据列表，不等于 `formula_zb` 返回的指标线结果。
- `formula_format_data` 若使用 `--data_file`，输入文件应来自 `get_market_data --output json`，否则原始输出无法稳定反序列化。
- `tq.price_df` 属于对 `get_market_data` 返回结果做二次整理的 DataFrame helper，不是当前仓库单独暴露的命令行主接口。
- `formula_get_all`、`formula_get_info` 当前带有 `TdxFuncMain` 实验性回退；是否可用取决于本机 `TPythClient.dll` 是否支持。
- `get_scjy_value`、`get_scjy_value_by_date` 当前只确认“脚本可运行”；如需确认字段语义，应更换字段或样例日期继续测。
- `subscribe_quote` 在当前测试过的客户端中都标注为“暂无实际功能”；当前即使绕过脚本缺陷，底层仍返回 `server return none`，因此先按“接口存在但客户端不可用”处理。
