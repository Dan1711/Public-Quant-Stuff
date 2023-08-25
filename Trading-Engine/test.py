from market import TradingPair, BidOrAsk
from engine import MatchingEngine
from orderbook import Order
import random

def liquidity_simulation():

    """For this simulation we used SOL/USD market and set probability of cancelation @ 20%"""

    
    matching_engine = MatchingEngine()
    pair = TradingPair("SOL", "USD")
    matching_engine.add_new_market(pair)

    def limit_bid(pair, size, price):
        limit_bid_order = Order(BidOrAsk.Bid, size)
        matching_engine.place_limit_order(pair, price, limit_bid_order)

    def limit_ask(pair, size, price):
        limit_ask_order = Order(BidOrAsk.Ask, size)
        matching_engine.place_limit_order(pair, price, limit_ask_order)

    def market_order(pair, side, size):
        market_order = Order(BidOrAsk.Bid if side == "buy" else BidOrAsk.Ask, size)
        matching_engine.place_market_order(pair, market_order)

    def cancel_limit(pair, order_id, side):
        if side == BidOrAsk.Bid or side == BidOrAsk.Ask:
            matching_engine.cancel_limit_order(pair, order_id, side)
        else:
            print("Invalid side provided for cancellation.")

    def iceberg(pair, iteration):
        matching_engine.view_iceberg(pair)
        matching_engine.orderbooks[pair].save_market_depth_plot(f"market_depth_{iteration}.png")

    side_to_cancel = None  
    for iteration in range(10):
        limit_side = random.choice([BidOrAsk.Bid, BidOrAsk.Ask])
        limit_amount = random.randint(10, 50)
        limit_price = round(random.uniform(20, 25), 2)
        limit_order = Order(limit_side, limit_amount)
        if limit_side == BidOrAsk.Bid:
            limit_bid(pair, limit_order.remaining_size, limit_price)
        else:
            limit_ask(pair, limit_order.remaining_size, limit_price)
        iceberg(pair, iteration)

        if random.random() < 0.2: 
            orders_to_cancel = matching_engine.orderbooks[pair].bids if limit_side == BidOrAsk.Bid else matching_engine.orderbooks[pair].asks
            if orders_to_cancel:
                price_to_cancel = random.choice(list(orders_to_cancel.keys()))
                if price_to_cancel in orders_to_cancel:
                    order_to_cancel = random.choice(orders_to_cancel[price_to_cancel].orders)
                    cancel_limit(pair, order_to_cancel.order_id, limit_side)
            iceberg(pair, iteration)

    for iteration in range(10, 200):
        is_limit_order = random.choice([True, False])

        if is_limit_order:
            limit_side = random.choice([BidOrAsk.Bid, BidOrAsk.Ask])
            limit_amount = random.randint(1, 200)
            limit_price = round(random.uniform(20, 25), 2)
            limit_order = Order(limit_side, limit_amount)

            bids, asks = matching_engine.orderbooks[pair].get_market_depth()
            total_bid_liquidity = sum(size for _, size in bids)
            total_ask_liquidity = sum(size for _, size in asks)

            if (limit_side == BidOrAsk.Bid and total_ask_liquidity > limit_amount) or \
                    (limit_side == BidOrAsk.Ask and total_bid_liquidity > limit_amount):
                if limit_side == BidOrAsk.Bid:
                    limit_bid(pair, limit_order.remaining_size, limit_price)
                else:
                    limit_ask(pair, limit_order.remaining_size, limit_price)
        else:
            market_side = random.choice([BidOrAsk.Bid, BidOrAsk.Ask])
            market_amount = random.randint(1, 200)
            if market_side == BidOrAsk.Bid:
                market_order(pair, "buy", market_amount)
            else:
                market_order(pair, "sell", market_amount)

        if random.random() < 0.2:  
            if is_limit_order:
                side_to_cancel = limit_side
            else:
                side_to_cancel = market_side

            if side_to_cancel == BidOrAsk.Bid:
                orders_to_cancel = matching_engine.orderbooks[pair].bids
            else:
                orders_to_cancel = matching_engine.orderbooks[pair].asks

            if orders_to_cancel:
                price_to_cancel = random.choice(list(orders_to_cancel.keys()))
                if price_to_cancel in orders_to_cancel:
                    order_to_cancel = random.choice(orders_to_cancel[price_to_cancel].orders)
                    cancel_limit(pair, order_to_cancel.order_id, side_to_cancel)
        iceberg(pair, iteration)

