---
name: tdx-direct-use
description: Use when the user wants to directly run this repository's non-trading TDX base-interface commands instead of changing code, such as querying market snapshots, K-line data, stock lists, sector members, trading calendars, financial data, dividend and bonus-share data, capital data, formula results, subscription state, or path diagnosis from natural-language requests.
---

# Tdx Direct Use

Use the repository's existing CLI commands as the first choice. Do not switch into implementation mode unless the user is asking to change behavior.

This skill can generate a portable snapshot under `bundle/`. The snapshot is local build output and is intentionally not committed to Git.

## First Step

Before running any TDX command, make sure the user has selected the intended Tongdaxin client path on that machine.

- If the active client path is wrong or unset, commands may attach to the wrong client, fail path discovery, or fail runtime initialization.
- In repository mode, tell the user to run `python tdx.py setup-tdx-path --output table` first when the client choice is not already confirmed.
- In portable mode, tell the user to run `python /abs/path/to/tdx-direct-use/run_tdx.py setup-tdx-path --output table` first when the client choice is not already confirmed.

## Read First

When working inside this repository, read these files before running commands:

- `AGENTS.md`
- `README.md`
- `scripts/README.md`

When using a copied-away portable snapshot, read these bundled references instead:

- `bundle/references/AGENTS.md`
- `bundle/references/README.md`
- `bundle/references/scripts-README.md`

Only read `lib/tdx_unified.py` or `bundle/lib/tdx_unified.py` when you need to confirm the unified command name.

If you need to refresh the bundled snapshot after repository changes, run:

`python skills/tdx-direct-use/scripts/refresh_bundle.py`

If you need a cwd-independent entry for the portable snapshot, run the wrapper script by its absolute path:

`python /abs/path/to/tdx-direct-use/run_tdx.py <command> [args]`

## Primary Workflow

1. Translate the user's request into one concrete CLI outcome.
2. In repository mode, prefer the unified entry: `python tdx.py <command> [args]`.
3. In portable mode, prefer the wrapper entry: `python /abs/path/to/tdx-direct-use/run_tdx.py <command> [args]`.
4. Fall back to `python scripts/<script>.py ...` in repository mode, or `python /abs/path/to/tdx-direct-use/run_tdx.py help <command>` plus the bundled script path in portable mode, only when the unified entry does not expose that command.
5. For read-only queries, default to `--output json` and then summarize the returned key fields for the user.
6. If the user uses relative time such as "今天" or "最近", resolve it to exact dates before running date-sensitive commands.
7. If the command fails on path or runtime initialization, run `python tdx.py diagnose-tdx-path --probe stock_list --market 5 --output json` in repository mode, or `python /abs/path/to/tdx-direct-use/run_tdx.py diagnose-tdx-path --probe stock_list --market 5 --output json` in portable mode.
8. If the environment is Linux or WSL and the TQ runtime fails to load Windows DLLs such as `TPythClient.dll` with errors like `invalid ELF header`, stop claiming the query can run locally and explain that the current shell cannot execute the Windows-side TQ runtime.

## Portable Bundle

- Generated runnable snapshot: `bundle/`
- Portable wrapper entry: `run_tdx.py`
- Bundled unified entry: `bundle/tdx.py`
- Bundled raw script entrypoints: `bundle/scripts/*.py`
- Bundled internal runtime: `bundle/lib/`
- Bundled dependency declarations: `bundle/pyproject.toml`, `bundle/requirements.txt`
- Bundled references for copied-away use: `bundle/references/*.md`

Before copying the skill away, refresh `bundle/` first. Then copy the entire `skills/tdx-direct-use/` directory, not just `SKILL.md`.

## Intent Routing

- 行情快照: `get-market-snapshot`
- K 线 / 分时 / 分笔: `get-market-data` or `subscribe-quote`
- 股票列表: `get-stock-list`
- 板块列表 / 板块成分 / 板块关系: `get-sector-list`, `get-stock-list-in-sector`, `get-relation`
- 交易日历 / 交易日: `get-trading-calendar`, `get-trading-dates`
- 扩展字段: `get-more-info`
- 财务数据: `get-financial-data`, `get-financial-data-by-date`
- 分红送转: `get-divid-factors`
- 股本信息: `get-gb-info`, `get-gb-info-by-date`
- 价量快照: `get-pricevol`
- 订阅列表: `get-subscribe-hq-stock-list`, `get-subscribe-hq-stock-list-cached`
- 公式执行: `formula-zb`, `formula-xg`, `formula-exp`, `formula-get-data`
- 路径配置与诊断: `setup-tdx-path`, `diagnose-tdx-path`

## Output Rules

- 用户只说“查一下”“看看”时，先返回核心结果，不把整段原始 JSON 全量转述。
- 用户明确要原始返回值时，再直接回传关键原文或说明命令输出结构。
- 如果命令执行失败，先给失败原因，再给下一步，而不是只贴堆栈。

## Guardrails

- 只覆盖非交易基础接口，不扩展到交易接口。
- 不为了单次查询修改脚本、统一入口或共享逻辑。
- 对 `subscribe`、`unsubscribe`、`send-*`、`create-sector`、`delete-sector`、`rename-sector` 这类有副作用的命令，只有在用户意图明确时才执行。
