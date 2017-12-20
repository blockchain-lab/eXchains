import MatchMaker
import operator

book = MatchMaker.OrderBook()

koop = MatchMaker.Ask(1,0,61,70,1)

koop1 = MatchMaker.Ask(2,0,50,50,1)
koop2 = MatchMaker.Ask(3,0,40,35,1)
koop3 = MatchMaker.Ask(4,0,45,35,1)


verkoop = MatchMaker.Bid(0,1,20,29,1)
verkoop1 = MatchMaker.Bid(0,2,47,31,1)

verkoop2 = MatchMaker.Bid(0,3,43,32,1)
verkoop3 = MatchMaker.Bid(0,4,33,31,1)


kooplijst = [koop, koop1, koop2, koop3, verkoop, verkoop1, verkoop2, verkoop3]
# kooplijst = [koop, verkoop, verkoop1]

book.add_order(kooplijst)

engine = MatchMaker.Matcher()

print("Order book:", book.getasklist() + book.getbidlist())
print("Trade book:", engine.match(book))
print("Order book:", book.getasklist() + book.getbidlist())



