# PanoptoDownloader
Downloads videos from Panopto

You can pass the "-headless" argument which will open up the browser alongside command prompt.
Right now this program is only tested on windows, not sure whether it would work on any other OS.

ChromeDriver 97.0.4692.71 is required, any above version is incompatible.


--How to use--

Type in your school's moodle page like this: www.moodle.boun.edu.tr (For the moment it only works with moodle)

Type in your username and password so the program logs you in, so your session is stored and can easily login to panopto.
Type in the panopto url of the video you would like to download.

If the video is recorded live then it won't show any progress since it will be downloading every part of it and then combining them. If the video is recorded first and then uploaded to panopto then it is probably in .mp4 format, while downloading it the progress will show. 

Right now it only detects and downloads .mp4 and .ts files.