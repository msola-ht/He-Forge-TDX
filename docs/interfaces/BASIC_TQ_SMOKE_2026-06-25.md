# 基础接口真实 TQ 冒烟记录（2026-06-25）

## 执行环境

- 日期：2026-06-25
- 系统：Windows
- Python：本机 `python`
- 通达信用户目录：已在本机真实 `PYPlugins/user` 目录下验证
- 命令：

```bash
python scripts/diagnostics/run_basic_tq_smoke.py --include-write-ops --show_output --trackzs_code 950162.CSI --output json
```

## 结果摘要

- 总命令数：35
- 退出码成功：35
- 返回码失败：0
- 按当前仓库校验规则计为失败：0
- 有效返回样例：35
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

- 本报告同时记录“退出码是否成功”和“按当前仓库校验规则是否得到有效结果”两套口径。
- 本次报告使用 `950162.CSI` 作为 `get-trackzs-etf-info` 的验证样例，当前已可稳定返回有效 ETF 列表。
- 旧样例 `000300.CSI` 曾在本机真实 TQ 环境下返回 `{}`，同时 stderr 含 `server return none`；仓库当前已将基础冒烟默认样例切换为 `950162.CSI`。
- `formula-set-data` 依赖 `formula-format-data` 输出文件；冒烟脚本当前会自动生成并使用临时文件：
  `%TEMP%\tdx_basic_tq_smoke\formula_format_000001_SZ.json`
- `get-kzz-info` 依赖实际存在的可转债代码；冒烟脚本当前会先执行 `get-stock-list --market 32 --list_type 1` 并自动选取首个可用代码。
