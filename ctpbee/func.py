"""
function used to cancle order, sender, qry_position and qry_account

"""
from typing import Text
from ctpbee.context import current_app
from ctpbee.ctp.constant import OrderRequest, CancelRequest, EVENT_TRADE, EVENT_SHARED, EVENT_ORDER, OrderData, \
    TradeData, PositionData, AccountData, TickData, SharedData, BarData, EVENT_POSITION
from ctpbee.event_engine import Event
from ctpbee.ctp.constant import EVENT_TICK, EVENT_BAR
from ctpbee.exceptions import TraderError


def send_order(order_req: OrderRequest):
    """发单"""
    app = current_app()
    if not app.config.get("TD_FUNC"):
        raise TraderError(message="交易功能未开启", args=("交易功能未开启",))
    return app.trader.send_order(order_req)


def cancle_order(cancle_req: CancelRequest):
    """撤单"""
    app = current_app()
    if not app.config.get("TD_FUNC"):
        raise TraderError(message="交易功能未开启", args=("交易功能未开启",))
    app.trader.cancel_order(cancle_req)


def subscribe(symbol: Text) -> None:
    """订阅"""
    app = current_app()
    app.market.subscribe(symbol)


def query_func(type: Text) -> None:
    """查询持仓 or 账户"""
    app = current_app()
    if not app.config.get("TD_FUNC"):
        raise TraderError(message="交易功能未开启", args=("交易功能未开启",))
    if type == "position":
        app.trader.query_position()
    if type == "account":
        app.trader.query_account()


class ExtAbstract(object):
    """
        如果你要开发插件需要继承此抽象demo
        usage:
        ## coding:
            class Processor(ApiAbstract):
                ...

            data_processor = Processor("data_processor", app)
                        or
            data_processor = Processor("data_processor")
            data_processor.init_app(app)
    """

    def __init__(self, name, app=None):
        self.extension_name = name
        self.app = app

        self.map = {
            EVENT_TICK: self.on_tick,
            EVENT_BAR: self.on_bar,
            EVENT_ORDER: self.on_order,
            EVENT_SHARED: self.on_shared,
            EVENT_TRADE: self.on_trade,
            EVENT_POSITION: self.on_position,
        }

    def on_order(self, order: OrderData, **kwargs) -> None:
        raise NotImplemented

    def on_shared(self, shared: SharedData, **kwargs) -> None:
        raise NotImplemented

    def on_bar(self, bar: BarData, interval: int, **kwargs) -> None:
        raise NotImplemented

    def on_tick(self, tick: TickData, **kwargs) -> None:
        raise NotImplemented

    def on_trade(self, trade: TradeData, **kwargs) -> None:
        raise NotImplemented

    def on_position(self, position: PositionData, **kwargs) -> None:
        raise NotImplemented

    def __call__(self, event):
        self.map[event.type](event.data)

    def init_app(self, app):
        if app:
            self.app = app

    def __repr__(self):
        return f"Api --> {self.extension_name}"

    def __str__(self):
        return self.extension_name
