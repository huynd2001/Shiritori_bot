import os
import discord
from discord.embeds import Embed
import requests
import json
from players import Players
from game import Game
from PyDictionary import PyDictionary
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
Dictionary = PyDictionary()
TOKEN = os.getenv('DISCORD_TOKEN')
COLOR = 0x00ff00

DEFAULT_TIME = 180
DEFAULT_DICT_TYPE = 0 
DEFAULT_JOIN_EMOTE = '✅'
""" 0 for english, 1 for urban dictionary, 2 for MAL, 3 for fifa, 4 for Vietnamese"""

intents = discord.Intents.default()
intents.members = True

shiritori = Game(DEFAULT_DICT_TYPE)
bot = commands.Bot(command_prefix = '&', intents = intents)

@bot.command(name = 'create', help = "Create a ultrabullet, bullet, blitz or srabble, shiritori game with different dictionary modes", aliases = ['c'])
async def create(ctx, game_type: str = None, dictionary_type: str = None):
    """create a game by selecting the game mode"""
    if shiritori.state == 1:
        embed_var = Embed(
            description = "Game already created!", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        return
    elif shiritori.state == 2:
        embed_var = Embed(
            description = "Game in progress!", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        return
    if game_type == None:
        embed_var = Embed(
            title = f'{ctx.message.author} please select a game mode!', 
            description = "ultrabullet, bullet, blitz, or scrabble", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        return
    if dictionary_type == None:
        embed_var = Embed(
            title = f'{ctx.message.author} please select a dictionary mode!', 
            description = "normal, urbandict, MAL, Fifa or Vietnamese", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        return
    game_type = game_type.lower()
    dictionary_type = dictionary_type.lower()
    correct_game_type = True
    correct_dict_type = True
    global DEFAULT_TIME
    if game_type == "ultrabullet":
        DEFAULT_TIME = 30
    elif game_type == "bullet":
        DEFAULT_TIME = 60
    elif game_type == "blitz":
        DEFAULT_TIME = 180  
    elif game_type == "scrabble":
        shiritori.BOOL_SCRABBLE = True
    else:
        embed_var = Embed(
            title = f'Invalid game mode. {ctx.message.author} please select again!', 
            description = "ultrabullet, bullet, blitz or scrabble", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        correct_game_type = False

    if correct_game_type == False:
        return
    
    dict_index = -1
    if dictionary_type == "normal":
        dict_index = 0
    elif dictionary_type == "urbandict":
        dict_index = 1
    elif dictionary_type == "mal":
        dict_index = 2
    elif dictionary_type == "fifa":
        dict_index = 3
    elif dictionary_type == "vietnamese":
        dict_index = 4
    else:
        embed_var = Embed(
            title = f'Invalid dictionary mode. {ctx.message.author} please select again!', 
            description = "normal, urbandict, MAL, fifa or Vietnamese", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        correct_dict_type = False

    if correct_dict_type == False:
        return
    shiritori.dict_type = dict_index
    shiritori.state = 1
    current_player = Players(str(ctx.message.author), DEFAULT_TIME, ctx.message.author.id)
    shiritori.add_new_players(current_player)
    embed_var = Embed(
        title = f'{ctx.message.author} is creating a new game!', 
        description = "Type &join or react to join the game.", 
        color = COLOR
    )
    message = await ctx.message.channel.send(embed = embed_var)
    await message.add_reaction(DEFAULT_JOIN_EMOTE)
    shiritori.start_message = message.id
    # print(f'debug checkpoint#1 {shiritori.state}')

   
@bot.command(name = 'join', help = 'join a game', aliases = ['j'])
async def join(ctx):
    """join the current game"""
    if shiritori.state == 2:
        embed_var = Embed(
            description = "Game in progress!", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    elif shiritori.state == 0 or shiritori.state == 3:
        embed_var = Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    else: 
        current_player = Players(str(ctx.message.author), DEFAULT_TIME, ctx.message.author.id)
        if shiritori.find_player(str(ctx.message.author)) != False:
            embed_var = Embed(
                    description = f'<@!{ctx.message.author.id}>'
                    ' You are already in the game!', 
                    color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
            return
        shiritori.add_new_players(current_player)
        embed_var = Embed(
            description = f'<@!{ctx.message.author.id}>'
            ' has joined the game.', 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    #print(f'debug checkpoint#2 {shiritori.state}')


@bot.command(name = 'start', help = 'start a game', aliases = ['s'])
async def start(ctx):
    """start the current game"""
    # print(shiritori.dict_type)
    if shiritori.state == 1:
        if shiritori.get_player_list_size() > 1:
            shiritori.start_game()
            desc = f'The game is beginning.\n<@!{shiritori.current_turn_Player().uid}>, '
            if shiritori.dict_type == 0:
                desc = desc + 'please choose a random English word.'
            elif shiritori.dict_type == 1:
                desc = desc + 'please choose a random Urban Dictionary phrase.'
            elif shiritori.dict_type == 2:
                desc = desc + 'please choose the full name of a random anime character.'
            elif shiritori.dict_type == 3:
                desc = desc + 'please choose a fifa player name.'
            elif shiritori.dict_type == 4:
                desc = desc + 'please choose a random Vietnamese word.'
            embed_var = Embed(
                description = desc, 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            embed_var = Embed(
                description = "Not enough players!", 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        # print(f'debug checkpoint#3 {shiritori.state}')
    elif shiritori.state == 2:
        embed_var = Embed(
            description = "Game in progress!", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    else: 
        embed_var = Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.event
async def on_message(message):
    """reaction to messages currently served mainly in the game Shiritori"""
    channel = message.channel
    word = str(message.content).lower() # case insensitive
    #print(f'reactional debug {shiritori.state}')
    if shiritori.state == 2 and shiritori.current_turn_Player() and str(message.author) == shiritori.current_turn_Player().name and message.content[0] != '&':
        shiritori.current_turn_Player().stop_countdown()
        # print(shiritori.current_turn_Player().time_left)
        if shiritori.current_turn_Player().time_left < 0:
            embed_var = Embed(
                description = f'<@!{message.author.id}>'
                '  You have ran out of time.', 
                color = COLOR
            )
            await channel.send(embed = embed_var)
            embed_var = Embed(
                description = f'<@!{message.author.id}>'
                ' has been kicced from the game.', 
                color = COLOR)
            await channel.send(embed = embed_var)

            shiritori.kick(shiritori.current_turn_Player())
            shiritori.next_turn()

            if shiritori.check_end():
                winner = shiritori.get_winner()
                embed_var = Embed(
                    title = "Game ended!", 
                    description = f'Congratulations <@!{winner.uid}>!' if winner is not None else f'Game ended in a draw!', 
                    color = COLOR)
                await channel.send(embed = embed_var)
                shiritori.end()
                return
            
            embed_var = Embed(
                title = 'Final turn! Answer correctly to win!' if shiritori.last_person else '',
                description = f'<@!{shiritori.current_turn_Player().uid}> your turn.\n' +
                f'Begin with the letter `{shiritori.current_letter}`.\n' +
                f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
                color = COLOR
            )
            await channel.send(embed = embed_var)

        else:
            if shiritori.check_word_validity(word) == 0:
                shiritori.current_turn_Player().countdown()
                embed_var = Embed(
                    description = 'Invalid word Baka!\n' 
                    + "{:.2f}".format(shiritori.current_turn_Player().time_left)
                    + ' seconds left.\n', 
                    color = COLOR
                )
                await channel.send(embed = embed_var)
                if shiritori.BOOL_SCRABBLE == True:
                    shiritori.current_turn_Player().penalty(20)
                    embed_var = Embed(
                        description = '-20 points penalty',
                        color = COLOR
                    )
                    await channel.send(embed = embed_var)

                shiritori.current_turn_Player().invalid_left -= 1
                if shiritori.current_turn_Player().invalid_left < 0:
                    embed_var = Embed(
                        description = f'<@!{message.author.id}>'
                        ' Your word is invalid for more than 3 times.', 
                        color = COLOR
                    )
                    await channel.send(embed = embed_var)
                    embed_var = Embed(
                        description = f'<@!{message.author.id}>'
                        '  has been kicced from the game.', 
                        color = COLOR
                    ) 
                    await channel.send(embed = embed_var)
                    
                    shiritori.kick(shiritori.current_turn_Player()) 
                    shiritori.next_turn()

                    if shiritori.check_end():
                        winner = shiritori.get_winner()
                        embed_var = Embed(
                            title = "Game ended!", 
                            description = f'Congratulations <@!{winner.uid}>!' if winner is not None else f'Game ended in a draw!', 
                            color = COLOR)
                        await channel.send(embed = embed_var)
                        shiritori.end()
                        return

                    embed_var = Embed(
                        title = 'Final turn! Answer correctly to win!' if shiritori.last_person else '',
                        description = f'<@!{shiritori.current_turn_Player().uid}> your turn.\n' +
                        f'Begin with the letter `{shiritori.current_letter}`.\n' +
                        f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
                        color = COLOR
                    )
                    await channel.send(embed = embed_var)
                    
                if shiritori.check_end():
                    winner = shiritori.get_winner()
                    embed_var = Embed(
                        title = "Game ended!", 
                        description = f'Congratulations <@!{winner.uid}>!' if winner is not None else f'Game ended in a draw!',  
                        color = COLOR
                    )
                    await channel.send(embed = embed_var)
                    shiritori.end()
                    return

            else:
                shiritori.add_new_word(word)
                
                if shiritori.get_player_list_size() == 1:
                    shiritori.last_person_answered = True

                if shiritori.check_end():
                    winner = shiritori.get_winner()
                    embed_var = Embed(
                        title = "Game ended!", 
                        description = f'Congratulations <@!{winner.uid}>!' if winner is not None else f'Game ended in a draw!',  
                        color = COLOR
                    )
                    await channel.send(embed = embed_var)
                    shiritori.end()
                    return

                shiritori.next_turn()
                embed_var = Embed(
                    title = 'Final turn! Answer correctly to win!' if shiritori.last_person else '',
                    description = f'<@!{shiritori.current_turn_Player().uid}> your turn.\n' +
                    f'Begin with the letter `{shiritori.current_letter}`.\n' +
                    f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
                    color = COLOR
                )
                await channel.send(embed = embed_var)

    else:
        await bot.process_commands(message)

@bot.command(name = 'resign', help = "resign from the game", aliases = ['r'])
async def resign(ctx):
    """resign from the current game"""
    player_name = str(ctx.message.author)
    if shiritori.state == 1:
        in_the_game = 0
        for s in shiritori.list_of_players:
            if player_name == s.name:
                shiritori.kick(s)
                in_the_game = 1
        if in_the_game:
            embed_var = Embed(
            description = f"<@!{ctx.message.author.id}> has resigned from the game.", 
            color = COLOR)
            await ctx.message.channel.send(embed = embed_var)
        else:
            embed_var = Embed(
            description = f"<@!{ctx.message.author.id}> You are not in the game yet!", 
            color = COLOR)
            await ctx.message.channel.send(embed = embed_var)


    elif shiritori.state == 2:
        nxt_turn = 0
        if  player_name == shiritori.current_turn_Player().name:
            nxt_turn = 1
        for s in shiritori.list_of_players:
            if player_name == s.name:
                shiritori.kick(s)
                s.out_of_rank(shiritori.BOOL_SCRABBLE)
        embed_var = Embed(
            description = f"<@!{ctx.message.author.id}> has resigned from the game.", 
            color = COLOR)
        await ctx.message.channel.send(embed = embed_var)

        if shiritori.check_end():
            winner = shiritori.get_winner()
            embed_var = Embed(
                title = "Game ended!", 
                description = f'Congratulations <@!{winner.uid}>!' if winner is not None else f'Game ended in a draw!',
                color = COLOR)
            # print(shiritori.get_winner().score)
            await ctx.channel.send(embed = embed_var)
            shiritori.end()
            return

        if nxt_turn:
            shiritori.next_turn()
            embed_var = Embed(
                title = 'Final turn! Answer correctly to win!' if shiritori.last_person else '',
                description = f'<@!{shiritori.current_turn_Player().uid}> your turn.\n' +
                f'Begin with the letter `{shiritori.current_letter}`.\n' +
                f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
                color = COLOR
            )
            await ctx.channel.send(embed = embed_var)

    else:
        embed_var = Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.command(name = 'kicc', help = "kicc a player", aliases = ['k'])
async def kicc(ctx, raw_id: str):
    """kick a player out of the game"""
    player_id = raw_id.translate({ ord(c): None for c in "<@!>" })
    if shiritori.state == 1:
        in_the_game = 0
        for s in shiritori.list_of_players:
            if player_id == s.uid:
                shiritori.kick(s)
                in_the_game = 1
                break
        # print(in_the_game)

        if in_the_game:
            embed_var = Embed(
            description = f"<@!{player_id}> has been kicked from the game.", 
            color = COLOR)
            await ctx.message.channel.send(embed = embed_var)
        else:
            embed_var = Embed(
            description = f"<@!{player_id}> is not in the game yet!", 
            color = COLOR)
            await ctx.message.channel.send(embed = embed_var)

    elif shiritori.state == 2:
        if str(ctx.message.author) != shiritori.game_owner().name:
            embed_var = Embed(
                description=f'<@!{ctx.message.author.id}>' 
                ' you do not have permission', 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            nxt_turn = 0
            has_find = False
            if  player_id == shiritori.current_turn_Player().uid:
                nxt_turn = 1
            for s in shiritori.list_of_players:
                #print(player_id, s.uid)
                if player_id == s.uid:
                    has_find = True
                    shiritori.kick(s)
                    s.out_of_rank(shiritori.BOOL_SCRABBLE)
                    break
            if has_find == True:
                embed_var = Embed(
                    description = f"<@!{player_id}> has been kicced from the game.", 
                    color = COLOR)
                await ctx.message.channel.send(embed = embed_var)
            else:
                embed_var = Embed(
                    description = f'<@!{player_id}> is not in the game yet!',
                    color = COLOR
                )
                await ctx.message.channel.send(embed = embed_var)

            if shiritori.check_end():
                winner = shiritori.get_winner()
                embed_var = Embed(
                    title = "Game ended!", 
                    description = f'Congratulations <@!{winner.uid}>!' if winner is not None else f'Game ended in a draw!',  
                    color = COLOR)
                await ctx.channel.send(embed = embed_var)
                shiritori.end()
                return

            if nxt_turn:
                shiritori.next_turn()    
                embed_var = Embed(
                    title = 'Final turn! Answer correctly to win!' if shiritori.last_person else '',
                    description = f'<@!{shiritori.current_turn_Player().uid}> your turn.\n' +
                    f'Begin with the letter `{shiritori.current_letter}`.\n' +
                    f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
                    color = COLOR
                )
                await ctx.channel.send(embed = embed_var)


    else:
        embed_var = Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.command(name = 'leaderboard', help = "display leaderboard", aliases = ['l']) 
async def leaderboard(ctx):
    if shiritori.state == 3:
        if shiritori.archive_leaderboard[-1][1] == True:
            ranking = shiritori.display_leaderboard()
            desc = ""
            for i in range (len(ranking)):
                if ranking[i].get_score() != -9203:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> with {ranking[i].get_score()} points\n'
                else:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> out of the game\n'
            embed_var = Embed(
                title = 'Final leaderboard',
                description = desc,
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            ranking = shiritori.display_leaderboard()
            desc = ""
            for i in range (len(ranking)):
                if ranking[i].time_left == -9203:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> out of the game\n'
                elif ranking[i].time_left < 0:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> out of time\n'
                else:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> with {ranking[i].time_left:.2f} seconds left\n'
            embed_var = Embed(
                title = 'Final leaderboard',
                description = desc,
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
    elif shiritori.state == 2:
        if shiritori.BOOL_SCRABBLE == True:
            ranking = shiritori.display_leaderboard()
            desc = ""
            for i in range (len(ranking)):
                if ranking[i].get_score() != -9203:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> with {ranking[i].get_score()} points\n'
                else:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> out of the game\n'
            embed_var = Embed(
                title = 'Final leaderboard',
                description = desc,
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            ranking = shiritori.display_leaderboard()
            desc = ""
            for i in range (len(ranking)):
                if ranking[i].time_left == -9203:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> out of the game\n'
                elif ranking[i].time_left < 0:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> out of time\n'
                else:
                    desc = desc + f'#{i + 1}: <@!{ranking[i].uid}> with {ranking[i].time_left:.2f} seconds left\n'
            embed_var = Embed(
                title = 'Final leaderboard',
                description = desc,
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
    else:
        embed_var = Embed(
            description = "There is no archived game yet!",
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.command(name = 'abort', help = "abort the game")
async def abort(ctx):
    """abort the game"""
    if shiritori.state == 1 or shiritori.state == 2:
        if str(ctx.message.author) != shiritori.game_owner().name:
            embed_var = Embed(
                description=f'<@!{ctx.message.author.id}>' 
                ', you do not have permission', 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            shiritori.end()
            embed_var = Embed(
                description = "The game has been aborted.", 
                color = COLOR)
            await ctx.message.channel.send(embed = embed_var)
    else:
        embed_var = Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.command(name = 'mean', help = "return the meaning of a string")
async def mean(ctx, word = '', word_type = ''):
    """return the meaning(s) of a word"""
    if word == '':
        embed_var = Embed(
            description = "Please include a word.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        return
    if word_type == '':
        embed_var = Embed(
            description = "Please include a word type.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    else:
        word_type = word_type.capitalize()
        temporary_dict = Dictionary.meaning(word)
        if temporary_dict is None:
            embed_var = Embed(
                description = "Word have no meaning!", 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        elif word_type not in temporary_dict:
            embed_var = Embed(
                description = "Wrong word type!", 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            for index, meaning_line in enumerate(temporary_dict[word_type]):
                embed_var = Embed(
                    description=f'-{meaning_line}', 
                    color = COLOR
                )
                await ctx.send(embed = embed_var)    
                if index == 4:
                    break

@bot.command(name = 'urbanmean', help = "return the meaning of a string in urban dictionary")
async def urbanmean(ctx, word = ''):
    if word == '':
        embed_var = Embed(
            description = "Please include a phrase.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        return
    response = requests.get("https://api.urbandictionary.com/v0/define?term=" + word).text
    dict_response = json.loads(response)
    if ('error' in dict_response): # url is redirected
        new_url = requests.get("https://www.urbandictionary.com/define.php?term="+ word).url
        new_word = new_url.rsplit('term=', 1)[1] # get the word redirected to (after the 'term=' part in the url)
        word = new_word
        response = requests.get("https://api.urbandictionary.com/v0/define?term=" + word).text
        dict_response = json.loads(response)

    def_list = dict_response['list']
    if not len(def_list):
        embed_var = Embed(
        description='The phrase has no meaning!', 
        color = COLOR
        )
        await ctx.send(embed = embed_var)
    else:
        for index, mean in enumerate(def_list):
            embed_var = Embed(
            description=str(mean['definition']), 
            color = COLOR
            )
            await ctx.send(embed = embed_var)
            if index == 4:
                break

@bot.command(name = 'announce', help = 'announce something')
async def announce(ctx):
    await shiritori.announce(ctx, 'a')
    
@bot.event
async def on_ready():
    print("maid0902 on board")

@bot.event
async def on_reaction_add(reaction, user):
    if shiritori.state != 1: # return if not waiting for players
        return
    if reaction.emoji != DEFAULT_JOIN_EMOTE or reaction.message.id != shiritori.start_message: # return if not start message or wrong emote
        return
    if user.id == bot.user.id: # return if it's the bot
        return
    if (not shiritori.find_player(str(user))):
        current_player = Players(str(user), DEFAULT_TIME, user.id)
        shiritori.add_new_players(current_player)
        print(f"{str(user)} joined the game")

@bot.event
async def on_reaction_remove(reaction, user):
    if shiritori.state != 1: # return if not waiting for players
        return
    if reaction.emoji != DEFAULT_JOIN_EMOTE or reaction.message.id != shiritori.start_message: # return if not start message or wrong emote
        return
    for s in shiritori.list_of_players:
        if str(user) == s.name:
            shiritori.kick(s)
            print(f"{str(user)} left the game")

async def announce_kick():
    pass

bot.run(TOKEN)
