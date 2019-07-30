import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('service.json', scope)
client = gspread.authorize(creds)

doc = client.open_by_url('https://docs.google.com/spreadsheets/d/1n3PlGK2lqQYJng2PTO9MBuiVnqzP8RigzzooCOiZHYw/edit#gid=64379218')

sheets = doc.worksheets()
sheet = sheets[-2]

thur = sheet.find("Thursday")
thur_col = sheet.get_all_values()

thur_col = thur_col[2:-1]

test = [item for item in thur_col if 'Social' not in item[0]]

#for x in test:
#    print(x[0]) 



def get_not_set_raiders():
    # Returns a list of raiders who have not set their Thursday and Sunday statuses yet
    #

    # Find locations of mandatory raid signups
    thur = sheet.find("Thursday")
    sun = sheet.find("Sunday")

    all_raiders = [r for r in sheet.get_all_values()[2:-1] if '(Social)' not in r[0]]

    # Check if raider has set thursday and sunday
    #print(thur.col)

    not_set_raiders = [r for r in all_raiders if r[thur.col-1] == 'Not Set' or r[sun.col-1] == 'Not Set']

    
    return [x[0] for x in not_set_raiders]



