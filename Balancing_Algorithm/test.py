import MatchMaker
import operator

book = MatchMaker.OrderBook()
koop = MatchMaker.Ask(0,0,20,34)
koop1 = MatchMaker.Ask(0,0,50,32)
koop2 = MatchMaker.Ask(0,0,40,35)
koop3 = MatchMaker.Ask(0,0,45,35)


verkoop = MatchMaker.Bid(0,1,32,29)
verkoop1 = MatchMaker.Bid(0,1,47,31)
verkoop2 = MatchMaker.Bid(0,1,43,33)
verkoop3 = MatchMaker.Bid(0,1,33,31)


kooplijst = [koop, koop1, koop2, koop3, verkoop, verkoop1, verkoop2, verkoop3]

book.addorder(kooplijst)

engine = MatchMaker.Matcher()
engine.match(book)

# print(asklist.sort(key=MatchMaker.Ask.price))



