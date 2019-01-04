#!/usr/bin/env python3
import random
import asyncio
import re
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
    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command(name='rob', description='Steal money from others', brief='can use =steal',
                      aliases=['thief', 'thieve', 'ROB', 'steal', 'mug'], pass_context=True)
    async def rob(self, context, *args):
        # create instance of the user starting the robbery
        robber = Users(context.message.author.id)
        # declare 30% fail chance, used to calculate chance of failing rob
        fail_chance = 30
        level_difference = 0
        # pick a random user in the server to rob
        # target variable will function as the victim user's "english" name
        target = random.choice(list(context.message.server.members))
        # make an instance of the target
        victim = Users(target.id)
        victim_id = target.id
        counter = 1

        # if randomly chosen victim has an account, and robber specified NO target, account for any level difference
        if not args and victim.find_user() == 1:
            level_difference = (robber.get_user_level(0) - victim.get_user_level(0))

        # if they specified a rob target, change the random target to their specified target
        if args:
            # retrieve rob target
            target = args[0]
            # use regex to extract only the user-id from the user targeted
            victim_id = int(re.findall("\d+", target)[0])
            victim = Users(victim_id)
            # higher fail chance, 35%, if they want to specify a rob target
            fail_chance = 35
            # if the target doesn't have an account, change fail chance back to 30% and the target will reroll next loop
            if victim.find_user() == 0:
                fail_chance = 30
                await self.client.say(context.message.author.mention +
                                      " Your rob target doesn't have an account."
                                      "\n**Rerolling** rob target now!")

        # while the user to rob is yourself, re-roll the target
        # while the user to rob does not have an account in the database, re-roll the target
        # while the user to rob is not within 3 levels of yourself, re-roll the target
        while victim_id == context.message.author.id or victim.find_user() == 0 or level_difference > 3:
            # only try 60 members in the user's server
            # otherwise if the user was the sole player with an account in the discord server, infinite while loop
            # this part is inefficient, but only way I can think of right now with discord's functionality
            if counter == 60:
                await self.client.say('No users found to rob...')
                return
            target = random.choice(list(context.message.server.members))
            # create a new instance of victim each loop
            # in order to check if the reroll has an account in database
            victim = Users(target.id)
            victim_id = target.id
            counter += 1
            if victim.find_user() == 1:
                level_difference = abs(robber.get_user_level(0) - victim.get_user_level(0))

        # calculate random integer 1-100
        # if the result is within 1 through fail chance, they failed the rob
        if fail_chance >= random.randint(1, 100) >= 1:
            robber_level = robber.get_user_level(0)

            bail = int(robber_level * 5.3)
            robber.update_user_money(bail * -1)
            await self.client.say('<a:policesiren2:490326123549556746> :oncoming_police_car: '
                                  '<a:policesiren2:490326123549556746>\n'
                                  '<a:monkacop:490323719063863306>         <a:monkacop:490323719063863306>\n**'
                                  '' + str(target) + '** dodged and the police shot you in the process.\n'
                                  'You spent **$' + str(bail) + '** to bail out of jail.')
            return

        # we passed the dodge check, so reward thief with prize and bonus prize
        victim_money = victim.get_user_money(0)
        victim_level = victim.get_user_level(0)
        robber_level = robber.get_user_level(0)

        # the victim will only lose the prize, not the bonus prize
        prize = int(victim_level * 8.2)
        bonus_prize = int(robber_level * 24.4)

        # balancing mechanic, only let victims lose money by robbers when they are greater than -50x their level in money
        if victim_money > (victim_level * -50):
            # subtract prize from victim
            victim.update_user_money(prize * -1)
        # reward robber with prize and bonus prize
        robber.update_user_money(prize + bonus_prize)
        await self.client.say('**Success!** <:poggers:490322361891946496> '
                              'You robbed **$' + str(prize) + '** (+**$' + str(bonus_prize)
                              + '**) from **' + str(target) + '**')


    '''BATTLE FUNCTION'''
    @has_account()
    @commands.command(name='fight', description='Battle another user in your server',
                      brief='can use "fight @user X --X being amount to bet"',
                      aliases=['battle', 'BATTLE', 'FIGHT'], pass_context=True)
    async def battle_user(self, context, *args):
        # retrieve how much the fighter is betting on the battle
        if len(args) == 2:
            bet = int(args[1])
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
            await self.client.say(target + ', you were challenged for **$' + str(bet) +
                                  '**\n:crossed_swords: Type **yes** to accept this battle. :crossed_swords: ')

            # made this check function with the help of discord API documentation
            # it will be called below to check if the confirmation response to fight is from fighter2
            def fighter2check(msg):
                return int(msg.author.id) == fighter2_id

            # (try to) wait for a battle acceptance from other user
            try:
                confirm = await self.client.wait_for_message(timeout=60, check=fighter2check)
                if confirm.clean_content.upper() == 'YES':
                    # have to use 2 messages to enlarge the emojis
                    await self.client.say('**Commencing battle!** Fight will conclude in 10 seconds...')
                    await self.client.say('<a:worryfight1:493220414206509056> <a:worryfight2:493220431738699786>')
                    await asyncio.sleep(10)
                    # get the difference in player level between each player
                    difference = fighter1.get_user_level(0) - fighter2.get_user_level(0)

                    # if fighter1 is higher level or same level
                    if difference >= 0:
                        # decide winner, with fighter 1 having better odds (unless same level)
                        winner = battle_decider(1, 2, difference)

                    # if fighter2 is higher level
                    elif difference < 0:
                        # make level difference positive before calling our function
                        difference *= -1
                        # decide winner, with fighter 2 having better odds
                        winner = battle_decider(2, 1, difference)

                    # check if they tried to exploit the code by spending all their money during the battle
                    if fighter1.get_user_money(0) < bet or fighter2.get_user_money(0) < bet:
                        await self.client.say(
                            context.message.author.mention + " One of you spent money while battling...")
                        return

                    # check who the winner was returned as
                    # update account balances respectively
                    if winner == 1:
                        await self.client.say(context.message.author.mention + ' won **$' + str(bet)
                                              + '** by defeating ' + target)
                        fighter1.update_user_money(bet)
                        # update winner's battle records... battles_won + 1 and total_winnings + X
                        fighter1.update_user_records(0, 1, bet)

                        fighter2.update_user_money(bet * -1)
                        # update loser's battle records... battles_lost + 1
                        fighter2.update_user_records(1, 0, 0)
                    else:
                        await self.client.say(target + ' won **$' + str(bet) +
                                              '** by defeating ' + context.message.author.mention)
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
                                  '```ml\nuse =fight like so: **=fight @user X**      -- X being amount to bet```')

    '''FLIP COIN FUNCTION'''
    @commands.command(name='flip', description='Flip a coin to earn social status.',
                      brief='can use "=flip" or "=flip X", with X being heads or tails',
                      aliases=['f', 'flpi', 'FLIP', 'F'], pass_context=True)
    async def flip_coin(self, context, *args):
        result = random.randint(0, 1)  # flipping in "binary"
        win = 0

        # first, check if they specified a bet and they have enough money for it
        if args:
            user = Users(context.message.author.id)
            bet = int(args[1])
            # pass 0 to return integer version of money, see USERS.PY function
            if bet > user.get_user_money(0) or bet < 1:
                await self.client.say("You don't have enough money for that bet..."
                                      " <a:pepehands:485869482602922021> " + context.message.author.mention)
                return


        # check if they specified a guess of heads or tails
        # process if they won or not
        try:
            if args[0] == 'heads':
                if result == 1:
                    msg = '<:heads:486705167643967508> Result is **Heads**! You win! <a:worryHype:487059927731273739>'
                    win = 1
                else:
                    msg = '<:heads:486705184370589718> Result is **Tails**! You lost. <a:pepehands:485869482602922021>'
            else:
                if result == 1:
                    msg = '<:heads:486705167643967508> Result is **Heads**! You lost. <a:pepehands:485869482602922021>'
                else:
                    msg = '<:heads:486705184370589718> Result is **Tails**! You win! <a:worryHype:487059927731273739>'
                    win = 1
        except:
            # no arguments provided at all. so just give a result
            print("No argument specified for betting on the coin side.")
            if result == 1:
                msg = '<:heads:486705167643967508> Result is **Heads**!'
            else:
                msg = '<:heads:486705184370589718> Result is **Tails**!'
        await self.client.say(msg + ' ' + context.message.author.mention)

        # if they specified a "guess" and "bet" that was valid, check if they won
        # note this will only pass through if "bet" was assigned through the earlier try/catch
        try:
            if win == 1:
                # triple user's bet if they win, add to account
                msg = user.update_user_money(bet)
            else:
                # remove user's bet from their account if they lose
                msg = user.update_user_money(bet * -1)
                # if they have $0 after that flip, give a donation dollar to discourage account re-creation
                # pass in 0 for get_user_money to return the money as integer, SEE USERS.PY
                if user.get_user_money(0) == 0:
                    msg += "\n** **\n_The gambling gods have shown mercy on your bankrupt existence, and given you **$1**_"
                    msg += "\n" + user.update_user_money(1)
            await self.client.say(msg)
        except:
            print("No bet specified")

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
            correct_word, category, underscore_sequence = pick_word(int(args[0]))

        # if no category was specified in argument by user...
        else:
            # pick random category 1-8
            rand_category = random.randint(1, 8)
            correct_word, category, underscore_sequence = pick_word(rand_category)

        await self.client.say(context.message.author.mention + ' Word category is: **```fix\n' + category + '```**')
        await self.client.say('** **')
        # print the hangman ascii setup
        await self.client.say(hangmen[0])
        await self.client.say('** **\n' + "".join(underscore_sequence))
        # use ** ** for empty line, discord doesn't allow empty messages.
        # also, using "".join because discord api can't  print lists.
        # we could cast, but the format would be unfriendly for the game.

        while True:  # main game loop
            await self.client.say('*Guess a letter or the entire word now...*')
            guess = await self.client.wait_for_message(author=context.message.author,
                                                       timeout=60)  # wait for user's guess
            already_guessed = 1
            while already_guessed == 1:  # loop that will exit immediately if letter guess isn't a repeat
                if guess.clean_content.upper() in str("".join(guessed_letters)):
                    await self.client.purge_from(context.message.channel, limit=1)
                    await self.client.say('\n*You already tried that. Guess a different letter now...*')
                    # wait for user's guess now
                    guess = await self.client.wait_for_message(author=context.message.author, timeout=30)
                    # account for that extra message, so delete last one
                    await self.client.purge_from(context.message.channel, limit=1)
                else:
                    already_guessed = 0

            '''RUN WIN CHECKS AND CANCEL CHECKS NOW'''
            # run conditionals to check if they guessed entire word or they used a cancel keyword
            print(guess.clean_content.upper() + ' and correct word: ' + correct_word)  # console print
            if guess.clean_content.upper() == correct_word:
                await self.client.purge_from(context.message.channel, limit=6)
                await self.client.say(hangmen[wrong_guesses])
                await self.client.say('**Correct word pick** <a:worryHype:487059927731273739>')
                await self.client.say('You **won** the game!! <a:worryHype:487059927731273739> Correct word was:'
                                      ' **' + correct_word.upper() + '** ' + context.message.author.mention)
                # add $200 to user's bank account now
                user = Users(context.message.author.id)
                await self.client.say(user.update_user_money(200))
                return

            if guess.clean_content.upper() in ['STOP', 'CANCEL']:
                await self.client.purge_from(context.message.channel, limit=6)
                await self.client.say('**Cancelled** the game!! <a:pepehands:485869482602922021> Correct word was: '
                                      '**' + correct_word.upper() + '** ' + context.message.author.mention)
                return

            # quick win check, check for any underscores left to fill.
            # if unknown_letters ends up as 0 for this iteration, then there are no letters left to guess.
            num_matches, underscore_sequence = find_matches(guess, correct_word, underscore_sequence)
            unknown_letters = 0
            for x in underscore_sequence:
                if x == '\u2581':  # if it's an underscore still, the letter is still unknown to the user
                    unknown_letters += 1
            if unknown_letters == 0:
                await self.client.purge_from(context.message.channel, limit=6)
                await self.client.say(hangmen[wrong_guesses])
                await self.client.say('You **won** the game!! <a:worryHype:487059927731273739> Correct word was: '
                                      '**' + correct_word.upper() + '** ' + context.message.author.mention)
                # add $500 to user's bank account now
                user = Users(context.message.author.id)
                await self.client.say(user.update_user_money(300))
                return

            # clear up last 6 messages, only 5 if first round, to reduce bot spam
            if len(guessed_letters) == 1:
                await self.client.purge_from(context.message.channel, limit=5)
            else:
                await self.client.purge_from(context.message.channel, limit=6)

            # print whether they guessed a correct letter or not
            if num_matches == 0:
                wrong_guesses += 1  # no letters matched, so they guessed a wrong letter
                if len(guess.clean_content) == 1:
                    await self.client.say('**Wrong letter pick** <a:pepehands:485869482602922021>')
                else:
                    await self.client.say('**Wrong word pick** <a:pepehands:485869482602922021>')
            else:
                await self.client.say('**Correct letter pick** <a:worryHype:487059927731273739>')
                # don't need "correct word pick" next because that would trigger
                # in the conditional right after the guess is taken

            # print the ascii art corresponding to wrong guesses
            if wrong_guesses < 6:
                await self.client.say(hangmen[wrong_guesses])
            elif wrong_guesses == 6:
                await self.client.say(hangmen[6])
                await self.client.say('\nYou were **hanged**! <a:pepehands:485869482602922021> The word was: '
                                      '**' + correct_word + '**\n' + context.message.author.mention)
                return

            # print underscores/letters, our main interface
            await self.client.say('** **\n**' + "".join(underscore_sequence) + '**')
            # add last guessed letter to our guessed-so-far list
            guessed_letters, all_guessed = add_guess_to_list(guess, guessed_letters)
            # print all letters guessed so far
            # all_guessed is just the string version of guessed_letters (a list version)
            await self.client.say('** ```fix\nGuessed so far: ' + all_guessed + '``` **')


def setup(client):
    client.add_cog(Games(client))


def battle_decider(higher_odds, lower_odds, difference):
    # the maximum player level difference is 9
    # choices function maps a selection to a probability, and selects one choice based off probability
    if difference == 1:
        winner = choices([higher_odds, lower_odds], [.52, .48])
    elif difference == 2:
        winner = choices([higher_odds, lower_odds], [.54, .46])
    elif difference == 3:
        winner = choices([higher_odds, lower_odds], [.56, .44])
    elif difference == 4:
        winner = choices([higher_odds, lower_odds], [.58, .42])
    elif difference == 5:
        winner = choices([higher_odds, lower_odds], [.60, .40])
    elif difference == 6:
        winner = choices([higher_odds, lower_odds], [.62, .38])
    elif difference == 7:
        winner = choices([higher_odds, lower_odds], [.64, .36])
    elif difference == 8:
        winner = choices([higher_odds, lower_odds], [.66, .34])
    elif difference == 9:
        winner = choices([higher_odds, lower_odds], [.68, .32])
    else:
        winner = choices([higher_odds, lower_odds], [.50, .50])

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
