# Chatplot

Chatplot is a simple Python script for both Twitch viewers and streamers to easily locate highlights within a livestream.
Users input a channel to observe, as well as the maximum amount of time to watch the channel continuously. An IRC bot then
records the number of chat messages per minute until the time is reached (or the stream goes offline). The data is used to
generate a histogram and print the nine most active minutes.

![](http://i.imgur.com/StbeYuq.png)

**Note**: The X-axis doesn't necessarily start from zero because it displays the timestamps of the VOD. In other words, if
the script is executed after the stream has been live for some time, the x values will be offset by that amount of minutes.
