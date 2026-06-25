# 项目边界与文件结构规划

## 目标

本仓库用于把通达信 TQ Python 的非交易基础能力整理成可直接调用的命令行脚本，并记录基础接口在真实机器上的可用性与兼容行为。

当前公开仓库只覆盖基础接口、基础诊断与相关共享运行时，不包含组合模块、持续监控或工作流型功能。

## 项目边界

### 纳入范围

- `scripts/` 根目录下的基础接口命令
- 通达信路径发现、配置存取、路径诊断
- 统一 CLI 入口与命令行输出适配
- 公式基础接口预载、格式化和底层兼容逻辑
- 与基础接口直接相关的文档、样例和测试

### 不纳入范围

- 交易相关接口开发
- 组合功能模块
- 持续监控、落盘、出图工作流
- 为未来模块化预留的通用框架或抽象层

## 当前结构

### `scripts/`

对外命令入口层。

规则：

- `scripts/` 根目录保留原子接口命令和基础诊断命令
- 每个脚本只做参数解析、调用内部能力和输出结果
- `scripts/_bootstrap.py` 与 `scripts/_formula_helpers.py` 仅作为桥接层存在

### `lib/`

内部共享逻辑层。

当前正式边界：

- `lib/cli/`：统一运行时、输出格式、命令行公共适配
- `lib/pathing/`：路径发现、配置存取、路径诊断
- `lib/formula/`：公式预载、参数兼容、底层公式回退
- `lib/tqcenter.py`：定位并加载通达信客户端 `tqcenter.py`
- `lib/config.py`：兼容出口，不新增实际逻辑

### `docs/interfaces/`

基础接口文档层。

这里记录：

- 参数与枚举说明
- 基础接口测试状态
- 真实环境兼容性说明

### 根目录

治理与索引层。

长期保留：

- `README.md`
- `ARCHITECTURE.md`
- `AGENTS.md`

## 目标文件结构

```text
/
  README.md
  ARCHITECTURE.md
  AGENTS.md
  docs/
    interfaces/
      README.md
      PARAMETERS.md
      TEST_STATUS.md
  lib/
    config.py
    tqcenter.py
    tq_constants.py
    tdx_unified.py
    cli/
      runtime.py
    formula/
      helpers.py
    pathing/
      config_store.py
      discovery.py
  scripts/
    README.md
    *.py
  tests/
    test_cli_help.py
    test_unified_cli.py
    test_pathing_discovery.py
    test_config_store.py
```

## 开发规则

### 新增接口时

1. 在 `scripts/` 根目录新增对应 CLI 入口
2. 如只服务单脚本，可先保留最小逻辑在脚本内
3. 如出现第二个复用点，再下沉到 `lib/` 对应域
4. 更新 `scripts/README.md`
5. 更新 `docs/interfaces/TEST_STATUS.md` 或相关接口文档

### 新增共享逻辑时

满足任一条件再下沉到 `lib/`：

- 被至少两个脚本复用
- 包含版本兼容分支
- 包含路径探测、输出序列化、缓存读写等横切能力
- 已经让脚本入口难以阅读

### 文档分工

- 用法入口写到 `scripts/README.md`
- 接口测试与兼容性写到 `docs/interfaces/TEST_STATUS.md`
- 边界规则、目录规则写到 `ARCHITECTURE.md`

### 验证建议

- 改统一入口时，优先跑 `tests.test_unified_cli`
- 改 CLI 参数帮助时，优先跑 `tests.test_cli_help`
- 改路径发现与配置时，优先跑 `tests.test_pathing_discovery`、`tests.test_config_store`
