import json, os, cssutils
from html import unescape
from bs4 import BeautifulSoup

'''
Downloaded data from SnapChat isn't terribly accessible - good luck figuring out chat history
This will schlep through it all and output a proper chat history log

Downloads unfortunately don't contain saved snap/image/graphic stuff
so there will be placeholders...
'''

# enter the full path to the extracted snapchat archive
# this should be the folder containing the html and json directories
# This is the only thing that should need modification at runtime
sc_archive_root = os.path.abspath(os.getenv('HOME') + '/Downloads/mydata~1668727811069')
# Location of converted files
outdir = os.path.abspath(sc_archive_root + '/coverted')

print("Reading Snapchat archive from " + sc_archive_root)
print("Output files to: " + outdir)

# files from archive
json_dir = os.path.abspath(sc_archive_root + '/json')
j_account = '/account.json'
j_chat_history = '/chat_history.json'
j_friends = '/friends.json'
j_snap_history = '/snap_history.json'

if not os.path.isdir(outdir):
    # Make the output directory if not present
    os.makedirs(outdir)

global contects
global chats


def parse_friends(friends_json, type):
    for friend in friends_json:
        contacts[friend['Username']] = dict()
        contacts[friend['Username']]['type'] = type
        contacts[friend['Username']]['username'] = friend['Username']
        if 'Display Name' not in friend or friend['Display Name'] in (None, ''):
            contacts[friend['Username']]['displayname'] = friend['Username']
        else:
            contacts[friend['Username']]['displayname'] = friend['Display Name']
        contacts[friend['Username']]['added'] = friend['Creation Timestamp']
        contacts[friend['Username']]['modified'] = friend['Last Modified Timestamp']
        contacts[friend['Username']]['source'] = friend['Source']


def parse_messages(message_json):
    for message in message_json:
        if 'From' in message:
            msg_with = message['From']
            msg_from = message['From']
            msg_to = my_username
            direction = 'From'
        else:
            msg_with = message['To']
            msg_to = message['To']
            msg_from = my_username
            direction = 'To'
        msg_type = message['Media Type']
        msg_text = ''
        if 'Text' in message:
            msg_text = message['Text']
        position = message_json.index(message)
        # Appending the index value of the message to the timestamp to hopefully avoid
        # two messages with the same person with the same timestamp from overwriting
        msg_time = message['Created'] + ' ' + str(position)
        if msg_with not in chats:
            chats[msg_with] = dict()
        chats[msg_with][msg_time] = dict()
        chats[msg_with][msg_time]['direction'] = direction
        chats[msg_with][msg_time]['time'] = message['Created']
        chats[msg_with][msg_time]['From'] = msg_from
        chats[msg_with][msg_time]['To'] = msg_to
        chats[msg_with][msg_time]['type'] = msg_type
        chats[msg_with][msg_time]['text'] = unescape(msg_text)
        if msg_type not in ['TEXT']:
            chats[msg_with][msg_time]['text'] = '<font color="teal"><i>' + msg_type + '</i></font>  ' + unescape(
                msg_text)
        if msg_with not in contacts:
            contacts[msg_with] = dict()
            contacts[msg_with]['type'] = 'unknown'
            contacts[msg_with]['username'] = msg_with
            contacts[msg_with]['displayname'] = msg_with
            contacts[msg_with]['added'] = ''
            contacts[msg_with]['modified'] = ''
            contacts[msg_with]['source'] = 'unknown'


print("Grabbing style sheet data")
# Load css from index.html for use in output files
# # This css is slightly modified for output readability
with open(sc_archive_root + '/index.html', 'r') as indexfyle:
    index = indexfyle.read()
index_soup = BeautifulSoup(str(index), features="html.parser")
for styles in index_soup.select('style'):
    css = cssutils.parseString(styles.encode_contents())
    for rule in css:
        if rule.type == rule.STYLE_RULE:
            if rule.selectorText in ('.leftpanel'):
                if 'width' in rule.style:
                    rule.style.width = '30px'
            if rule.selectorText in ('.rightpanel'):
                if 'padding-left' in rule.style:
                    rule.style.paddingLeft = '30px'
    styles.replaceWith(css.cssText.decode())
style_css = css.cssText.decode()

# Get some info about you!
print("Loading your account details")
with open(os.path.abspath(json_dir + j_account)) as accountfyle:
    my_account_json = json.load(accountfyle)

my_username = my_account_json['Basic Information']['Username']
my_display_name = my_account_json['Basic Information']['Name']
my_start_date = my_account_json['Basic Information']['Creation Date']

# Get friends
print("Loading your friends")
with open(os.path.abspath(json_dir + j_friends)) as friendsfyle:
    my_friends_json = json.load(friendsfyle)

# Build a dictionary of friend dictionaries, each dict has info about the friend
print("Processing your friends")
contacts = dict()
parse_friends(my_friends_json['Friends'], 'friend')
parse_friends(my_friends_json['Friend Requests Sent'], 'pending')
parse_friends(my_friends_json['Blocked Users'], 'blocked')
parse_friends(my_friends_json['Deleted Friends'], 'unfriended')
parse_friends(my_friends_json['Hidden Friend Suggestions'], 'hidden_suggestion')

print("Loading chat history")
with open(os.path.abspath(json_dir + j_chat_history)) as chatfyle:
    my_chats_json = json.load(chatfyle)
print("Loading snap history")
with open(os.path.abspath(json_dir + j_snap_history)) as snapfyle:
    my_snaps_json = json.load(snapfyle)

print("Processing chat history - this may take a moment")
chats = dict()
parse_messages(my_chats_json['Received Saved Chat History'])
parse_messages(my_chats_json['Sent Saved Chat History'])
print("Processing snap history")
parse_messages(my_snaps_json['Received Snap History'])
parse_messages(my_snaps_json['Sent Snap History'])

chats_sorted = dict()
for someone in chats:
    if someone not in chats_sorted:
        chats_sorted[someone] = dict()
    chats_sorted[someone] = dict(sorted(chats[someone].items()))

print("Creating chat log files")
for someone in chats_sorted:
    contact_fyle = os.path.abspath(outdir + '/' + someone + '.html')
    # This is pretty janky don't look too close
    outFyle = open(contact_fyle, 'w')
    outFyle.write('''
    <!DOCTYPE html><head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    ''')
    outFyle.write(('    <title>{someone}</title> \n').format(someone=someone))
    outFyle.write('<style>\n')
    outFyle.write(style_css)
    outFyle.write('</style>\n')
    outFyle.write('</head><html><body> \n')
    outFyle.write('''<table style="table-layout: auto;">
                        <tbody><tr><th style="white-space: nowrap; overflow: hidden;">
                    ''')
    outFyle.write('<div class="rightpanel"><h1>Chat History with: {someone}</h1><p></p> \n'.format(someone=someone))
    header_table_line = '<li align="left"><b>{description}:</b> {value}</li>\n'
    outFyle.write(header_table_line.format(description="Display Name", value=contacts[someone]['displayname']))
    outFyle.write(header_table_line.format(description="Username", value=contacts[someone]['username']))
    outFyle.write(header_table_line.format(description="Added On", value=contacts[someone]['added']))
    outFyle.write(header_table_line.format(description="Contact Type", value=contacts[someone]['type']))
    # outFyle.write(header_table_line.format(description="Modified",value=contacts[someone]['modified']))
    # outFyle.write(header_table_line.format(description="Source",value=contacts[someone]['source']))
    outFyle.write('</br></br> \n')
    outFyle.write('''<table style="table-layout: auto;">
                    <tbody><tr><th style="white-space: nowrap; overflow: hidden;"> \n''')
    message_header = '<font color="{color}">{message_from}</font><font color="grey"> - {time}:</font></br>\n'
    message_line = '<font color="black">{message_text}</font><br>\n'
    for timestamp in chats_sorted[someone]:
        message = chats_sorted[someone][timestamp]
        color = 'blue'
        if message['direction'] == 'To':
            color = 'red'
        outFyle.write(message_header.format(color=color, message_from=message['From'], time=message['time']))
        outFyle.write(message_line.format(message_text=message['text']))
    outFyle.write('</tbody></html>\n')
    outFyle.close()
print("You have " + str(len(my_friends_json['Friends'])) + " friends and " + str(len(contacts)) + " total contacts")
print("You have " + str(len(chats_sorted)) + " saved conversations")
print('All Done!')
