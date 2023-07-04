import sys
import Pyro4


@Pyro4.expose
class Seller:
    def __init__(self, serverURI):
        self.serverProxy = Pyro4.Proxy(serverURI)

    def createAuction(self, itemName, startingPrice, reservePrice, duration):
        creation = self.serverProxy.createAuction(itemName, startingPrice, reservePrice, duration)
        print(creation)

    def closeAuction(self, auctionID):
        closure = self.serverProxy.closeAuction(auctionID)
        print(closure)

    def getActiveAuctions(self):
        result = self.serverProxy.sellerGetActiveAuctions()
        print(result)

    def announceWinner(self, auctionID):
        announcement = self.serverProxy.announceWinner(auctionID)
        print(announcement)



from Seller import Seller
def main():
    uri = input("Enter the Pyro uri of the Auctioning Server: ")
    seller = Seller(uri)
    print("1. Create Auction\n2. Close Auction\n3. View Active Auctions\n4. Announce an auction winner\n 5.Exit")
    choice = int(input("Enter choice: "))
    if choice == 1:
        item_name = str(input("Enter item name: "))
        starting_price = float(input("Enter starting price: "))
        reserve_price = float(input("Enter reserve price: "))
        duration = int(input("Enter duration (in hours): "))
        seller.createAuction(item_name, starting_price, reserve_price, duration)
    elif choice == 2:
        auction_ID = input("Enter the ID of the auction you would like to close: ")
        seller.closeAuction(auction_ID)
    elif choice == 3:
        seller.getActiveAuctions()
    elif choice == 4:
        auctionID = int(input("Enter the ID of the auction for which you want to announce the winner: "))
        seller.announceWinner(auctionID)
    elif choice == 5:
        sys.exit()









if __name__ == '__main__':
    with Pyro4.Daemon() as daemon:
        seller = Seller(None)
        ns = Pyro4.locateNS()
        uri = daemon.register(seller)
        ns.register("example.seller", uri)
        main()
