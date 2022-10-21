def GetUserInfo(user, db):
    udata = db.child("/users/ " + user['localId']).get(user['idToken'])
    data = []
    for user_data in udata.each():
        info = [user_data.key(), user_data.val()]
        data.append(info)
    data = dict(data)
    return data


def CreateUser(user, db):
    data = {"users/" + user['localId'].strip(): {
        "email_id": user['email'],
        "email_verified": False,
        "name": user["displayName"],
        "balance": 0,
        "banned": False,
        "phone_no": user["phoneNum"],
        "profile": ""
    }}
    db.update(data, user['idToken'])


def CreateUserVault(user, db, keys):
    data = {"vault/" + user["localId"]:
        {
            "2FA_KEY": keys['2FA'],
            "ENC_KEY": keys['ENC']
        }
    }
    db.push(data, user['idToken'])
