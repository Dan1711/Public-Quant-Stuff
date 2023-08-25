from orderbook import Orderbook
from market import  BidOrAsk 
from copy import deepcopy

class MatchingEngine:
    def __init__(self):
        self.orderbooks = {}
        
    
    def add_new_market(self, pair):
        self.orderbooks[pair] = Orderbook()
        
        print(f"Opening {pair.market()} market...")
        
    def place_limit_order(self, pair, price, order):
        if pair in self.orderbooks:
            orderbook = self.orderbooks[pair]
            orderbook.add_order(price, order)  
            base_currency = pair.base
            order_type = "buy" if order.bid_or_ask == BidOrAsk.Bid else "sell"
            print(f"Limit {order_type} placed @ ${price} for {order.remaining_size} {base_currency}.")

    def cancel_limit_order(self, pair, order_id, side):
        if pair in self.orderbooks:
            orderbook = self.orderbooks[pair]
            if side == BidOrAsk.Bid:
                limit_orders = orderbook.bids
            else:
                limit_orders = orderbook.asks

            price = None
            for level, limit in limit_orders.items():
                for order in limit.orders:
                    if order.order_id == order_id:
                        price = level
                        base_currency = pair.base
                        break
                if price is not None:
                    limit_orders[price].cancel_order(order_id)  
                    print(f"Limit order ({order_id}) cancelled for {order.remaining_size} {base_currency} successfully.")
                    break  
            else:
                print(f"No limit orders with the given order ID. Try again.")
        else:
            print(f"The market for the ({pair.market()}) pair does not exist")



    def place_market_order(self, pair, order):
        if pair in self.orderbooks:
            orderbook = self.orderbooks[pair]
            initial_remaining_size = order.remaining_size

            bids, asks = orderbook.get_market_depth()
            if order.bid_or_ask == BidOrAsk.Bid:
                bids.sort(key=lambda x: x[0], reverse=True)
            else:
                asks.sort(key=lambda x: x[0])

            total_bid_liquidity = sum(size for _, size in bids)
            total_ask_liquidity = sum(size for _, size in asks)

            order_type = "buy" if order.bid_or_ask == BidOrAsk.Bid else "sell"

            if total_bid_liquidity > 0 and (initial_remaining_size / total_bid_liquidity) > 0.25:
                print("Error, high price impact or not enough liquidity. Try again.")
                order.remaining_size = initial_remaining_size  

            elif total_ask_liquidity > 0 and (initial_remaining_size / total_ask_liquidity) > 0.25:
                print("Error, high price impact or not enough liquidity. Try again.")
                order.remaining_size = initial_remaining_size  

            else:
                orderbook_copy = deepcopy(orderbook)  
                orderbook_copy.fill_market_order(order)

                base_currency = pair.base
                filled = initial_remaining_size - order.remaining_size
                

                print(f"Market {order_type} filled for {filled} {base_currency}.")

                self.orderbooks[pair] = orderbook_copy  
        else:
            print(f"The market for the ({pair.market()}) pair does not exist")

    def view_iceberg(self, pair):
        orderbook = self.orderbooks.get(pair)
        if orderbook:
            bids, asks = orderbook.get_market_depth()
            print("Bids:", bids)
            print("Asks:", asks)