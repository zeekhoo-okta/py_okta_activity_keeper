class Session(object):
    def __init__(self, id, userId, login,
                 firstName=None, lastName=None, cronofyAccessToken=None, sfdcAccessToken=None):
        self.id = id
        self.userId = userId
        self.login = login
        self.firstName = firstName
        self.lastName = lastName
        self.cronofyAccessToken = cronofyAccessToken
        self.sfdcAccessToken = sfdcAccessToken