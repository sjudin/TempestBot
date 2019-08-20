import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_not_set_raiders():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('service.json', scope)
    client = gspread.authorize(creds)

    doc = client.open_by_url('https://docs.google.com/spreadsheets/d/1n3PlGK2lqQYJng2PTO9MBuiVnqzP8RigzzooCOiZHYw/edit#gid=64379218')

    sheets = doc.worksheets()
    # Assumes that the current sheet is the second to last one TODO: Make it more robust
    sheet = sheets[-2]

   # Returns a list of raiders who have not set their Thursday and Sunday statuses yet
    #

    # Find locations of mandatory raid signups
    thur = sheet.find("Thursday")
    sun = sheet.find("Sunday")

    all_raiders = [r for r in sheet.get_all_values()[2:-1] if '(Social)' not in r[0]]

    # Create list of raiders that have not set thursday and sunday
    not_set_raiders = [r for r in all_raiders if r[thur.col-1] == 'Not Set' or r[sun.col-1] == 'Not Set']
	if 'Artex' in not_set_raiders:
    not_set_raiders.remove('Artex')
    # Return list of names for all raiders who have not set attendance
    return ([x[0] for x in not_set_raiders], sheet.title)


if __name__ == '__main__':
    names, title = get_not_set_raiders()
    print(names, title)



