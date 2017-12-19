import MatchMaker

book = MatchMaker.OrderBook()
koop = MatchMaker.Ask(0,0,12,34)
koop1 = MatchMaker.Ask(0,0,12,34)
verkoop = MatchMaker.Bid(0,1,43,21)
kooplijst = [koop, verkoop, koop]

book.addorder(kooplijst)

asklist = book.getbidlist

#print(asklist)
print(kooplijst)



