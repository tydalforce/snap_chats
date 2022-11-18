import json, os, sys
from html import unescape


'''
Downloaded data from SnapChat isn't terribly accessible - good luck figuring out chat history
This will schlep through it all and output a proper chat history log

Downloads unfortunately don't contain saved snap/image/graphic stuff
so there will be placeholders...
'''

# enter the full path to the extracted snapchat archive
# this should be the folder containing the html and json directories
# This is the only thing that should need modification at runtime
sc_archive_root = os.path.abspath(os.getenv('HOME') + '/Documents/snapchat_archives/mydata~1662430041936')


# Location of converted files
outdir = os.path.abspath(sc_archive_root + '/coverted')

# files from archive
json_dir = os.path.abspath(sc_archive_root + '/json')
j_account = '/account.json'
j_chat_history = '/chat_history.json'
j_friends = '/friends.json'
j_snap_history = '/snap_history.json'

if not os.path.isdir(outdir):
    # Make the output directory if not present
    os.makedirs(outdir)

# # stylecss is just the <style>...</style> stolen from the snap download html files
# # TODO - less halfassed way to prettify
# # This css is slightly modified for output readability
with open('./style.txt') as styles:
    stylecss = styles.readlines()

# Get some info about you!
with open(os.path.abspath(json_dir + j_account)) as accountfyle:
    my_account_json = json.load(accountfyle)

my_username = my_account_json['Basic Information']['Username']
my_display_name = my_account_json['Basic Information']['Name']
my_start_date = my_account_json['Basic Information']['Creation Date']

# Get friends
with open(os.path.abspath(json_dir + j_friends)) as friendsfyle:
    my_friends_json = json.load(friendsfyle)

# Build a dictionary of friend dictionaries, each dict has info about the friend
contacts = dict()
for friend in my_friends_json['Friends']:
    contacts[friend['Username']] = dict()
    contacts[friend['Username']]['type'] = 'friend'
    contacts[friend['Username']]['username'] = friend['Username']
    contacts[friend['Username']]['displayname'] = friend['Display Name']
    contacts[friend['Username']]['added'] = friend['Creation Timestamp']
    contacts[friend['Username']]['modified'] = friend['Last Modified Timestamp']
    contacts[friend['Username']]['source'] = friend['Source']

# also friend requesteds
for friend in my_friends_json['Friend Requests Sent']:
    contacts[friend['Username']] = dict()
    contacts[friend['Username']]['type'] = 'pending'
    contacts[friend['Username']]['username'] = friend['Username']
    if 'Display Name' not in friend or friend['Display Name'] in (None, ''):
        contacts[friend['Username']]['displayname'] = friend['Username']
    else:
        contacts[friend['Username']]['displayname'] = friend['Display Name']
    contacts[friend['Username']]['added'] = friend['Creation Timestamp']
    contacts[friend['Username']]['modified'] = friend['Last Modified Timestamp']
    contacts[friend['Username']]['source'] = friend['Source']

# and bitches you blocked
for friend in my_friends_json['Blocked Users']:
    contacts[friend['Username']] = dict()
    contacts[friend['Username']]['type'] = 'blocked'
    contacts[friend['Username']]['username'] = friend['Username']
    contacts[friend['Username']]['displayname'] = friend['Display Name']
    contacts[friend['Username']]['added'] = friend['Creation Timestamp']
    contacts[friend['Username']]['modified'] = friend['Last Modified Timestamp']
    contacts[friend['Username']]['source'] = friend['Source']

# Gone but not forgotten
for friend in my_friends_json['Deleted Friends']:
    contacts[friend['Username']] = dict()
    contacts[friend['Username']]['type'] = 'unfriended'
    contacts[friend['Username']]['username'] = friend['Username']
    contacts[friend['Username']]['displayname'] = friend['Display Name']
    contacts[friend['Username']]['added'] = friend['Creation Timestamp']
    contacts[friend['Username']]['modified'] = friend['Last Modified Timestamp']
    contacts[friend['Username']]['source'] = friend['Source']


for friend in my_friends_json['Hidden Friend Suggestions']:
    contacts[friend['Username']] = dict()
    contacts[friend['Username']]['type'] = 'hidden_suggestion'
    contacts[friend['Username']]['username'] = friend['Username']
    contacts[friend['Username']]['displayname'] = friend['Display Name']
    contacts[friend['Username']]['added'] = friend['Creation Timestamp']
    contacts[friend['Username']]['modified'] = friend['Last Modified Timestamp']
    contacts[friend['Username']]['source'] = friend['Source']

with open(os.path.abspath(json_dir + j_chat_history)) as chatfyle:
    my_chats_json = json.load(chatfyle)

chats = dict()


# TODO: The for loops below are all basically the same thing; function these maybe?
for message in my_chats_json['Received Saved Chat History']:
    msg_with = message['From']
    msg_type = message['Media Type']
    msg_text = message['Text']
    position = my_chats_json['Received Saved Chat History'].index(message)
    # Appending the index value of the message to the timestamp to hopefully avoid
    # two messages with the same person with the same timestamp from overwriting
    msg_time = message['Created'] + ' ' + str(position)
    if msg_with not in chats:
        chats[msg_with] = dict()
    chats[msg_with][msg_time] = dict()
    chats[msg_with][msg_time]['direction'] = 'From'
    chats[msg_with][msg_time]['time'] = message['Created']
    chats[msg_with][msg_time]['From'] = msg_with
    chats[msg_with][msg_time]['To'] = my_username
    chats[msg_with][msg_time]['type'] = msg_type
    chats[msg_with][msg_time]['text'] = unescape(msg_text)
    if msg_type not in ['TEXT']:
        chats[msg_with][msg_time]['text'] = '<font color="teal"><i>' + msg_type + '</i></font>  ' + unescape(msg_text)
    if msg_with not in contacts:
        contacts[msg_with] = dict()
        contacts[msg_with]['type'] = 'unknown'
        contacts[msg_with]['username'] = msg_with
        contacts[msg_with]['displayname'] = msg_with
        contacts[msg_with]['added'] = ''
        contacts[msg_with]['modified'] = ''
        contacts[msg_with]['source'] = 'unknown'

for message in my_chats_json['Sent Saved Chat History']:
    msg_with = message['To']
    msg_type = message['Media Type']
    msg_text = message['Text']
    position = my_chats_json['Sent Saved Chat History'].index(message)
    # Appending the index value of the message to the timestamp to hopefully avoid
    # two messages with the same person with the same timestamp from overwriting
    msg_time = message['Created'] + ' ' + str(position)
    if msg_with not in chats:
        chats[msg_with] = dict()
    chats[msg_with][msg_time] = dict()
    chats[msg_with][msg_time]['direction'] = 'To'
    chats[msg_with][msg_time]['time'] = message['Created']
    chats[msg_with][msg_time]['To'] = msg_with
    chats[msg_with][msg_time]['From'] = my_username
    chats[msg_with][msg_time]['type'] = msg_type
    chats[msg_with][msg_time]['text'] = unescape(msg_text)
    if msg_type not in ['TEXT']:
        chats[msg_with][msg_time]['text'] = '<font color="teal"><i>' + msg_type + '</i></font>  ' + unescape(msg_text)


with open(os.path.abspath(json_dir + j_snap_history)) as snapfyle:
    my_snaps_json = json.load(snapfyle)

for message in my_snaps_json['Received Snap History']:
    msg_with = message['From']
    msg_type = message['Media Type']
    msg_text = msg_type
    position = my_snaps_json['Received Snap History'].index(message)
    # Appending the index value of the message to the timestamp to hopefully avoid
    # two messages with the same person with the same timestamp from overwriting
    msg_time = message['Created'] + ' ' + str(position)
    if msg_with not in chats:
        chats[msg_with] = dict()
    chats[msg_with][msg_time] = dict()
    chats[msg_with][msg_time]['direction'] = 'From'
    chats[msg_with][msg_time]['time'] = message['Created']
    chats[msg_with][msg_time]['From'] = msg_with
    chats[msg_with][msg_time]['To'] = my_username
    chats[msg_with][msg_time]['type'] = msg_type
    chats[msg_with][msg_time]['text'] = unescape(msg_text)

for message in my_snaps_json['Sent Snap History']:
    msg_with = message['To']
    msg_type = message['Media Type']
    msg_text = msg_type
    position = my_snaps_json['Sent Snap History'].index(message)
    # Appending the index value of the message to the timestamp to hopefully avoid
    # two messages with the same person with the same timestamp from overwriting
    msg_time = message['Created'] + ' ' + str(position)
    if msg_with not in chats:
        chats[msg_with] = dict()
    chats[msg_with][msg_time] = dict()
    chats[msg_with][msg_time]['direction'] = 'To'
    chats[msg_with][msg_time]['time'] = message['Created']
    chats[msg_with][msg_time]['To'] = msg_with
    chats[msg_with][msg_time]['From'] = my_username
    chats[msg_with][msg_time]['type'] = msg_type
    chats[msg_with][msg_time]['text'] = unescape(msg_text)

chats_sorted=dict()
for someone in chats:
    if someone not in chats_sorted:
        chats_sorted[someone] = dict()
    chats_sorted[someone] = dict(sorted(chats[someone].items()))

for someone in chats_sorted:
    contact_fyle = os.path.abspath(outdir + '/' + someone + '.html')

    # This is pretty janky don't look too close
    outFyle = open(contact_fyle, 'w')
    outFyle.write('''
    <!DOCTYPE html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    ''')
    outFyle.write(('    <title>' + someone + '</title> \n'))

    #outFyle.write(stylecss)
    for line in stylecss:
        outFyle.write(line)
    outFyle.write('</head><html><body> \n')
    outFyle.write('''<table style="table-layout: auto;">
<tbody><tr><th style="white-space: nowrap; overflow: hidden;">
''')
    outFyle.write('<div class="rightpanel"><h1>Chat History with: ' + someone + '</h1><p></p> \n')
    outFyle.write('<li align="left"><b>Display Name:</b> ' + contacts[someone]['displayname'] + '</li>\n')
    outFyle.write('<li align="left"><b>Username:</b> ' + contacts[someone]['username'] + '</li>\n')
    outFyle.write('<li align="left"><b>Added On:</b> ' + contacts[someone]['added'] + '</li>\n')
    # outFyle.write('<li align="left"><b>Modified::</b> ' + contacts[someone]['modified'] + '</li>\n')
    outFyle.write('<li align="left"><b>Contact Type:</b> ' + contacts[someone]['type'] + '</li>\n')
    # outFyle.write('<li align="left"><b>Source:</b> ' + contacts[someone]['source'] + '</li>\n')
    outFyle.write('</br></br> \n')
    outFyle.write('''<table style="table-layout: auto;">
<tbody><tr><th style="white-space: nowrap; overflow: hidden;"> \n''')
    for timestamp in chats_sorted[someone]:
        message = chats_sorted[someone][timestamp]
        color = 'blue'
        if message['direction'] == 'To':
            color = 'red'
        outFyle.write( '<font color="' + color + '">' + message['From'] + '</font><font color="grey"> - ' + message['time']  + ':</font></br>\n')
        outFyle.write('<font color="black">' + message['text'] + '</font><br>\n')

    outFyle.write('</tbody></html>\n')
    outFyle.close()
print('Done!')