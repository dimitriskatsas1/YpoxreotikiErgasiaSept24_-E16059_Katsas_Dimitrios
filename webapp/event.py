from pymongo import MongoClient
from bson.objectid import ObjectId

class event:
    def __init__(self, id, title, description, day, time, place, type, creator):
        self.id = id
        #Όνομα Εκδήλωσης: Ένα όνομα ως τίτλος της εκδήλωσης.
        self.title = title
        #Περιγραφή Εκδήλωσης: Μία περιγραφή που θα μπορεί να δώσει ο χρήστης ως επιπλέων πληροφορίες της εκδήλωσης.
        self.description = description
        #Ημερομηνία Εκδήλωσης: Η ημέρα που θα λάβει μέρος η εκδήλωση.
        self.day = day
        #Ώρα Εκδήλωσης: Η ώρα που θα λάβει μέρος η εκδήλωση.	
        self.time = time	
        #Μέρος Εκδήλωσης: Το σημείο στο οποίο θα λάβει μέρος η εκδήλωση.
        self.place = place
        #Τύπος Εκδήλωσης: Ο τύπος της εκδήλωσης ο οποίος θα είναι ένας από τους εξής: «meet up», «conference», «party», «festival».
        self.type = type
        self.creator = creator
        self.participants = []
    def addParticipant(self, user, status):
        self.participants.append({"user":user, "status":status})
	
    def checkParticipant(self, user):
        for p in self.participants:
            if p.user == user:
                return p
        return None
   
    def to_dict(self):
        d = dict({"title": self.title,"description": self.description,"day": self.day,"time": self.time,"place": self.place,"type": self.type,"creator": self.creator,"participants": self.participants})
        return d
    
    
    @staticmethod
    def from_dict(data):
        """Δημιουργεί ένα αντικείμενο Event από ένα λεξικό που έχει ανακτηθεί από τη βάση δεδομένων."""
        Event = event(data["_id"], data["title"], data["description"], data["day"], data["time"], data["place"], data["type"], data["creator"])
        Event.participants = data["participants"]
        return Event

    @staticmethod
    def get_db_collection():
        """Επιστρέφει τη συλλογή της MongoDB για τα events."""
        client = MongoClient("mongodb://mongodb:27017/")
        db = client["eventsdb"]
        return db["events"]

    def save_to_db(self):
        """Αποθηκεύει το αντικείμενο Event στη MongoDB."""
        collection = self.get_db_collection()
        collection.insert_one(self.to_dict())

    @staticmethod
    def delete_from_db(id):
        """Διαγράφει ένα event από τη MongoDB βάσει του τίτλου."""
        collection = event.get_db_collection()
        collection.delete_one({"_id": ObjectId(id)})

    @staticmethod
    def update_in_db(id, update_fields):
        print(update_fields)
        """Ενημερώνει ένα event στη MongoDB βάσει του τίτλου."""
        collection = event.get_db_collection()
        print(ObjectId(id))
        collection.update_one({"_id": ObjectId(id)}, {"$set": update_fields})

    @staticmethod
    def get_from_db(id):
        collection = event.get_db_collection()
        data = collection.find_one({"_id": ObjectId(id)})
        if data:
            return event.from_dict(data)
        return None
    
    @staticmethod
    def get_user_event_from_db(user):
        collection = event.get_db_collection()
        lst = []
        for d in collection.find():
            if d['creator']==user:
                lst.append(d)
        return lst
    @staticmethod
    def get_user_parts_event_from_db(user):
        collection = event.get_db_collection()
        #data = collection.find({"creator": user})
        lst = []
        for d in collection.find():
            for e in d['participants']:
                if e['user'] == user:
                    lst.append(d)
                    break;
        return lst

