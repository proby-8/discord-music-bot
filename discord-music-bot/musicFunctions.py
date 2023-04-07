import re
import discord
import os
import urllib
import yt_dlp


async def sendMessageAsync(ctx, message):
    await ctx.send(message)


async def join(ctx):
    # join the voice channel
    try:
        channel = ctx.author.voice.channel
        await channel.connect()
        server = ctx.guild
        print("Joined a voice chat in the server: " + str(server))
        await ctx.guild.change_voice_state(channel = channel, self_mute=False, self_deaf=False)
    except AttributeError:
        await ctx.send("You are not in a voice channel.")
    except discord.errors.ClientException:
        pass

    try:
        # make folder struct for server if it doesn't exist
        os.makedirs(os.path.join(str(ctx.guild)), 0o666)
        file = open(str(os.path.join(str(ctx.guild))) + "/" + str(ctx.guild) + ".txt", "w+")
        file.close()
    except Exception:
        # if folder struct exists, make sure the txt file exists
        try :
            file1 = open(str(ctx.guild) + '/' + str(ctx.guild) + ".txt", "w")
            file1.close()
        except Exception as e:
            print("There was a problem creating the file.")
            print(str(e))


async def queueSong(ctx, songname):
    # write songname into file
    file = open(str(ctx.guild) + '/' + str(ctx.guild) + ".txt", 'a')
    file.writelines(songname)
    file.close()


def playSong(ctx):
    # get songname from file
    file = open(str(ctx.guild) + '/' + str(ctx.guild) + ".txt", 'r')
    songname = file.readline()
    file.close()

    # last song in queue
    if (songname == ""):
        return

    # get the song url
    songname = songname.replace(" ", "+")
    # search for the song
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + songname)
    # find all possible videos and save them to video_ids
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    # choose the top video, get its url
    songurl = ("https://www.youtube.com/watch?v=" + video_ids[0])

    # download the song
    if (os.path.isfile(str(ctx.guild) + '/' + str(ctx.guild) + ".mp3")):
        # a file is already there
        os.remove(str(ctx.guild) + '/' + str(ctx.guild) + ".mp3")
    ydlPref = {
                'format': 'bestaudio/best',
                'postprocessorts': [{
                    'key': 'FFmpegExtractAudio',
                    'prefessedcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
    
    # check length of file
    with yt_dlp.YoutubeDL(ydlPref) as ydl:
        info = ydl.extract_info(songurl, download=False)
    seconds = (info['duration'])

    # has to be less than 10 min
    if (seconds <= 600) :
        with yt_dlp.YoutubeDL(ydlPref) as ydl:
            info = ydl.extract_info(songurl, download=True)
    else:
        # loop through videos till shorter one is found?
        print(message)
        return
    
    # now have the downloaded song, rename it and put in server folder
    for file in os.listdir():
        if file.endswith(".webm"):
            os.rename(file, str(ctx.guild) + '/' + str(ctx.guild) + ".mp3")
        if file.endswith(".m4a"):
            os.rename(file, str(ctx.guild) + '/' + str(ctx.guild) + ".mp3")

    # play the song
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(str(ctx.guild) + '/' + str(ctx.guild) + ".mp3"))
    ctx.voice_client.play(source, after=lambda ex: playSong(ctx))

    print(f"\nNow playing {info['fulltitle']}")

    # print
    seconds = (info['duration'])
    minutes, seconds = divmod(seconds, 60)
    # print 01 rather than 1
    if (seconds < 10):
        Sseconds = ("0"+str(seconds))
    else:
        Sseconds = seconds
    message = (f"```Now playing: {info['title']}\nDuration: {minutes}:{(Sseconds)}\n(Note that queued songs will not be announced)```")

    # delete the old song
    file1 = open(str(ctx.guild) + '/' + str(ctx.guild) + ".txt", 'w+') 
    content = file1.readlines()
    file1.writelines(content[1:])
    file1.close()

    return message