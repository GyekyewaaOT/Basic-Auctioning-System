import sys
import Pyro4

@Pyro4.expose
class Buyer:
    def __init__(self, serverURI):
        self.serverProxy = Pyro4.Proxy(serverURI)

    @Pyro4.expose
    def getActiveAuctions(self):
            print("Active Auctions: ")
            result = self.serverProxy.buyerGetActiveAuctions()
            print(result)

    @Pyro4.expose
    def placeBid(self, auctionID, bidderName, bidderPhoneNumber, bidAmount):
        placement = self.serverProxy.placeBid(auctionID, bidderName, bidderPhoneNumber, bidAmount)
        print(placement)


from Buyer import Buyer
def main():
    uri = input("Enter the Pyro uri of the Auctioning Server: ")
    buyer = Buyer(uri)
    print("1. View Active Auctions\n2. Place bid\n3. Exit")
    choice = int(input("Enter choice: "))
    if choice == 1:
        buyer.getActiveAuctions()
    elif choice == 2:
        auction_ID = input("Enter the ID of the auction you would like to place a bid on: ")
        bidder_name = input("Enter your first name: ")
        bidder_phonenumber = input("Enter your phone number: ")
        bid_amount = input("Enter the amount you would like to bid for the item: ")
        buyer.placeBid(auction_ID, bidder_name, bidder_phonenumber, bid_amount)
    elif choice == 3:
        sys.exit()


if __name__ == '__main__':
    with Pyro4.Daemon() as daemon:
        buyer = Buyer(None)
        ns = Pyro4.locateNS()
        uri = daemon.register(buyer)
        ns.register("example.buyer", uri)
        main()
