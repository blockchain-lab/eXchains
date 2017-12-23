from enum import Enum
import operator


class OrderBook:
    def __init__(self):
        self.askList = []
        self.bidList = []

    def add_order(self, order):
        if isinstance(order, Ask):
            # print("You've added an Ask order ")
            self.askList.append(order)
        elif isinstance(order, Bid):
            # print("You've added an Bid order " )
            self.bidList.append(order)
        elif isinstance(order, list):
            for orders in order[:]:
                # print("Oooeh adding a thing from the list")
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
            ask_volume = 0
            sub_ask_list.clear()
            current_ask_price = ask_list[0].price
            while len(ask_list) > 0 and ask_list[0].price == current_ask_price:
                order = ask_list[0]
                ask_volume += order.volume
                sub_ask_list.append(order)        # Create a sub list with all the orders that have the same price
                # orderbook.remove_order(order)     # Remove them from the orderbook, and ask _list untouched and
                ask_list.remove(order)            # partially fulfilled orders will be placed back later

            bid_volume = 0
            sub_bid_list.clear()
            current_bid_price = bid_list[0].price
            while len(bid_list) > 0 and bid_list[0].price == current_bid_price:
                order = bid_list[0]
                bid_volume += order.volume
                sub_bid_list.append(order)        # Create a sub list with all the order that overlap in price
                # orderbook.remove_order(order)     # Remove them from the orderbook, and bid _list untouched and
                bid_list.remove(order)            # partially fulfilled orders will be placed back later

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
            for entry in bigger_list:
                if isinstance(entry, Ask):
                    order_type = OrderType.ASK
                else:
                    order_type = OrderType.BID

                trading_volume = round(entry.volume / remaining_big_volume * remaining_small_volume)

                remaining_big_volume -= entry.volume
                remaining_small_volume -= trading_volume
                entry.volume -= trading_volume
                self.trade_list.append(Transaction(entry.uuid, entry.order_id, order_type, trading_volume, price))
                if entry.volume == 0:
                    bigger_list.remove(entry)   # If an order is fullfilled get rid of it
                else:
                    place_back_buffer.append(entry)

            # If there are any unfullfilled orders, and clear, so it's empty for the next round
            if len(place_back_buffer) != 0:
                if isinstance(place_back_buffer[0], Ask):   # They're either all asks or all bids
                    ask_list = sorted(place_back_buffer, key=operator.attrgetter('price', 'volume', 'timestamp'), reverse=True) + ask_list
                else:
                    bid_list = sorted(place_back_buffer, key=operator.attrgetter('price', 'volume', 'timestamp'), reverse=False) + bid_list
                place_back_buffer.clear()

            for entry in smaller_list:
                if isinstance(entry, Ask):
                    order_type = OrderType.ASK
                else:
                    order_type = OrderType.BID
                self.trade_list.append(Transaction(entry.uuid, entry.order_id, order_type, entry.volume, price))

        print("No matches can be made anymore")
        orderbook.add_order(ask_list)
        orderbook.add_order(bid_list)
        return self.trade_list

    def merge(self,orderbook: OrderBook):
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
                    i += i
            merged_orders.add_order(Ask(self.uuid, self.order_id, volume, current_price, 2))
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
                    i += i
            merged_orders.add_order(Bid(self.uuid,self.order_id, volume,current_price, 2))
            self.cross_reference_list.append(cross_reference)
            self.order_id += 1

        return merged_orders
