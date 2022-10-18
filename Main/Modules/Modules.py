def GetUserInfo(user, db):
    udata = db.child("/users/ "+user['localId']).get(user['idToken'])
    data = []
    for user_data in udata.each():
        info = [user_data.key(), user_data.val()]
        data.append(info)
    data = dict(data)
    return data

def CreateUser(user):
    data = {"users/ " +user["localId"]: {
            "email_id": user['']
        }
    }