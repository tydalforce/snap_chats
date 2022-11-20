# snap_chats
Processes a Snapchat data download for readability.  Grabs all your messages from the archive and creates individual chat log files viewable in a web browser.  This, of course, only has access to Saved messages; expired history is gone forever!


Download your Snapchat data
https://support.snapchat.com/en-US/article/download-my-data
extract the .zip archive somewhere
Update the "sc_archive_root =" path in the script to point to this directory, and run

Requires Python 3.x
Requires BeautifulSoup 4 (bs4) and cssutils


<img width="946" alt="Screenshot 2022-11-20 at 10 40 44 AM" src="https://user-images.githubusercontent.com/12863601/202911436-93299c7d-9c8e-44f5-b9be-cf53b34746d0.png">
