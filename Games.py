#!/usr/bin/env python3
import random
import asyncio
import re
import discord
from discord.ext import commands
from Users import Users
from random import choices

# only read words file once so we won't have to re-open the file every game call
words_file = open("db_and_words\words.txt", "r")
all_words = words_file.readlines()
words_file.close()

# short decorator function declaration, confirm that command user has an account in database
def has_account():
    def predicate(ctx):
        user = Users(ctx.message.author.id)
        if user.find_user() == 0:
            return False
        else:
            return True
    return commands.check(predicate)

class Games:
    def __init__(self, client):
        self.client = client

    '''ROB FUNCTION'''
    @has_account()
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name='rob', description='Steal money from others', brief='can use =steal',
                      aliases=['thief', 'thieve', 'ROB', 'steal', 'mug'], pass_context=True)
    async def rob(self, context, *args):
        # create instance of the user starting the robbery
        robber = Users(context.message.author.id)
        # declare 30% fail chance, used to calculate chance of failing rob
        fail_chance = 30
        # pick a random user in the server to rob
        # target variable will function as the victim user's "english" name
        target = random.choice(list(context.message.server.members))
        # make an instance of the target
        victim = Users(target.id)
        victim_id = target.id
        counter = 1

        # if they specified a rob target, change the random target to their specified target
        if args:
            try:
                # use regex to extract only the user-id from the user targeted
                victim_id = re.findall("\d+", args[0])[0]
                victim = Users(victim_id)

                # get_member() returns the "member" object that matches an id provided
                target = context.message.server.get_member(victim_id)
                # higher fail chance, 35%, if they want to specify a rob target
                fail_chance = 35
                # if the target doesn't have an account, change fail chance back to 30% and the target will reroll next loop
                if victim.find_user() == 0:
                    fail_chance = 30
                    await self.client.say(context.message.author.mention +
                                          " Your rob target doesn't have an account."
                                          "\n**Rerolling** rob target now!")
                if robber.get_user_peace_status() == 1:
                    fail_chance = 30
                    await self.client.say(context.message.author.mention +
                                          ' You are in :dove: **peace mode** :dove: and cannot use =rob @user.'
                                          '\n**Rerolling** rob target now!')

                    # pick a random user in the server to rob
                    # target variable will function as the victim user's "english" name
                    target = random.choice(list(context.message.server.members))
                    # make an instance of the target
                    victim = Users(target.id)
                    victim_id = target.id
                elif victim.get_user_peace_status() == 1:
                    fail_chance = 30
                    await self.client.say(context.message.author.mention +
                                          ' That target is in :dove: **peace mode** :dove: and exempt to =rob @user.'
                                          '\n**Rerolling** rob target now!')

                    # pick a random user in the server to rob
                    # target variable will function as the victim user's "english" name
                    target = random.choice(list(context.message.server.members))
                    # make an instance of the target
                    victim = Users(target.id)
                    victim_id = target.id

            except:
                pass

        # while the user to rob is the robber, re-roll the target
        # while the user to rob does not have an account in the database, re-roll the target
        while victim_id == context.message.author.id or victim.find_user() == 0:
            # only try 120 members in the user's server
            # otherwise if the user was the sole player with an account in the discord server, infinite while loop
            # this part is inefficient, but only way I can think of right now with discord's functionality
            if counter == 120:
                # no users were found to rob if we hit 120 in the counter
                # calculate random integer 1-100
                # if the result is within 1 through fail chance, they failed the rob, so take bail money and return
                if fail_chance >= random.randint(1, 100) >= 1:
                    robber_level = robber.get_user_level(0)

                    bail = int(robber_level * 8.4)
                    robber.update_user_money(bail * -1)

                    msg = '<a:policesiren2:490326123549556746> :oncoming_police_car: ' \
                          '<a:policesiren2:490326123549556746>\n<a:monkacop:490323719063863306>' \
                          '\u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B' \
                          '<a:monkacop:490323719063863306>\n' + 'Police shot you in the process.\n' \
                          'You spent **$' + str(bail) + '** to bail out of jail.'

                    # embed the rob failure message, set thumbnail to 80x80 of a "police siren" gif
                    em = discord.Embed(description=msg, colour=0x607d4a)
                    em.set_thumbnail(url="https://cdn.discordapp.com/emojis/490326123549556746.gif?size=80")
                    await self.client.say(embed=em)
                    return
                else:
                    # if they passed the fail test, give the user a small prize and return
                    bonus_prize = int(robber.get_user_level(0) * 29.3)
                    robber.update_user_money(bonus_prize)
                    msg = '**No users found to rob...** ' \
                          '\nOn the way back to your basement, you found **$' + str(bonus_prize) + '** ' + \
                          '<:poggers:490322361891946496>'
                    # embed the rob confirmation message, set thumbnail to 40x40 of a "ninja" gif
                    em = discord.Embed(description=msg, colour=0x607d4a)
                    em.set_thumbnail(url="https://cdn.discordapp.com/emojis/419506568728543263.gif?size=40")
                    await self.client.say(embed=em)
                    return
            target = random.choice(list(context.message.server.members))
            # create a new instance of victim each loop
            # in order to check if the reroll has an account in database
            victim = Users(target.id)
            victim_id = target.id
            counter += 1


        # calculate random integer 1-100
        # if the result is within 1 through fail chance, they failed the rob
        if fail_chance >= random.randint(1, 100) >= 1:
            robber_level = robber.get_user_level(0)

            bail = int(robber_level * 10.4)
            robber.update_user_money(bail * -1)

            msg = '<a:policesiren2:490326123549556746> :oncoming_police_car: ' \
                  '<a:policesiren2:490326123549556746>\n<a:monkacop:490323719063863306>' \
                  '\u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B' \
                  '<a:monkacop:490323719063863306>\n**' + str(target.display_name) + '**' \
                  ' dodged and the police shot you in the process.\nYou spent **$' + str(bail) + '** to bail out of jail.'

            # embed the rob failure message, set thumbnail to 80x80 of a "police siren" gif
            em = discord.Embed(description=msg, colour=0x607d4a)
            em.set_thumbnail(url="https://cdn.discordapp.com/emojis/490326123549556746.gif?size=80")
            await self.client.say(embed=em)
            return

        # we passed the dodge check, so reward thief with prize and bonus prize
        victim_money = victim.get_user_money(0)
        victim_level = victim.get_user_level(0)
        robber_level = robber.get_user_level(0)

        # the victim will only lose the prize, not the bonus prize
        bonus_prize = int(robber_level * 29.3)

        # the prize will begin by scaling by victim's level
        prize = int(victim_level * 9.4)
        # if prize greater than the robber's maximum prize amount, decrease the standard prize to compensate
        if prize > int(robber_level * 9.4):
            prize = int(robber_level * 9.4)
        # if prize less than the robber's maximum prize amount, increase the bonus prize to compensate
        if prize < int(robber_level * 9.4):
            bonus_prize += int(robber_level * 9.4 - prize)


        # balancing mechanic, don't let victims lose any more money when they have less money than -50x their level
        if not victim_money < (victim_level * -50):
            # subtract prize from victim
            victim.update_user_money(prize * -1)
        # reward robber with prize and bonus prize
        robber.update_user_money(prize + bonus_prize)
        msg = '**Success!** <:poggers:490322361891946496> ' \
              '\nRobbed **$' + str(prize) + '** (+**$' + str(bonus_prize) \
              + '**) from **' + str(target.display_name) + '**'

        # embed the rob confirmation message, set thumbnail to 40x40 of a "ninja" gif
        em = discord.Embed(description=msg, colour=0x607d4a)
        em.set_thumbnail(url="https://cdn.discordapp.com/emojis/419506568728543263.gif?size=40")
        await self.client.say(embed=em)

    '''TOURNAMENT BATTLE FUNCTION'''
    @has_account()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='tournament', aliases=['TOURNAMENT', 'tourney', 'TOURNEY'], pass_context=True)
    async def enter_daily_tournament(self, context):
        # the bulk work of this feature is when the results are calculated from daily_maintenance.py
        # create instance of user who wants to enter the daily, server-specific colosseum tournament
        fighter = Users(context.message.author.id)
        # update their tourney_server_id entry to be the server they executed the command on
        msg = fighter.update_user_tourney_server_id(context.message.server.name, context.message.server.id)

        # embed the tourney registration confirmation message, set thumbnail to 40x40 of the respective server's icon
        em = discord.Embed(description=msg, colour=0x607d4a)
        thumb_url = "https://cdn.discordapp.com/icons/{0.id}/{0.icon}.webp?size=40".format(context.message.server)
        em.set_thumbnail(url=thumb_url)
        await self.client.say(embed=em)


    '''1v1 BATTLE FUNCTION'''
    @has_account()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name='fight', description='Battle another user in your server',
                      brief='can use "fight @user X --X being amount to bet"',
                      aliases=['battle', 'BATTLE', 'FIGHT', 'duel', 'DUEL'], pass_context=True)
    async def battle_user(self, context, *args):
        # retrieve how much the fighter is betting on the battle
        if len(args) == 2:
            bet = int(args[1])
            if bet < 1:
                await self.client.say('Bet cant be negative...')
                return
        else:
            await self.client.say('No bet specified, defaulting to **$10**\n ** **')
            bet = 10

        try:
            # make instance of user for user initiating fight
            fighter1 = Users(context.message.author.id)

            # retrieve battle target
            target = args[0]
            # use regex to extract only the user-id from the user targeted
            fighter2_id = int(re.findall("\d+", target)[0])
            fighter2 = Users(fighter2_id)

            # check if targeted user has account
            if fighter2.find_user() == 0:
                await self.client.say(context.message.author.mention +
                                      " Your fighting target doesn't have an account."
                                      "\nTell them to use **=create** to make one.")
                return

            # check if both users have enough money
            if fighter1.get_user_money(0) < bet or fighter2.get_user_money(0) < bet:
                await self.client.say(context.message.author.mention +
                                      " Either you or the target doesn't have enough money...")
                return

            # give target the prompt to ask if they will accept the challenge
            alert_msg = await self.client.say(target + ', you were challenged for **$' + str(bet) +
                                              '**\n:crossed_swords: Type **yes** to accept this battle. :crossed_swords: ')

            # made this check function with the help of discord API documentation
            # it will be called below to check if the confirmation response to fight is from fighter2
            def fighter2check(msg):
                return int(msg.author.id) == fighter2_id

            # (try to) wait for a battle acceptance from other user
            try:
                confirm = await self.client.wait_for_message(timeout=60, check=fighter2check)
                await self.client.delete_message(alert_msg)
                if confirm.clean_content.upper() == 'YES':
                    await self.client.delete_message(confirm)
                    # have to use 2 messages to enlarge the emojis
                    msg = context.message.author.mention + ' vs ' + args[0] + ' for **$' + str(bet) \
                          + '**\nFight will conclude in 10 seconds...'
                    # embed the duel alert message, set thumbnail to a "nunchuck frog" gif of size 64x64
                    em = discord.Embed(title="", colour=0x607d4a)
                    em.add_field(name="DUEL ALERT", value=msg, inline=True)
                    em.set_thumbnail(url="https://cdn.discordapp.com/emojis/493220414206509056.gif?size=64")

                    await self.client.say(embed=em)
                    await asyncio.sleep(10)

                    # get the stats of each fighter
                    # algorithm for calculating a fighter's stats in duels: (item score + user level*2 + 20)
                    f1_stats = fighter1.get_user_item_score() + (fighter1.get_user_level(0)*2) + 20
                    f2_stats = fighter2.get_user_item_score() + (fighter2.get_user_level(0)*2) + 20
                    total = (f1_stats + f2_stats)
                    f1_weight = f1_stats / total
                    f2_weight = f2_stats / total


                    # decide winner with custom function
                    # if it returns 1, fighter 1 won
                    # if it returns 2, fighter 2 won
                    winner = battle_decider(1, 2, f1_weight, f2_weight)

                    # check if they tried to exploit the code by spending all their money during the battle
                    if fighter1.get_user_money(0) < bet or fighter2.get_user_money(0) < bet:
                        await self.client.say(
                            context.message.author.mention + " One of you spent money while battling...")
                        return

                    # check who the winner was returned as
                    # update account balances respectively
                    if winner == 1:
                        msg = context.message.author.mention + ' won **$' + str(bet) \
                              + '** by defeating ' + target
                        # embed the duel results message
                        em = discord.Embed(description=msg, colour=0x607d4a)
                        await self.client.say(embed=em)

                        fighter1.update_user_money(bet)
                        # update winner's battle records... battles_won + 1 and total_winnings + X
                        fighter1.update_user_records(0, 1, bet)

                        fighter2.update_user_money(bet * -1)
                        # update loser's battle records... battles_lost + 1
                        fighter2.update_user_records(1, 0, 0)
                    elif winner == 2:
                        msg = target + ' won **$' + str(bet) + '** by defeating ' + context.message.author.mention
                        # embed the duel results message
                        em = discord.Embed(description=msg, colour=0x607d4a)
                        await self.client.say(embed=em)

                        fighter1.update_user_money(bet * -1)
                        # update loser's battle records... battles_lost + 1
                        fighter1.update_user_records(1, 0, 0)

                        fighter2.update_user_money(bet)
                        # update winner's battle records... battles_won + 1 and total_winnings + X
                        fighter2.update_user_records(0, 1, bet)
                else:
                    await self.client.say('You rejected the battle! ' + target)

            # if the target never responded
            except:
                await self.client.say('**Battle request ignored...** <a:pepehands:485869482602922021>')

    

        # if they used syntax incorrectly
        except:
            await self.client.say(context.message.author.mention +
                                  '```ml\nuse =fight like so: "=fight @user X"  -- X being amount to bet```')

    '''FLIP COIN FUNCTION'''
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.command(name='flip', description='Flip a coin to earn social status.',
                      brief='can use "=flip" or "=flip X", with X being heads or tails',
                      aliases=['f', 'flpi', 'FLIP', 'F'], pass_context=True)
    async def flip_coin(self, context, *args):
        result = random.randint(0, 1)  # flipping in "binary"
        win = 0

        # first, check if they specified a bet and they have enough money for it
        # this try/catch block will simply pass if they did not specify a bet
        try:
            user = Users(context.message.author.id)
            bet = int(args[1])
            # pass 0 to return integer version of money, see USERS.PY function
            if bet > user.get_user_money(0) or bet < 1:
                error_msg = await self.client.say("You don't have enough money for that bet..."
                                                  " <a:pepehands:485869482602922021> " + context.message.author.mention)
                await asyncio.sleep(6)
                await self.client.delete_message(error_msg)

                return
        except:
            pass

        gif = await self.client.say("https://media1.tenor.com/images/938e1fc4fcf2e136855fd0e83b1e8a5f/tenor.gif?itemid=5017733")
        await asyncio.sleep(3)
        await self.client.delete_message(gif)

        # check if they specified a guess of heads or tails
        # process if they won or not
        try:
            if args[0] in ['heads', 'HEADS']:
                if result == 1:
                    msg = '<:heads:486705167643967508> Result is **Heads**! You win! <a:worryHype:487059927731273739>'
                    win = 1
                else:
                    msg = '<:heads:486705184370589718> Result is **Tails**! You lost. <a:pepehands:485869482602922021>'
            elif args[0] in ['tails', 'TAILS']:
                if result == 1:
                    msg = '<:heads:486705167643967508> Result is **Heads**! You lost. <a:pepehands:485869482602922021>'
                else:
                    msg = '<:heads:486705184370589718> Result is **Tails**! You win! <a:worryHype:487059927731273739>'
                    win = 1
            else:
                error_msg = await self.client.say('Did you mean heads or tails? Try **=flip heads** or **=flip tails**.')
                await asyncio.sleep(6)
                await self.client.delete_message(error_msg)
                return
        except:
            # no arguments provided at all. so just give a result
            if result == 1:
                msg = '<:heads:486705167643967508> Result is **Heads**!'
            else:
                msg = '<:heads:486705184370589718> Result is **Tails**!'

        # if they specified a "guess" and "bet" that was valid, check if they won
        # note this will only pass through if "bet" was assigned through the earlier try/catch
        try:
            if win == 1:
                # triple user's bet if they win, add to account
                msg2 = '\n' + user.update_user_money(bet)
            else:
                # remove user's bet from their account if they lose
                msg2 = '\n' + user.update_user_money(bet * -1)
                # if they have $0 after that flip, give a donation dollar to discourage account re-creation
                # pass in 0 for get_user_money to return the money as integer, SEE USERS.PY
                if user.get_user_money(0) == 0:
                    msg2 += "\n** **\n_Mission failed. We'll get 'em next time. Take this **$1**._"
                    msg2 += "\n" + user.update_user_money(1)
        except:
            pass

        try:
            # embed the flip results message with money won and send
            em = discord.Embed(description=msg + msg2, colour=0x607d4a)
            await self.client.say(context.message.author.mention, embed=em)
        except:
            # embed the flip results message and send
            em = discord.Embed(description=msg, colour=0x607d4a)
            await self.client.say(context.message.author.mention, embed=em)




    '''HANGMAN main function'''

    @commands.command(name='hangman', description='Guess the word in order to survive.',
                      brief='can use "=hangman", type "stop" or "cancel" to end game',
                      aliases=['hm', 'hang', 'HM', 'HANGMAN'], pass_context=True)
    async def hangman(self, context, *args):
        hangmen = get_hangman_art()
        # initialize message to be printed if user wants category list
        hm_help = '```fix\n1. Country name\n2. Farm\n3. Camping\n4. Household items/devices\n' \
                  '5. Beach\n6. Holidays\n7. US States\n8. Sports & Hobbies```'
        wrong_guesses = 0  # global running count of incorrect guesses
        guessed_letters = ['']  # string of letters

        # pick starting word with a category, also make the string of underscores to replace later
        # check if they want to list the categories
        if args:
            if args[0] in ('help', 'HELP', 'categories', 'cats', 'h'):
                await self.client.say(context.message.author.mention + ' Categories:\n' + '```fix\n1. Country name\n'
                                                                                          '2. Farm\n3. Camping\n'
                                                                                          '4. Household items/devices\n'
                                                                                          '5. Beach\n6. Holidays\n'
                                                                                          '7. US States\n'
                                                                                          '8. Sports & Hobbies```')
                return
            try:
                correct_word, category, underscore_sequence = pick_word(int(args[0]))
            except:
                await self.client.say('Use a category number! (**Ex for Beach**: =hm 5)')
                return
        # if no category was specified in argument by user...
        else:
            # pick random category 1-8
            rand_category = random.randint(1, 8)
            correct_word, category, underscore_sequence = pick_word(rand_category)

        # print the hangman starting interface and ascii setup
        # use ** ** for empty line, discord doesn't allow empty messages.
        # also, using "".join because discord api can't  print lists.
        # we could cast, but the format would be unfriendly for the game.
        cat_msg = await self.client.say(context.message.author.mention + ' Word category is: **```fix\n' + category + '\n```**')
        art_msg = await self.client.say('\n** **\n' + hangmen[0] + '\n** **\n' + "".join(underscore_sequence))

        counter = 0
        while True:  # main game loop
            guess_prompt_msg = await self.client.say('*Guess a letter or the entire word now...*')
            guess_msg = await self.client.wait_for_message(author=context.message.author,
                                                       timeout=60)  # wait for user's guess_msg

            # make already_guessed boolean to facilitate a while loop that will loop if the user makes duplicate guess
            already_guessed = 1
            while already_guessed == 1:  # loop that will exit immediately if letter guess_msg isn't a repeat
                if guess_msg.clean_content.upper() in str("".join(guessed_letters)):
                    await self.client.delete_message(guess_msg)
                    already_guessed_msg = await self.client.say('\n*You already tried that.'
                                                                ' Guess a different letter now...*')
                    # wait for user's guess_msg now
                    guess_msg = await self.client.wait_for_message(author=context.message.author, timeout=30)
                    await self.client.delete_message(already_guessed_msg)
                else:
                    already_guessed = 0

            '''RUN WIN CHECKS AND CANCEL CHECKS NOW'''
            # run conditionals to check if they guessed entire word or they used a cancel keyword
            print(guess_msg.clean_content.upper() + ' and correct word: ' + correct_word)  # console print
            if guess_msg.clean_content.upper() == correct_word:
                await self.client.delete_message(cat_msg)
                await self.client.delete_message(art_msg)
                await self.client.delete_message(guess_prompt_msg)
                await self.client.delete_message(guess_msg)
                # pick_result_msg, underscore_seq_msg, guessed_list_msg will only exist if the game has gone at least 1 loop
                if counter > 0:
                    await self.client.delete_message(pick_result_msg)
                    await self.client.delete_message(underscore_seq_msg)
                    await self.client.delete_message(guessed_list_msg)
                await self.client.say(hangmen[wrong_guesses])
                # prepare win message string & embed it
                win_msg = '**Correct word pick** <a:worryHype:487059927731273739> ' + ' Correct word was: ' + \
                          '**' + correct_word.upper() + '**\n'
                # add WINNINGS to user's bank account now
                user = Users(context.message.author.id)
                prize = user.get_user_level(0) * 8
                win_msg += "Won **$" + str(prize) + "**... " + user.update_user_money(prize)
                em = discord.Embed(description=win_msg, colour=0x607d4a)
                await self.client.say(context.message.author.mention, embed=em)
                return

            if guess_msg.clean_content.upper() in ['STOP', 'CANCEL']:
                await self.client.delete_message(cat_msg)
                await self.client.delete_message(art_msg)
                await self.client.delete_message(guess_prompt_msg)
                await self.client.delete_message(guess_msg)
                # pick_result_msg, underscore_seq_msg, guessed_list_msg will only exist if the game has gone at least 1 loop
                if counter > 0:
                    await self.client.delete_message(pick_result_msg)
                    await self.client.delete_message(underscore_seq_msg)
                    await self.client.delete_message(guessed_list_msg)
                await self.client.say('**Cancelled** the game!! <a:pepehands:485869482602922021> Correct word was: '
                                      '**' + correct_word.upper() + '** ' + context.message.author.mention)
                return

            # quick win check, check for any underscores left to fill.
            # if unknown_letters ends up as 0 for this iteration, then there are no letters left to guess.
            num_matches, underscore_sequence = find_matches(guess_msg, correct_word, underscore_sequence)
            unknown_letters = 0
            for x in underscore_sequence:
                if x == '\u2581':  # if there is a blank underscore , the letter is still unknown to the user
                    unknown_letters += 1
            if unknown_letters == 0:
                await self.client.delete_message(cat_msg)
                await self.client.delete_message(art_msg)
                await self.client.delete_message(guess_prompt_msg)
                await self.client.delete_message(guess_msg)
                # pick_result_msg, underscore_seq_msg, guessed_list_msg will only exist if the game has gone at least 1 loop
                if counter > 0:
                    await self.client.delete_message(pick_result_msg)
                    await self.client.delete_message(underscore_seq_msg)
                    await self.client.delete_message(guessed_list_msg)
                await self.client.say(hangmen[wrong_guesses])
                # prepare win message string & embed it
                win_msg = 'You **won** the game!!' + \
                          ' <a:worryHype:487059927731273739> Correct word was: ' + \
                          '**' + correct_word.upper() + '**\n'
                # add WINNINGS to user's bank account now
                user = Users(context.message.author.id)
                prize = user.get_user_level(0) * 8
                win_msg += "Won **$" + str(prize) + "**... " + user.update_user_money(prize)
                em = discord.Embed(description=win_msg, colour=0x607d4a)
                await self.client.say(context.message.author.mention, embed=em)
                return


            # now clear all messages besides category message (cat_msg variable)
            await self.client.delete_message(art_msg)
            await self.client.delete_message(guess_prompt_msg)
            await self.client.delete_message(guess_msg)
            # pick_result_msg, underscore_seq_msg, guessed_list_msg will only exist if the game has gone at least 1 loop
            if counter > 0:
                await self.client.delete_message(pick_result_msg)
                await self.client.delete_message(underscore_seq_msg)
                await self.client.delete_message(guessed_list_msg)

            # if user's guess has zero matches in the correct word
            if num_matches == 0:
                wrong_guesses += 1  # no letters matched, so they guessed a wrong letter
                if len(guess_msg.clean_content) == 1:
                    pick_result_msg = await self.client.say('**Wrong letter pick** <a:pepehands:485869482602922021>')
                else:
                    pick_result_msg = await self.client.say('**Wrong word pick** <a:pepehands:485869482602922021>')
            # if user's guess has any matches found in the correct word
            else:
                pick_result_msg = await self.client.say('**Correct letter pick** <a:worryHype:487059927731273739>')
                # don't need "correct word pick" next because that would trigger
                # in the conditional right after the guess is taken

            # print the ascii art corresponding to wrong guesses
            if wrong_guesses < 6:
                art_msg = await self.client.say(hangmen[wrong_guesses])
            elif wrong_guesses == 6:
                await self.client.delete_message(cat_msg)
                await self.client.delete_message(pick_result_msg)
                await self.client.say(hangmen[6])
                losing_msg = '\nYou were **hanged**! <a:pepehands:485869482602922021> ' + \
                             'The word was: ' + '**' + correct_word + '**\n'
                em = discord.Embed(description=losing_msg, colour=0x607d4a)
                await self.client.say(context.message.author.mention, embed=em)
                return

            # print underscores/letters, our main interface
            underscore_seq_msg = await self.client.say('** **\n**' + "".join(underscore_sequence) + '**')
            # add last guessed letter to our guessed-so-far list
            guessed_letters, all_guessed = add_guess_to_list(guess_msg, guessed_letters)
            # print all letters guessed so far
            guessed_list_msg = await self.client.say('** ```fix\nGuessed so far: ' + all_guessed + '``` **')
            # add 1 to the main game loop's counter
            counter += 1


def setup(client):
    client.add_cog(Games(client))


def battle_decider(fighter1, fighter2, fighter1_weight, fighter2_weight):
    # choices function maps a selection to a probability, and selects one choice based off probability
    winner = choices([fighter1, fighter2], [fighter1_weight, fighter2_weight])
    print(winner)
    # choices function returning [1] or [2] so use regex to pull the integers out
    return int(re.findall("\d+", str(winner))[0])

def pick_word(cat):
    if cat == 1:
        random_word = random.choice(all_words[0:180])
        category = 'Country name'
    elif cat == 2:
        random_word = random.choice(all_words[181:319])
        category = 'Farm'
    elif cat == 3:
        random_word = random.choice(all_words[320:389])
        category = 'Camping'
    elif cat == 4:
        random_word = random.choice(all_words[390:490])
        category = 'Household items/devices'
    elif cat == 5:
        random_word = random.choice(all_words[491:603])
        category = 'Beach'
    elif cat == 6:
        random_word = random.choice(all_words[604:648])
        category = 'Holidays'
    elif cat == 7:
        random_word = random.choice(all_words[649:699])
        category = 'US States'
    elif cat == 8:
        random_word = random.choice(all_words[700:998])
        category = 'Sports & Hobbies'
    else:
        random_word = random.choice(all_words[649:699])
        category = 'US States'

    # quick band-aid fix to truncate CR in text file, COMING BACK LATER TO FIX
    length = len(random_word) - 1  # to remove carriage return, I'm not using unix format to make the list
    random_word = random_word[:length]  # truncate word with [:length] cause of carriage return in text file...

    underscore_sequence = list('')  # this will be our list of underscores
    # it will be consistently replaced by guesses

    # fill the underscore_sequence list with underscore underscore_sequencelate of the correct word
    for x in random_word:
        if x == ' ':
            underscore_sequence += '      '  # in the case of 2-word phrases, need to move everything over
        elif x == '\'':
            underscore_sequence += ' \''
        else:
            underscore_sequence += ' \u2581'  # if not a space, add: \u2581, a special underscore character.
            # using to replace by correctly guessed letters

    return random_word.upper(), category, underscore_sequence

def get_hangman_art():
    # prepare array of hangman art
    hangmen = []
    with open("db_and_words\hangmen.txt") as my_file:
        for line in my_file:
            hangmen.append(line)

    # convert respective list index-ranges to string with ''.join
    # the resulting hangmen[0-6] will represent each stage of hangman
    hangmen[0] = ''.join(hangmen[0:6])
    hangmen[1] = ''.join(hangmen[7:13])
    hangmen[2] = ''.join(hangmen[14:20])
    hangmen[3] = ''.join(hangmen[21:27])
    hangmen[4] = ''.join(hangmen[28:34])
    hangmen[5] = ''.join(hangmen[35:41])
    hangmen[6] = ''.join(hangmen[42:49])

    return hangmen

def add_guess_to_list(guess, guessed):  # accepts guess and list of all guesses
    if len(guess.clean_content) > 1:  # don't want to add whole word to guess list
        all_guessed = ''.join(map(str, guessed))
        return guessed, all_guessed
    guessed.extend(guess.clean_content.upper())  # add last guess to the list of guessed words
    guessed.extend(' ')  # add space to guessed list
    all_guessed = ''.join(map(str, guessed))  # messy syntax, convert the list into a string so bot can print it
    return guessed, all_guessed


def find_matches(guess, correct_word, underscore_sequence):
    index = 0
    num_matches = 0
    for x in correct_word:
        index += 1
        if x == ' ':
            index += 2
        # if any matches, we need to replace underscore(s) in the sequence
        # and increase the number of matches for the loop
        if guess.clean_content.upper() == x:
            # convulted index scheme due to underscore_sequence format
            underscore_sequence[index * 2 - 1] = guess.clean_content.upper()
            num_matches += 1
    return num_matches, underscore_sequence
