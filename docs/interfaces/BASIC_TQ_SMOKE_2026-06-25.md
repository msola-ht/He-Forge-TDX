# 基础接口真实 TQ 冒烟记录（2026-06-25）

## 执行环境

- 日期：2026-06-25
- 系统：Windows
- Python：本机 `python`
- 通达信用户目录：已在本机真实 `PYPlugins/user` 目录下验证
- 命令：

```bash
python scripts/diagnostics/run_basic_tq_smoke.py --include-write-ops --show_output --output json
```

## 结果摘要

- 总命令数：35
- 退出码成功：35
- 返回码失败：0
- 按当前仓库校验规则计为失败：1
- 有效返回样例：34
- 包含写操作：是

## 覆盖范围

### 预处理

- 自动发现一只可转债代码
- 自动执行 `formula-format-data` 并生成临时 JSON 文件

### 路径与诊断

- `diagnose-tdx-path`

### 行情与市场

- `get-stock-list`
- `get-stock-info`
- `get-market-snapshot`
- `get-market-data`
- `get-sector-list`
- `get-stock-list-in-sector`
- `get-user-sector`
- `get-trading-calendar`
- `get-trading-dates`
- `get-trackzs-etf-info`

### 扩展资料

- `get-more-info`
- `get-relation`
- `get-divid-factors`
- `get-financial-data`
- `get-gb-info`
- `get-kzz-info`
- `get-ipo-info`

### 客户端操作

- `get-subscribe-hq-stock-list-cached`
- `subscribe-hq`
- `unsubscribe-hq`
- `create-sector`
- `send-user-block`
- `clear-sector`
- `delete-sector`
- `send-message`

### 公式接口

- `formula-get-all`
- `formula-get-info`
- `formula-zb`
- `formula-exp`
- `formula-get-data`
- `formula-set-data-info`
- `formula-set-data`

## 备注

- 本次冒烟以“命令可运行并返回成功退出码”为通过标准。
- `get-trackzs-etf-info` 在本次样例 `000300.CSI` 下返回 `{}`，同时 stderr 含 `server return none`；当前仓库的冒烟脚本已把这类“空 JSON 成功返回”按失败处理，不把它当作有效数据样例。
- `formula-set-data` 依赖 `formula-format-data` 输出文件；冒烟脚本当前会自动生成并使用临时文件：
  `%TEMP%\tdx_basic_tq_smoke\formula_format_000001_SZ.json`
- `get-kzz-info` 依赖实际存在的可转债代码；冒烟脚本当前会先执行 `get-stock-list --market 32 --list_type 1` 并自动选取首个可用代码。
