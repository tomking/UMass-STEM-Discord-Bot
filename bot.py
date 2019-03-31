import random
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
from overlay import overlay_image, url_to_image, get_image_url, draw_text
from stem_roles import stem_add_role, stem_remove_role, list_roles
from face_detection import paste_on_face, open_image_cv
import os
import time

BOT_PREFIX = "$"
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_ROLE = "bots"

bot_last_command = {} #Key = User ID, Value = Bot's most recent message tied to the command
 
client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(game = Game(name = '#rules | $help'))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message_delete(message):
    author = message.author
    print(author.id)
    if message.server.id == '387465995176116224':
        if (BOT_ROLE not in [role.name.lower() for role in author.roles]) and author.id != '98138045173227520':
            content = message.content
            await client.send_message(client.get_channel('557002016782680076'), '_Deleted Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + message.channel.mention + '\n**Contents:** *' + content + '*\n--------------')

@client.event
async def on_message_edit(before, after):
    author = before.author
    if before.server.id == '387465995176116224':
        if (BOT_ROLE not in [role.name.lower() for role in author.roles]) and author.id != '98138045173227520':
            before_content = before.content
            after_content = after.content
            await client.send_message(client.get_channel('557002016782680076'), '_Edited Message_\n**Message sent by:** ' + author.mention + '\n**Channel:** ' + before.channel.mention + '\n**Pre-edit contents:** *' + before_content + '*\n**Post-edit contents:** *'+ after_content + '*\n--------------')

@client.command()
async def help():
    embed = discord.Embed(
        color = discord.Color.orange()
    )
    embed.set_author(name='Help', icon_url='https://cdn.discordapp.com/attachments/501594682820788224/558396074868342785/UMass_Stem_discord_logo.png')
    embed.add_field(name = 'Roles', value='*$getlist* - Sends a list of all the available roles\n*$get [role]* - Gives you the specified role\n*$remove [role]* - Removes the specified role from you', inline=True)
    embed.add_field(name = 'Memes', value='*$mdraw [image/url]* - Sends a photo of <:smugmarius:557699496767651840> drawing on the specified image\n*$bdraw [image/url]* - Sends a photo of <:barr:557186728167997445> drawing on the specified image\n*$erase* - Deletes the most recent m/bdraw generated by the bot', inline=True)
    await client.say(embed=embed)

@client.command(name='get', pass_context = True)
async def get_role(requested_role):
    member = requested_role.message.author
    if requested_role.message.server.id == '387465995176116224':
        await stem_add_role(requested_role, member, client)
    else:
        await client.send_message(requested_role.message.channel, embed=discord.Embed(description="Roles are not yet supported on this server", color=discord.Color.dark_red()))

@client.command(name='remove', pass_context = True)
async def remove_role(requested_role):
    member = requested_role.message.author
    if requested_role.message.server.id == '387465995176116224':
        await stem_remove_role(requested_role, member, client)
    else:
        await client.send_message(requested_role.message.channel, embed=discord.Embed(description="Roles are not yet supported on this server", color=discord.Color.dark_red()))

@client.command(name='getlist', pass_context = True)
async def get_list(ctx):
    await list_roles(ctx, client) # found in stem_roles.py

@client.command(name='mdraw', pass_context = True)
async def mdraw(ctx):
    url = get_image_url(ctx)
    if url == 0:
        output = draw_text(ctx.message.content[7:], Path('memes/marius/draw.png'))
    else:
        output = overlay_image(url_to_image(url), Path('memes/marius/draw.png'))
    name = 'marius-drawing.png'
    output.save(name)
    message = await client.send_file(ctx.message.channel, name)
    track_command(ctx.message.author.id, message)
    os.remove(name)

@client.command(name='bdraw', pass_context = True)
async def bdraw(ctx):
    url = get_image_url(ctx)
    if url == 0:
        output = draw_text(ctx.message.content[7:], Path('memes/barrington/bdraw.png'))
    else:
        output = overlay_image(url_to_image(url), Path('memes/barrington/bdraw.png'))
    output.save('barrington-drawing.png')
    message = await client.send_file(ctx.message.channel, 'barrington-drawing.png')
    track_command(ctx.message.author.id, message)
    os.remove('barrington-drawing.png')

#Deletes image based messages, such as bdraw, that the user requesting just sent.
@client.command(name='erase', pass_context = True)
async def erase(ctx):
    if bot_last_command[ctx.message.author.id] is not None:
        await client.delete_message(bot_last_command[ctx.message.author.id])
        bot_last_command[ctx.message.author.id] = None #Clears this back up to avoid errors

@client.command(name='barrify', pass_context = True)
async def barrify(ctx):
    url = get_image_url(ctx)
    if url == 0: # invalid image
        await client.send_message(ctx.message.channel, embed=discord.Embed(description="Invalid image", color=discord.Color.red()))
        return
    else:
        output = paste_on_face(Path('memes/barrington/barr-face.png'), url)
    output.save('barrify.png')
    message = await client.send_file(ctx.message.channel, 'barrify.png')
    track_command(ctx.message.author.id, message)
    os.remove('barrify.png')


def track_command(author, bot_message):
    bot_last_command[author] = bot_message

client.run(BOT_TOKEN)
