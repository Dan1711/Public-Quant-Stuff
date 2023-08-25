from collections import defaultdict
from market import BidOrAsk
import matplotlib.pyplot as plt


class Order: 
    def __init__(self, bid_or_ask, size):
        self.bid_or_ask = bid_or_ask
        self.size = size
        self.remaining_size = size
        self.order_id=None

    def filled(self):
        return self.remaining_size == 0.0

class Limit:
    def __init__(self):
        self.orders = []
        self.next_order_id=1
    
    def fill_order(self, market_order):
        orders_to_remove = []
        for limit_order in self.orders:
            if limit_order.remaining_size <= market_order.remaining_size:
                market_order.remaining_size -= limit_order.remaining_size
                orders_to_remove.append(limit_order)
            else:
                limit_order.remaining_size -= market_order.remaining_size
                market_order.remaining_size = 0.0
                break
            if market_order.filled():
                break
        
        for order in orders_to_remove:
            self.orders.remove(order)
        
        self.orders = [order for order in self.orders if not order.filled()]

        if market_order.remaining_size > 0.0:
            matching_limit_orders = [limit_order for limit_order in self.orders if limit_order.bid_or_ask != market_order.bid_or_ask and limit_order.remaining_size > 0.0]
            for limit_order in matching_limit_orders:
                if limit_order.remaining_size <= market_order.remaining_size:
                    market_order.remaining_size -= limit_order.remaining_size
                    self.orders.remove(limit_order)
                else:
                    limit_order.remaining_size -= market_order.remaining_size
                    market_order.remaining_size = 0.0
                    break
                if market_order.filled():
                    break
            self.orders = [order for order in self.orders if not order.filled()]

        if market_order.remaining_size > 0.0:
            self.orders.append(Order(market_order.bid_or_ask, market_order.remaining_size)) 
    def add_order(self, order_size):
        order_size.order_id=self.next_order_id
        self.next_order_id +=1
        for existing_order in self.orders:
            if existing_order.bid_or_ask == order_size.bid_or_ask:
                existing_order.remaining_size += order_size.remaining_size
                existing_order.remaining_size +=order_size.remaining_size
                break
        else:
            self.orders.append(order_size)

    def cancel_order(self, order_id):
        orders_to_remove = [order for order in self.orders if order.order_id == order_id]
        canceled_order_total_size = sum(order.remaining_size for order in orders_to_remove)

        for order in orders_to_remove:
            self.orders.remove(order)

        if self.orders:
            self.remaining_size = sum(order.remaining_size for order in self.orders)
        else:
            self.remaining_size = 0.0
    
class Orderbook:
    def __init__(self):
        self.asks = defaultdict(Limit)
        self.bids = defaultdict(Limit)
        
    def fill_market_order(self, market_order):
        orders_to_fill = self.asks if market_order.bid_or_ask == BidOrAsk.Bid else self.bids

        while market_order.remaining_size > 0.0 and orders_to_fill:
            best_price = min(orders_to_fill.keys()) if market_order.bid_or_ask == BidOrAsk.Bid else max(orders_to_fill.keys())
            best_price_orders = orders_to_fill[best_price]
            best_price_orders.fill_order(market_order)

            if best_price_orders.orders:
                best_price_orders_remaining = sum(order.remaining_size for order in best_price_orders.orders)
                if best_price_orders_remaining > 0.0:
                    if market_order.bid_or_ask == BidOrAsk.Bid:
                        self.asks[best_price] = best_price_orders
                    else:
                        self.bids[best_price] = best_price_orders
                else:
                    del orders_to_fill[best_price]
            else:
                del orders_to_fill[best_price]

            if market_order.filled():
                break
        for price, limit_orders in orders_to_fill.items():
            limit_orders.orders = [order for order in limit_orders.orders if not order.filled()]
            if not limit_orders.orders:
                del orders_to_fill[price]

    def add_order(self, price, order):
        if order.bid_or_ask == BidOrAsk.Bid:
            self.bids[price].add_order(order)
        else:
            self.asks[price].add_order(order)

    def cancel_limit_order(self, price, order_id, side):
        if side == BidOrAsk.Bid:
            if price in self.bids and order_id in self.bids[price].orders:
                canceled_order = self.bids[price].orders[order_id]
                self.bids[price].remaining_size -= canceled_order.remaining_size
                if self.bids[price].remaining_size <= 0:
                    del self.bids[price]
                del self.orders[order_id]
        elif side == BidOrAsk.Ask:
            if price in self.asks and order_id in self.asks[price].orders:
                canceled_order = self.asks[price].orders[order_id]
                self.asks[price].remaining_size -= canceled_order.remaining_size
                if self.asks[price].remaining_size <= 0:
                    del self.asks[price]
                del self.orders[order_id]
    
    def update_orderbook(self):
        for price, limit_orders in list(self.bids.items()):
            limit_orders.orders = [order for order in limit_orders.orders if order.remaining_size > 0.0]
            if not limit_orders.orders:
                del self.bids[price]

        for price, limit_orders in list(self.asks.items()):
            limit_orders.orders = [order for order in limit_orders.orders if order.remaining_size > 0.0]
            if not limit_orders.orders:
                del self.asks[price]

        matching_prices = sorted(set(self.bids.keys()) & set(self.asks.keys()))

        for price in matching_prices:
            bid_limit = self.bids[price]
            ask_limit = self.asks[price]

            while bid_limit.orders and ask_limit.orders:
                bid_order = bid_limit.orders[0]
                ask_order = ask_limit.orders[0]

                if bid_order.remaining_size <= ask_order.remaining_size:
                    ask_order.remaining_size -= bid_order.remaining_size
                    bid_limit.orders.pop(0)
                    if ask_order.remaining_size == 0.0:
                        ask_limit.orders.pop(0)
                else:
                    bid_order.remaining_size -= ask_order.remaining_size
                    ask_limit.orders.pop(0)
                    if bid_order.remaining_size == 0.0:
                        bid_limit.orders.pop(0)
                        break

        for price, limit_orders in list(self.bids.items()):
            limit_orders.orders = [order for order in limit_orders.orders if order.remaining_size > 0.0]
            if not limit_orders.orders:
                del self.bids[price]

        for price, limit_orders in list(self.asks.items()):
            limit_orders.orders = [order for order in limit_orders.orders if order.remaining_size > 0.0]
            if not limit_orders.orders:
                del self.asks[price]
    def get_market_depth(self):
        self.update_orderbook()
        bids = [(price, sum(order.remaining_size for order in limit.orders)) for price, limit in self.bids.items()]
        asks = [(price, sum(order.remaining_size for order in limit.orders)) for price, limit in self.asks.items()]
        return bids, asks
    
    def save_market_depth_plot(self, filename):
        bids, asks = self.get_market_depth()
        bid_prices, bid_volumes = zip(*bids) if bids else ([], [])

        if asks:
            ask_prices, ask_volumes = zip(*asks)
        else:
            ask_prices, ask_volumes = [], []

        plt.figure(figsize=(10, 6))

        plt.barh(bid_prices, bid_volumes, color='blue', alpha=0.6, label='Bids')

        if ask_prices and ask_volumes:
            plt.barh(ask_prices, ask_volumes, color='red', alpha=0.6, label='Asks')

        plt.ylabel('Price')
        plt.xlabel('Base Currency Amount')
        plt.title('Market Depth')
        plt.legend()
        plt.grid(True)

        plt.savefig(filename)  
        plt.close()  
