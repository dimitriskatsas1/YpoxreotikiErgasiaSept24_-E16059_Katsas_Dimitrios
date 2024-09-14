from pymongo import MongoClient


class user:
   def __init__(self,_id, firstname, lastname, email, type = "user", username = "", password = ""): 
        self.id = _id
            #όνομα
        self.firstname = firstname
            #επώνυμο
        self.lastname = lastname
            #email
        self.email = email
            #username
        self.username = username
            #password
        self.password = password
        self.type = type
   
   @staticmethod
   def login(username, password):
        collection = user.get_db_collection()
        lst = []
        for d in collection.find():
            print(d, " ", username, " ",password)
            if d['username'] == username:
                if d['password'] == password:
                    return (d['username'], d['firstname'], d['lastname'], d['email'], d['type'])
                else:
                    return (d['username'], "", "", "", None)
        return (None, "", "", "", "", None)
   

   def to_dict(self):
        d = dict({"firstname": self.firstname,"lastname": self.lastname,"email": self.email,"username": self.username,"password": self.password,"type": self.type})
        return d
    
    
   @staticmethod
   def from_dict(data):
        User = user(data["_id"], data["firstname"], data["lastname"], data["email"],data["type"],data["username"], data["password"])
        return User

   @staticmethod
   def get_db_collection():
        client = MongoClient("mongodb://mongodb:27017/")
        db = client["eventsdb"]
        return db["users"]

   def save_to_db(self):
        collection = self.get_db_collection()
        collection.insert_one(self.to_dict())

   @staticmethod
   def delete_from_db(title):
        collection = user.get_db_collection()
        collection.delete_one({"username": title})

   @staticmethod
   def update_in_db(title, update_fields):
        collection = user.get_db_collection()
        collection.update_one({"username": title}, {"$set": update_fields})

   @staticmethod
   def get_from_db(username=""):
        collection = user.get_db_collection()
        if username!="":
            data = collection.find_one({"username": username})
            if data:
                return user.from_dict(data)
        else:
            data = collection.find()
            if data:
                return list(data)
        return None
   
   @staticmethod
   def get_from_db_by_email(email=""):
        collection = user.get_db_collection()
        if email!="":
            data = collection.find_one({"email": email})
            if data:
                return user.from_dict(data)
        else:
            data = collection.find()
            if data:
                return list(data)
        return None
        
   def __str__(self):
        return self.username+" "+self.firstname+" "+self.lastname
    
