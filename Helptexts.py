

class Helptexts:
    def __init__(self):
        self.Ping = 'Pings bot to see if it is alive, it will return some info about its current status'
        self.changeTimes = 'Changes the current times when notifications should be sent. Times should be on HH:MM format and separated by spaces. Example usage:\n.changeTimes 09:00 12:00 15:00'

        self.changeDays = 'Changes the current days when notifications should be sent. Dates should be integers from 0-6 that represent the days of the week. Example usage:\n.changeDays 1 2 3\n\nThis will notify on tue/wed/thur'

        self.Log = 'Sends log information from systemctl service on Raspberry. Mostly used by Loriell for logging purposes.'




