from enum import Enum
from typing import List
import operator
import datetime

# This module's purpose is to perform matchmaking between asks and bids. The algorithm first matches the highers buyer
# With the lowest seller. If there are multiple buyer/sellers at the same price point the order or matched in decreasing
# volume. The reason for this is to reward behavior that generates flexibility, if people are willing to buy for higher
# and sell for lower there is a bigger chance on matches being made. When there is an sur plus of asks or bids, the
# client offering for the price that generates the most flexibility will get priority as they are contributing to more
# matches being made.

# Use of this module
# 1) Create an instance of the orderbook class
# 2) Add orders to the order book
# 3) create an instance of the Matcher class
# 4) run matcher.match(orderbook)

# optional (only if orders will be passed upwards):
# 5) use matcher.merge(orderbook) to create a new orderbook
# 6) pass these orders to another level and repeat from step 1
# 7) use the trades made from the higher level with the unmerge function to match remaining orders with extra-cluster trades
# 8) match.unmerge(trade_list_from_higher_level)

# For a new round clear everything and start again from step 1


class OrderBook:
    def __init__(self):
        self.askList = []
        self.bidList = []

    def add_order(self, order):
        if isinstance(order, Ask):
            self.askList.append(order)
        elif isinstance(order, Bid):
            self.bidList.append(order)
        elif isinstance(order, list):
            for orders in order[:]:
                self.add_order(orders)

    def remove_order(self, order):
        if isinstance(order, Ask):
            if order in self.askList:
                self.askList.remove(order)
        elif isinstance(order, Bid):
            if order in self.bidList:
                self.bidList.remove(order)
        elif isinstance(order, list):
            for orders in order[:]:
                self.remove_order(orders)

    def clear(self):
        self.askList.clear()
        self.bidList.clear()

    def getbidlist(self):
        return self.bidList

    def getasklist(self):
        return self.askList


class Ask:
    def __init__(self, uuid, order_id, volume, price, timestamp):
        self.uuid = uuid
        self.order_id = order_id
        self.volume = volume
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return "\nA(uuid: {}, orderid: {}, volume: {}, price: {}, timeStamp: {})".format(self.uuid, self.order_id,
                                                                                    self.volume, self.price,
                                                                                    self.timestamp)


class Bid:
    def __init__(self, uuid, order_id, volume, price, timestamp):
        self.uuid = uuid
        self.order_id = order_id
        self.volume = volume
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return "\nB(uuid: {}, orderid: {}, volume: {}, price: {}, timeStamp: {})".format(self.uuid, self.order_id,
                                                                                    self.volume, self.price,
                                                                                    self.timestamp)


class CrossReference:
    def __init__(self, uuid, order_id):
        self.uuid = uuid
        self.order_id = order_id
        self.orders = []


class Trades:
    transactions = []

    def addtransaction(self, transaction):
        self.transactions.append(transaction)

    def __repr__(self):
        result = ""
        for transaction in self.transactions:
            result.join("\nID: {}, Type: {}, Energy: {}, Price: {}\n".format(transaction.ID, transaction.type, transaction.energy,
                                                                   transaction.price))
        return result


class OrderType(Enum):
    ASK = 1
    BID = 2


class Transaction:
    def __init__(self, uuid, order_id, order_type: OrderType, volume, price):
        self.uuid = uuid
        self.order_id = order_id
        self.order_type = order_type
        self.volume = volume
        self.price = price

    def __eq__(self, other):
        return self.uuid == other.uuid and \
               self.order_id == other.order_id and \
               self.order_type == other.order_type and \
               self.volume == other.volume and \
               self.price == other.price

    def __ne__(self, other):
        return self.uuid != other.uuid or \
               self.order_id != other.order_id or \
               self.order_type != other.order_type or \
               self.volume != other.volume or \
               self.price != other.price

    def __repr__(self):
        return "\nT(uuid: {}, order id: {}, Type: {}, Volume: {}, Price: {})".format(self.uuid, self.order_id, self.order_type, self.volume,
                                                                self.price)


class Matcher:
    def __init__(self, uuid, order_id_start=0):
        self.uuid = uuid
        self.order_id = order_id_start
        self.trade_list = []
        self.cross_reference_list = []

    def match(self,orderbook: OrderBook):
        # todo: First sort for timestamp, then for price and volume in reverse (Works because of sort-stability)
        ask_list = sorted(orderbook.getasklist(), key=operator.attrgetter('price', 'volume', 'timestamp', 'uuid' , 'order_id'), reverse=True)
        bid_list = sorted(orderbook.getbidlist(), key=operator.attrgetter('price', 'volume', 'timestamp',  'uuid' , 'order_id'), reverse=False)
        orderbook.clear() # remove all orders from the orderbook, untouched or partially filled orders will put back later
        self.trade_list.clear()

        if len(ask_list)==0 or len(bid_list)==0:
            return []

        sub_ask_list = []
        sub_bid_list = []

        place_back_buffer = []

        while len(ask_list) != 0 and len(bid_list) != 0 and ask_list[0].price >= bid_list[0].price:
            # Create 2 lists if there are multiple orders at the same price (one for bid, one for ask)
            ask_volume = 0
            sub_ask_list.clear()
            current_ask_price = ask_list[0].price
            while len(ask_list) > 0 and ask_list[0].price == current_ask_price:
                order = ask_list[0]
                ask_volume += order.volume      # Keep track of the total ask volume for this price
                sub_ask_list.append(order)      # Create a sub list with all the orders that have the same price
                ask_list.remove(order)          # Temporary remove from the ask list (Placed back if not full filled)

            bid_volume = 0
            sub_bid_list.clear()
            current_bid_price = bid_list[0].price
            while len(bid_list) > 0 and bid_list[0].price == current_bid_price:
                order = bid_list[0]
                bid_volume += order.volume      # keep track of the total bid volume for this price
                sub_bid_list.append(order)      # Create a sub list with all the order that overlap in price
                bid_list.remove(order)          # Temporary remove from the ask list (Placed back if not full filled)

            if bid_volume > ask_volume:
                bigger_list = sub_bid_list
                smaller_list = sub_ask_list
                remaining_big_volume = bid_volume
                remaining_small_volume = ask_volume
            else:
                bigger_list = sub_ask_list
                smaller_list = sub_bid_list
                remaining_big_volume = ask_volume
                remaining_small_volume = bid_volume

            price = round((sub_ask_list[0].price + sub_bid_list[0].price)/2)

            # spread out the smaller volume pro rata over the bigger amount
            while len(bigger_list) > 0:
                entry = bigger_list[0]
                if isinstance(entry, Ask):
                    order_type = OrderType.ASK.value
                else:
                    order_type = OrderType.BID.value

                trading_volume = round(entry.volume / remaining_big_volume * remaining_small_volume)

                remaining_big_volume -= entry.volume
                remaining_small_volume -= trading_volume
                entry.volume -= trading_volume
                self.trade_list.append(Transaction(entry.uuid, entry.order_id, order_type, trading_volume, price))

                if entry.volume != 0:
                    place_back_buffer.append(entry)
                bigger_list.pop(0)  # If an order is full filled get rid of it


            # If there are any unfullfilled orders, and clear, so it's empty for the next round
            if len(place_back_buffer) != 0:
                if isinstance(place_back_buffer[0], Ask):   # They're either all asks or all bids
                    ask_list = sorted(place_back_buffer, key=operator.attrgetter('price', 'volume', 'timestamp'), reverse=True) + ask_list
                else:
                    bid_list = sorted(place_back_buffer, key=operator.attrgetter('price', 'volume', 'timestamp'), reverse=False) + bid_list
                place_back_buffer.clear()

            for entry in smaller_list:
                if isinstance(entry, Ask):
                    order_type = OrderType.ASK.value
                else:
                    order_type = OrderType.BID.value
                self.trade_list.append(Transaction(entry.uuid, entry.order_id, order_type, entry.volume, price))

        orderbook.add_order(ask_list)
        orderbook.add_order(bid_list)
        return self.trade_list

    def merge(self, orderbook: OrderBook):
        # This function will create a new order book with the remaining orders. It will combine multiple orders of the
        # same price and keep track of the corresponding original order and uuid. All the orders in the order book will
        # be linked to the cluster id and then returned so they can be passed on to a higher level.

        merged_orders = OrderBook()

        ask_list = orderbook.getasklist()
        bid_list = orderbook.getbidlist()
        while len(ask_list) != 0:

            volume = 0
            current_price = ask_list[0].price
            i = 0

            cross_reference = CrossReference(self.uuid, self.order_id)

            while i < len(ask_list):
                if ask_list[i].price == current_price:
                    cross_reference.orders.append((ask_list[i].uuid, ask_list[i].order_id))
                    volume += ask_list[i].volume
                    ask_list.pop(i)
                else:
                    i += 1
            merged_orders.add_order(Ask(self.uuid, self.order_id, volume, current_price, str(datetime.datetime.now())))
            self.cross_reference_list.append(cross_reference)
            self.order_id += 1

        while len(bid_list) != 0:

            volume = 0
            current_price = bid_list[0].price
            i = 0
            cross_reference = CrossReference(self.uuid, self.order_id)
            while i < len(bid_list):
                if bid_list[i].price == current_price:
                    cross_reference.orders.append((bid_list[i].uuid, bid_list[i].order_id))
                    volume += bid_list[i].volume
                    bid_list.pop(i)
                else:
                    i += 1
            merged_orders.add_order(Bid(self.uuid,self.order_id, volume,current_price, 2))
            self.cross_reference_list.append(cross_reference)
            self.order_id += 1

        return merged_orders

    def unmerge(self, orderbook: OrderBook, trades: List[Transaction]):
        # This functions accepts a list of trades from a higher cluster and then link the trades made by a higher level
        # to the remaining open orders in its own order book. This is done by using the self.cross_reference_list, Which
        # contains a uuid and order id (that was send to the higher cluster) among with a list of the order id's of the
        # original id's it used to create the new order.

        while len(trades) != 0:
            while len(self.cross_reference_list):
                pass
                # Find the merged order matching the trade in self.cross_reference_list
                # self.cross_reference_list[0].orders is a list consisting of dupples of uuid and order id
                # 1) Take all the mentioned orders from the list -> sum the volume
                # 2) Do the pro rata splitting out and create trades.
                # 3) check for none-zero volumes and add them back as orders.
