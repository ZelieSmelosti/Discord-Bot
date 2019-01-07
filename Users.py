#!/usr/bin/env python3
from Database import Database

class Users:
    def __init__(self, id):
        self.id = id

    def add_user(self):
        hm_db = Database(self.id)
        hm_db.connect()
        return " Made account!\nYour starting :moneybag: balance: **$" + str(hm_db.insert_acct()) + "**"

    def find_user(self):
        hm_db = Database(self.id)
        hm_db.connect()
        return hm_db.find_acct()

    def delete_user(self):
        hm_db = Database(self.id)
        hm_db.connect()
        hm_db.delete_acct()
        return " Deleted account! <a:pepehands:485869482602922021>"

    def donate_money(self, amnt, receiver, receiver_string):
        self.update_user_money(amnt * -1)
        receiver.update_user_money(amnt)
        return " Donated **$" + str(amnt) + "** to " + receiver_string

    # pass 0 to 'string' to return integer version of user's money EX: 100, default is string, EX: "**$100**"
    def get_user_money(self, string=1):
        hm_db = Database(self.id)
        hm_db.connect()

        # if we want integer form of money
        if string == 0:
            return hm_db.get_money()
        # if we want the full bold discord-formatted string sequence of money
        elif string == 1:
            return "**$" + str(hm_db.get_money()) + "**"

    # pass 0 to 'string' to return integer version of user's level EX: 3, default is string, EX: "**3**"
    def get_user_level(self, string=1):
        hm_db = Database(self.id)
        hm_db.connect()

        # if we want integer form of level
        if string == 0:
            return hm_db.get_level()
        # if we want the full bold discord-formatted string sequence of money
        elif string == 1:
            return "**" + str(hm_db.get_level()) + "**"

    # returns integer of user's weapon + helmet + chest + boots levels' total
    def get_user_item_score(self):
        hm_db = Database(self.id)
        hm_db.connect()

        return hm_db.get_item_score()

    # pass 0 to 'string' to return integer version of user's battles records EX: 3, default is string, EX: "**3**"
    def get_user_battle_stats(self, string=1):
        hm_db = Database(self.id)
        hm_db.connect()

        # if we want integer form of each battle record
        if string == 0:
            return hm_db.get_battle_stats()
        # if we want the full formatted string sequence of battle records
        elif string == 1:
            # assign each variable from the sql query
            weapon_level, helmet_level, chest_level, boots_level,\
            battles_lost, battles_won, total_winnings = hm_db.get_battle_stats()

            # add full bold discord-format to each variable
            item_score = '**' + str(weapon_level + helmet_level + chest_level + boots_level) + '**'

            weapon_level = '**' + str(weapon_level) + '**'
            helmet_level = '**' + str(helmet_level) + '**'
            chest_level = '**' + str(chest_level) + '**'
            boots_level = '**' + str(boots_level) + '**'
            battles_lost = '**' + str(battles_lost) + '**'
            battles_won = '**' + str(battles_won) + '**'
            total_winnings = '**$' + str(total_winnings) + '**'

            return ('\n**STATS:**\n'
                    'Weapon:  ' + weapon_level +
                    '\nHelmet:    ' + helmet_level +
                    '\nChest:       ' + chest_level +
                    '\nBoots:       ' + boots_level +
                    '\n**Total:**       ' + item_score +
                    '\n\n**RECORDS:**\n'
                    ':crossed_swords:  lost:  ' + battles_lost +
                    '\n:crossed_swords:  won: ' + battles_won +
                    '\nTotal winnings: ' + total_winnings)

    def get_user_ticket_status(self):
        hm_db = Database(self.id)
        hm_db.connect()
        return hm_db.get_ticket_status()
    
    def update_user_money(self, amount):
        hm_db = Database(self.id)
        hm_db.connect()
        return "Your new account balance: **$" + str(hm_db.update_money(amount)) + "**"

    def update_user_level(self):
        hm_db = Database(self.id)
        hm_db.connect()
        return " Your new level: **" + str(hm_db.update_level()) + "**"

    def update_user_battle_gear(self, gear_type, level):
        hm_db = Database(self.id)
        hm_db.connect()

        if gear_type == 'weapon':
            return " Your new total item score: **" + \
                   str(hm_db.update_battle_weapon(level)) + "**"
        elif gear_type == 'helmet':
            return " Your new total item score: **" +\
               str(hm_db.update_battle_helmet(level)) + "**"
        elif gear_type == 'chest':
            return " Your new total item score: **" +\
               str(hm_db.update_battle_chest(level)) + "**"
        elif gear_type == 'boots':
            return " Your new total item score: **" +\
               str(hm_db.update_battle_boots(level)) + "**"

    def update_user_records(self, battles_lost, battles_won, total_winnings):
        hm_db = Database(self.id)
        hm_db.connect()

        return " Your new battle records: **" \
               + str(hm_db.update_battle_records(battles_lost, battles_won, total_winnings)) + "**"

    def update_user_lottery_guess(self, ticket_guess, ticket_active):
        hm_db = Database(self.id)
        hm_db.connect()

        hm_db.update_lottery_guess(ticket_guess, ticket_active)
        return "Thanks! You are ticket ID: **" + self.id + "**\n <a:pepehack:525159339007148032> " \
               "Entering your ticket guess in our database now <a:pepehack:525159339007148032>"