import Pyro4
import random
import time
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("C:/Users/amaod/Downloads/auctiondb-46716-firebase-adminsdk-kwc86-5230deca7b.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

@Pyro4.expose
class AuctioningServer(object):
    def __init__(self):
        self.auctions = {}


    #Seller related methods
    @Pyro4.expose
    def createAuction(self, itemName, startingPrice, reservePrice, duration): #creates auction based on seller-provided details as shown in the parameters
        try:
            newAuction = {}
            auction_ID: int = random.randint(0, 9999999)  #randomly generated auction ID for unique identification of individual auctions
            auctionID = str(auction_ID)
            item_Name = str(itemName)
            starting_Price = str(startingPrice)
            reserve_Price = str(reservePrice)
            auction_Duration = str(duration)
            newAuction.update({u'ID': auctionID,        #unicode formatting to avoid type sensitivity challenges while being written onto DB
                               u'ItemName': item_Name,
                               u'StartingPrice': starting_Price,
                               u'ReservePrice': reserve_Price,
                               u'Duration': auction_Duration,
                               u'HighestBid': "0.0",
                               u'HighestBidID': None,
                               u'HighestBidderName': None,
                               u'Status': u'Active'})
            docRef = db.collection('Auctions').document(auctionID).set(newAuction)  #assignment of dictionary content to auction document in firestore DB
            success = docRef
            if success:
                self.countdown(auctionID, duration)
                return "Your auction has been created successfully!"
        except Exception as e:
            return "Error creating auction: ", e

    @Pyro4.expose
    def sellerGetActiveAuctions(self): #retrieves unexpired auctions
        try:
            docs = db.collection('Auctions').where("Status", "==", "Active").get()   #extracts auction documents whose 'Status' == 'Active'
            for doc in docs:
                docData = doc.to_dict()
                return docData
        except Exception as e:
            return "Error retrieving active auctions: ", e

    @Pyro4.expose
    def countdown(self, auctionID, duration):     #counts down from time auction was created
        try:
            seconds = duration * 60
            time.sleep(seconds)
            self.closeAuction(auctionID)
        except Exception as e:
            return "Error starting auction timer: ", e


    @Pyro4.expose
    def closeAuction(self, auctionID):     #closes auction either by countdown, or manually by seller
        try:
            docRef = db.collection('Auctions').document(auctionID)
            retRef = db.collection('Auctions').document(auctionID).get()
            status = retRef.get("Status")
            inactive = "Inactive"
            if status == "Inactive":
                return "This auction has already been closed"
            elif status == 'Active':
                docRef.update({u'Status': inactive})
                return "Your auction was found and has just been closed."
        except Exception as e:
            return "Error closing auction: ", e

    @Pyro4.expose
    def announceWinner(self, auctionID):  #allows seller to announce winner of their auction
        try:
            retRef = db.collection('Auctions').document(auctionID).get()
            status = retRef.get('Status')

            if status == "Inactive":
                winner = retRef.get('HighestBidderName')
                ID = retRef.get('HighestBidID')
                cash = retRef.get('HighestBid')
                if winner != "":
                    return "Congratulations, Auction" + auctionID + "was won by" + winner + ", Bid Number " + ID + "at a price of" + cash +"!"
                else:
                    return "Sorry, there was no winner for this auction!"
            elif status == "Active":
                return "The winner for this auction cannot be announced since the auction is not yet closed."
        except Exception as e:
            return "Error announcing winner: ", e




    # Buyer Related Methods
    @Pyro4.expose
    def buyerGetActiveAuctions(self):
        try:
            docs = db.collection('Auctions').where('Status', '==', 'Active').get()
            reserve = 'ReservePrice'
            winner = 'Winner'
            hb = 'HighestBid'
            hbn = 'HighestBidderName'
            hbi = 'HighestBidID'
            sp = 'StartingPrice'

            for doc in docs:
                docData = doc.to_dict()
                if reserve in docData:
                    del docData[reserve]
                if winner in docData:
                    del docData[winner]
                if hb in docData:
                    del docData[hb]
                if hbn in docData:
                    del docData[hbn]
                if hbi in docData:
                    del docData[hbi]
                if sp in docData:
                    del docData[sp]

            return docData
        except Exception as e:
            return "Error retrieving active auctions: ", e



    @Pyro4.expose
    def maxBid(self, auctionID, bidID, bidderName, bidAmount):
        try:
            auctionID = auctionID
            bidID = bidID
            bidAmount = float(bidAmount)
            doc = db.collection('Auctions').document(auctionID).get()
            docRef = db.collection('Auctions').document(auctionID)
            highestBid = doc.get('HighestBid')
            HighestBid = float(highestBid)
            if bidAmount > HighestBid:
                docRef.update({'HighestBid': bidAmount,
                               'HighestBidID': bidID,
                               'HighestBidderName': bidderName})
            else:
                pass
        except Exception as e:
            return "Error calculating highest bid: ", e


    @Pyro4.expose
    def placeBid(self, auctionID, bidderName, bidderPhoneNumber, bidAmount):
        try:
            newBid = {}
            bid_ID = random.randint(0, 9999999)
            bidID = str(bid_ID)
            auction_ID = str(auctionID)
            bidder_name = bidderName
            bidder_phonenumber = str(bidderPhoneNumber)
            bid_amount = str(bidAmount)
            doc = db.collection('Auctions').document(auction_ID).get()
            status = doc.get('Status')
            ID = doc.get('ID')
            resRef = doc.get('ReservePrice')
            if ID == auction_ID:
                bidamount = float(bid_amount)
                reserve = float(resRef)
                if bidamount > reserve:
                    newBid.update({u'BidID': bidID,
                                   u'AuctionID': auction_ID,
                                   u'BidderName': bidder_name,
                                   u'BidderPhoneNumber': bidder_phonenumber,
                                   u'BidAmount': bid_amount})
                    bid = db.collection('Bids').document(bidID)
                    bid.set(newBid)
                    db.collection('Bids').document(auction_ID)
                    docRef = db.collection('Auctions').document(auction_ID)
                    docRef.set({'Bids': newBid}, merge=True)
                    self.maxBid(auction_ID, bidID, bidder_name, bid_amount)
                    return "Congrats! Your bid has successfully been placed."
                else:
                    return "The bid amount is below the reserve price."
            else:
                return "The auction ID you entered does not exist."
        except Exception as e:
            return "Error placing bid: ", e




daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(AuctioningServer)
ns.register("example.auction", uri)
print("Auction Server URI: " + uri.asString())


print("Ready to auction.")
daemon.requestLoop()




