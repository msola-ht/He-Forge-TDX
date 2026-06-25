"""通达信常用参数与枚举定义。"""

PERIOD_CHOICES = ["1m", "5m", "15m", "30m", "1h", "1d", "1w", "1mon", "1q", "1y", "tick"]
PERIOD_LABELS = {
    "1m": "1分钟",
    "5m": "5分钟",
    "15m": "15分钟",
    "30m": "30分钟",
    "1h": "60分钟（1小时）",
    "1d": "1天",
    "1w": "1周",
    "1mon": "1月",
    "1q": "1季",
    "1y": "1年",
    "tick": "分笔",
}
PERIOD_HELP_TEXT = "K线周期"

DIVIDEND_TYPE_CHOICES = ["none", "front", "back"]
DIVIDEND_TYPE_LABELS = {
    "none": "不复权",
    "front": "前复权",
    "back": "后复权",
}
DIVIDEND_TYPE_INT_MAP = {
    "none": 0,
    "front": 1,
    "back": 2,
}
DIVIDEND_TYPE_INT_CHOICES = [DIVIDEND_TYPE_INT_MAP[name] for name in DIVIDEND_TYPE_CHOICES]
DIVIDEND_TYPE_HELP_TEXT = "复权类型: none=不复权, front=前复权, back=后复权"
DIVIDEND_TYPE_INT_HELP_TEXT = "复权类型: 0=不复权, 1=前复权, 2=后复权"

MARKET_TYPE_DEFINITIONS = (
    {"name": ".SZ", "type": "int", "value": 0, "description": "深圳交易所"},
    {"name": ".SH", "type": "int", "value": 1, "description": "上海交易所"},
    {"name": ".BJ", "type": "int", "value": 2, "description": "北京交易所"},
    {"name": ".NQ", "type": "int", "value": 44, "description": "新三板"},
    {"name": ".SHO", "type": "int", "value": 8, "description": "上海个股期权"},
    {"name": ".SZO", "type": "int", "value": 9, "description": "深圳个股期权"},
    {"name": ".HK", "type": "int", "value": 31, "description": "香港交易所"},
    {"name": ".US", "type": "int", "value": 74, "description": "美国股票"},
    {"name": ".CSI", "type": "int", "value": 62, "description": "中证指数"},
    {"name": ".CNI", "type": "int", "value": 102, "description": "国证指数"},
    {"name": ".HG", "type": "int", "value": 38, "description": "国内宏观指标"},
    {"name": ".CFF", "type": "int", "value": 47, "description": "中金期货"},
    {"name": ".CZC", "type": "int", "value": 28, "description": "郑州期货"},
    {"name": ".DCE", "type": "int", "value": 29, "description": "大连期货"},
    {"name": ".SHF", "type": "int", "value": 30, "description": "上海期货"},
    {"name": ".GFE", "type": "int", "value": 66, "description": "广州期货"},
    {"name": ".INE", "type": "int", "value": 30, "description": "上海能源"},
    {"name": ".HI", "type": "int", "value": 27, "description": "港股指数"},
    {"name": ".OF", "type": "int", "value": 33, "description": "开放式基金净值"},
    {"name": ".CFFO", "type": "int", "value": 7, "description": "中金所期权"},
    {"name": ".CZCO", "type": "int", "value": 4, "description": "郑州期货期权"},
    {"name": ".DCEO", "type": "int", "value": 5, "description": "大连期货期权"},
    {"name": ".SHFO", "type": "int", "value": 6, "description": "上海期货期权"},
    {"name": ".GFEO", "type": "int", "value": 67, "description": "广州期货期权"},
    {"name": ".QHZ", "type": "int", "value": 42, "description": "期货类指数"},
)

ORDER_TYPE_DEFINITIONS = (
    {"name": "STOCK_BUY", "type": "int", "value": 0, "description": "买"},
    {"name": "STOCK_SELL", "type": "int", "value": 1, "description": "卖"},
    {"name": "CREDIT_BUY", "type": "int", "value": 0, "description": "担保品买入"},
    {"name": "CREDIT_SELL", "type": "int", "value": 1, "description": "担保品卖出"},
    {"name": "CREDIT_FIN_BUY", "type": "int", "value": 69, "description": "融资买入"},
    {"name": "CREDIT_SLO_SELL", "type": "int", "value": 70, "description": "融券卖出"},
    {"name": "CREDIT_COV_BUY", "type": "int", "value": 71, "description": "买券还券"},
    {"name": "CREDIT_STK_REPAY", "type": "int", "value": 76, "description": "卖券还款"},
    {"name": "ETF_PURCHASE", "type": "int", "value": 45, "description": "基金申购"},
    {"name": "ETF_REDEMPTION", "type": "int", "value": 46, "description": "基金赎回"},
    {"name": "FUTURE_OPEN_LONG", "type": "int", "value": 101, "description": "期货开多"},
    {"name": "FUTURE_OPEN_SHORT", "type": "int", "value": 102, "description": "期货开空"},
    {"name": "FUTURE_CLOSE_LONG", "type": "int", "value": 103, "description": "期货平多"},
    {"name": "FUTURE_CLOSE_SHORT", "type": "int", "value": 104, "description": "期货平空"},
    {"name": "OPTION_OPEN_LONG", "type": "int", "value": 201, "description": "期权开多"},
    {"name": "OPTION_OPEN_SHORT", "type": "int", "value": 202, "description": "期权开空"},
    {"name": "OPTION_CLOSE_LONG", "type": "int", "value": 203, "description": "期权平多"},
    {"name": "OPTION_CLOSE_SHORT", "type": "int", "value": 204, "description": "期权平空"},
)

PRICE_TYPE_DEFINITIONS = (
    {"name": "PRICE_MY", "type": "int", "value": 0, "description": "自填价"},
    {"name": "PRICE_SJ", "type": "int", "value": 1, "description": "市价"},
    {"name": "PRICE_ZTJ", "type": "int", "value": 2, "description": "涨停价/笼子上限"},
    {"name": "PRICE_DTJ", "type": "int", "value": 3, "description": "跌停价/笼子下限"},
)

ORDER_STATUS_DEFINITIONS = (
    {"name": "WTSTATUS_NULL", "type": "int", "value": 0, "description": "无效单"},
    {"name": "WTSTATUS_NOCJ", "type": "int", "value": 1, "description": "未成交"},
    {"name": "WTSTATUS_PARTCJ", "type": "int", "value": 2, "description": "部分成交"},
    {"name": "WTSTATUS_ALLCJ", "type": "int", "value": 3, "description": "全部成交"},
    {"name": "WTSTATUS_BCBC", "type": "int", "value": 4, "description": "部分成交部分撤单"},
    {"name": "WTSTATUS_ALLCD", "type": "int", "value": 5, "description": "全部撤单"},
)


def dividend_type_to_int(dividend_type: str) -> int:
    """将字符串复权类型映射为底层接口使用的整数值。"""

    normalized = str(dividend_type).strip().lower()
    return DIVIDEND_TYPE_INT_MAP.get(normalized, 0)


__all__ = [
    "DIVIDEND_TYPE_CHOICES",
    "DIVIDEND_TYPE_HELP_TEXT",
    "DIVIDEND_TYPE_INT_CHOICES",
    "DIVIDEND_TYPE_INT_HELP_TEXT",
    "DIVIDEND_TYPE_INT_MAP",
    "DIVIDEND_TYPE_LABELS",
    "MARKET_TYPE_DEFINITIONS",
    "ORDER_STATUS_DEFINITIONS",
    "ORDER_TYPE_DEFINITIONS",
    "PERIOD_CHOICES",
    "PERIOD_HELP_TEXT",
    "PERIOD_LABELS",
    "PRICE_TYPE_DEFINITIONS",
    "dividend_type_to_int",
]
