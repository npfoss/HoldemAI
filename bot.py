# Nate Foss and Eli Lifland , Texas Holdem bot , Summer 2015
from __future__ import *
from sys import stderr, stdin, stdout
from poker import Card, Hand, Pocket, Table
from itertools import combinations
from math import sqrt
class Bot(object):
#---Main bot class
    def __init__(self):
#-------Bot constructor
#       Add data that needs to be persisted between rounds here.
        self.pre_flop_raise_rate = 0.0
        self.post_flop_raise_rate = 0.0
        self.post_flop_fold_rate = 0.0
        self.pre_flop_raises = 0
        self.post_flop_raises = 0
        self.post_flop_folds = 0
        self.pre_flop_raise_chances = 0
        self.post_flop_raise_chances = 0
        self.post_flop_fold_chances = 0
        self.last_table_strength = 0.0
       # self.opponent_has_slow_played = False
        self.has_straight_or_flush = False
        self.we_raised = False
        self.slow_play = False
        self.table_length = 0
       # in case we play an all in bot
        self.facing_all_in_bot = False
       # self.opponent_play_log = {}
        self.settings = {}
        self.match_settings = {}
        self.game_state = {}
        self.pocket = None
        self.bots = {
            'me': {},
            'opponent': {}
        }
    def run(self):
#-------Main loop
#       Keeps running while begin fed data from stdin.
#       Writes output to stdout, remember to flush.
        while not stdin.closed:
            try:
                rawline = stdin.readline()
                # End of file check
                if len(rawline) == 0:
                    break
                line = rawline.strip()
                # Empty lines can be ignored
                if len(line) == 0:
                    continue
                
                parts = line.split()
                command = parts[0].lower()

                if command == 'settings':
                    self.update_settings(parts[1:])
                    pass
                elif command == 'match':
                    self.update_match_info(parts[1:])
                    pass
                elif command.startswith('player'):
                    self.update_game_state(parts[0], parts[1], parts[2])
                    pass
                elif command == 'action':
                    stdout.write(self.make_move(parts[2]) + '\n')
                    stdout.flush()
                    pass
                else:
                    stderr.write('Unknown command: %s\n' % (command))
                    stderr.flush()
            except EOFError:
                return
#---Takes in all input from engine beginning with Settings, stores all info in set
    def update_settings(self, options):
#       Updates game settings
        key, value = options
        self.settings[key] = value
#---Takes in all input from engine beginning with Match, stores all info in set
    def update_match_info(self, options):
#       Updates match information
        key, value = options
        if key == 'table':
            self.we_raised = False #reset at beginning of round
            self.table_length = len(self.parse_cards(value)) 
            value = Table(self.parse_cards(value))
        self.match_settings[key] = value
#---Takes in all other info, updates state of game
    def update_game_state(self, player, info_type, info_value):
#       Updates game state
        # Checks if info pertains self
        if player == self.settings['yourBot']:
            
            # Update bot stack
            if info_type == 'stack':
                self.table_length = 0 # sets table length to 0 as default, changes in update_match_info if receives table info
                self.bots['me']['stack'] = int(info_value)

            # Remove blind from stack
            elif info_type == 'post':
                self.bots['me']['stack'] -= int(info_value)

            # Update bot cards
            elif info_type == 'hand':
                self.bots['me']['pocket'] = Pocket(self.parse_cards(info_value))

            # Round winnings, currently unused
            elif info_type == 'wins':
                self.we_raised = False #reset at beginning of round

            elif info_type == 'call':
                self.we_raised = False
            
            elif info_type == 'check':
                self.we_raised = False            

            elif info_type == 'raise':
                self.we_raised = True
            
            elif info_type == 'fold':
                self.we_raised = False
            else:
                stderr.write('Unknown info_type: %s\n' % (info_type))

        else:
            if info_type == 'call':
                if 0 < self.table_length < 5:
        #           self.opponent_play_log[self.table_length] += [info_type]
                   self.bots['opponent']['lastmove'] = 2.0
                if self.table_length == 0:
                   self.pre_flop_raise_chances += 1
                   self.pre_flop_raise_rate = self.pre_flop_raises / self.pre_flop_raise_chances
                else:
                   self.post_flop_fold_chances += 1
                   self.post_flop_fold_rate = self.post_flop_folds / self.post_flop_fold_chances
            
            if info_type == 'check':
                if 0 < self.table_length < 5:
       #            self.opponent_play_log[self.table_length] += [info_type]
                   self.bots['opponent']['lastmove'] = -1.0    
                if self.table_length == 0:
                   self.pre_flop_raise_chances += 1
                   self.pre_flop_raise_rate = self.pre_flop_raises / self.pre_flop_raise_chances
                else:
                   self.post_flop_raise_chances += 1
                   self.post_flop_raise_rate = self.post_flop_raises / self.post_flop_raise_chances

            if info_type == 'raise':
                if 0 < self.table_length < 5:
       #            self.opponent_play_log[self.table_length] += [info_type]
                   self.bots['opponent']['lastmove'] = 3.0 + int(self.we_raised) * 1.5 #more scared if they reraised
                if self.table_length == 0:
                   self.pre_flop_raise_chances += 1
                   self.pre_flop_raises += 1
                   self.pre_flop_raise_rate = self.pre_flop_raises / self.pre_flop_raise_chances
                elif self.we_raised:
                   self.post_flop_fold_chances += 1
                   self.post_flop_fold_rate = self.post_flop_folds / self.post_flop_fold_chances
                else:
                   self.post_flop_raise_chances += 1
                   self.post_flop_raises += 1
                   self.post_flop_raise_rate = self.post_flop_raises / self.post_flop_raise_chances
            
            if info_type == 'fold':
        #        if 0 < self.table_length < 5:
        #           self.opponent_play_log[self.table_length] += [info_type]
                if self.table_length == 0:
                   self.pre_flop_raise_chances += 1
                   self.pre_flop_raise_rate = self.pre_flop_raises / self.pre_flop_raise_chances
                else:
                   self.post_flop_fold_chances += 1
                   self.post_flop_folds += 1
                   self.post_flop_fold_rate = self.post_flop_folds / self.post_flop_fold_chances                
            # Update opponent stack
            if info_type == 'stack':
                self.bots['opponent']['stack'] = int(info_value)

            # Remove blind from opponent stack
            elif info_type == 'post':
                self.bots['opponent']['stack'] -= int(info_value)

            # Opponent hand on showdown, currently unused
            elif info_type == 'hand':
                pass

            # Opponent round winnings, currently unused
            elif info_type == 'wins':
                self.we_raised = False #reset at beginning of round
                
#---Main method to output what we want to do.
    def make_move(self, timeout):
#       Checks cards and makes a move
        small_stack = (self.bots['me']['stack'] < (15 * int(self.match_settings['bigBlind'])))
        tiny_stack = (self.bots['me']['stack'] < (5 * int(self.match_settings['bigBlind'])))
        pre_flop_raise_modifier = 0.0 #number between -1 and 1
        post_flop_fold_modifier = 0.0 #see above
        post_flop_raise_modifier = 0.0#see above
        if int(self.match_settings['round']) > 5:
           self.facing_all_in_bot = self.pre_flop_raise_rate > .9 and self.post_flop_raise_rate > .9
        if int(self.match_settings['round']) > 5:
            if self.table_length == 0:
                pre_flop_raise_modifier = self.pre_flop_raise_rate - .15 #constant is average value, then multiply to scale pos, neg values
                if pre_flop_raise_modifier > 0:
                   pre_flop_raise_modifier = pre_flop_raise_modifier * 100 / 85
                else:
                   pre_flop_raise_modifier = pre_flop_raise_modifier * 100 / 15
            else:
                post_flop_raise_modifier = self.post_flop_raise_rate - .22
                if post_flop_raise_modifier > 0:
                   post_flop_raise_modifier = post_flop_raise_modifier * 50 / 39
                   post_flop_raise_modifier = sqrt(post_flop_raise_modifier)
                else:
                   post_flop_raise_modifier = post_flop_raise_modifier * 50 / 11
                post_flop_fold_modifier = self.post_flop_fold_rate - .4
                if post_flop_fold_modifier > 0:
                   post_flop_fold_modifier = post_flop_fold_modifier * 5 / 3
                else:
                   post_flop_fold_modifier = post_flop_fold_modifier * 5 / 2
        hand_strength = 0 #number always at least 0 and rarely greater than 1
        amount_to_call = float(self.match_settings['amountToCall'])
        on_button = (self.match_settings['onButton'] == self.settings['yourBot'])
        pot = float(self.match_settings['maxWinPot'])
        pot_odds = amount_to_call/pot
        #stderr.write(str(amount_to_call))
        #stderr.write(str(pot))
        #stderr.write(str(pot_odds))
        self.slow_play = False
        improved_table_strength = False
        bluff = False
        if self.table_length == 0:
            #pre-flop valuation
            pocket = self.bots['me']['pocket'].getCards()
            hand_strength = self.preFlopEval(pocket)
        else:
            #post-flop valuation
            pot_odds = sqrt(sqrt(pot_odds)) / (2 * sqrt(sqrt(.5)))
            #stderr.write(str(pot_odds) + '\n')
            pocket = self.bots['me']['pocket'].getCards()
            pocket_combos = list(combinations(pocket,2))
            table_combos = list(combinations(self.match_settings['table'].getCards(),3))
            hand_strength = self.postFlopEval(pocket_combos, table_combos)
            values = sorted(['23456789TJQKA'.find(card.getValue()) for card in pocket])
            self.has_straight_or_flush = .4 <= hand_strength < .59
            table_strength = self.tableStrength(table_combos, values, hand_strength)  
            old_hs = hand_strength #old hand strength. only used against allin bots
            if self.table_length == 3 and table_strength >= .5:
                improved_table_strength = True
            elif table_strength >= .5 and self.last_table_strength < .5:
                improved_table_strength = True
            if self.table_length < 5 and improved_table_strength and hand_strength >= .5:
                self.slow_play = True  
            self.last_table_strength = table_strength
            if int(self.bots['me']['stack']) > pot * 10 and improved_table_strength and hand_strength < .5 and post_flop_fold_modifier > 0 and (not self.slow_play):
                bluff = True
                stderr.write('decided to bluff in round ' + self.match_settings['round'] + '\n')
            #opponent_slow_play_modifier = 0.0
            #opponent_slow_play_modifier = improved_table_strength * self.opponent_has_slow_played
            #stderr.write(str(hand_strength)
            #now use hand strength to determine move         
            hand_strength = hand_strength / table_strength
        if self.facing_all_in_bot:
           stderr.write("found an all in bot! it's round " + self.match_settings['round'] + '\n')
           #preflop
           if self.table_length == 0:
              if amount_to_call == 0:
                 return 'check 0'
              if hand_strength > .37:
                 return 'call 0'
           #postflop
           elif old_hs > .27 and hand_srength > .6:
              return 'raise 9999' #higher than max bet, but will be adjusted by engine, dw
           elif amount_to_call == 0:
              return 'check 0'
           return 'fold 0'
        if amount_to_call > 0:#if there was a bet (aka check is not an option)
            they_re_raised = self.we_raised
            if self.table_length > 0:
                if hand_strength > .85 - post_flop_raise_modifier * .15 + .05 * (improved_table_strength or they_re_raised) - (small_stack + tiny_stack) * .15:
                   return 'raise '  + str(int(float(self.match_settings['amountToCall'])*2))
                hand_strength += ((not self.has_straight_or_flush) and self.futureEval(pocket_combos, list(combinations(self.match_settings['table'].getCards(),2)))) * (5 - self.table_length) * (not small_stack)#don't want to call based on future when we have small stack. so it reflects the number of cards still to come
            if pot_odds + .1 * (self.table_length > 0) + they_re_raised * .20 - post_flop_raise_modifier * .23 - ((not they_re_raised) and post_flop_raise_modifier < 0 and improved_table_strength and post_flop_raise_modifier * .20) - ( (not on_button) and pre_flop_raise_modifier * .20) > hand_strength:
               return 'fold 0'
            return 'call 0'
        else:#if no bet -- can do anything --- plays semi-agressively (seems to work better with bots i think)
            lastMoveModifier = 0.0
            if (not on_button) and (self.table_length > 3):
               if self.bots['opponent']['lastmove'] > 0:
                   lastMoveModifier = (.10 + post_flop_fold_modifier * .10) * self.bots['opponent']['lastmove'] #if there is a higher post_flop_fold modifier, the opponent calling or reraising means more
               elif not improved_table_strength:
                   lastMoveModifier = (.06 + post_flop_raise_modifier * .12) * self.bots['opponent']['lastmove'] #if there is a higher post_flop_raise modifier, the opponent checking means more
                   if lastMoveModifier > 0.0:
                      lastMoveModifier = 0.0
            if bluff:
               return 'raise ' + str(int(pot))
            if self.slow_play or hand_strength <= .47 + improved_table_strength * .15 * ((not on_button) or self.table_length < 5) - (self.table_length > 0) * (small_stack + tiny_stack) * .12 + (self.table_length == 0) * .24 - (.10 + post_flop_raise_modifier * .25) * int(on_button) + lastMoveModifier:
               return 'check 0'
   #        return 'raise ' + str(int(float(self.match_settings['bigBlind'])*(hand_strength + 1.5)))
            return 'raise ' + str(int(pot*hand_strength*hand_strength*1.4))
            
#---returns the strength of BEST POSSIBLE HAND given the table (on a scale of 0 to 1)
    def tableStrength(self, table_combos, pocket_values, our_hand_strength):
         best_hand_strength = 0.3
         flush_is_at_all_possible = False
         straight_is_at_all_possible = False
         for combo in table_combos:
             hand_strength = 0
             values = sorted(['23456789TJQKA'.find(card.getValue()) for card in combo])
             #First we'll look for pairs/trips/quads
             # Get card value counts
             value_count = {value: values.count(value) for value in values}
             # Sort value counts by most occuring
             sorted_value_count = sorted([(count, value) for value, count in value_count.items()], reverse = True)
             # Get all kinds (e.g. four of a kind, three of a kind, pair)
             kinds = [value_count[0] for value_count in sorted_value_count]
             # Get values for kinds
             kind_values = [value_count[1] for value_count in sorted_value_count]
             # Now I will add arbitrary numbers for having kinds, can be changed later.
             #now we'll look at suitedness
             suits = sorted(card.getSuit() for card in combo)
             # Get card suit counts
             suit_count = {suit: suits.count(suit) for suit in suits}
             # Sort suit counts by most occuring
             sorted_suit_count = sorted([(count, suit) for suit, count in suit_count.items()], reverse = True)
             # Get all suit matches (e.g. four of a kind, three of a kind, pair)
             suit_kinds = [suit_count[0] for suit_count in sorted_suit_count]     
             #3 of a kind check
             hand_strength = 0.3 + values[2]/130       
             #straight check
             straight_is_possible = ((values[2] - values[0] <= 4) and (kinds[0] == 1))
             if straight_is_possible:
                straight_is_at_all_possible = True
                hand_strength = (0.4 + (values[2]+(4-(values[2]-values[0])))/130)  
                if hand_strength > (.4 + 12/130):
                   hand_strength = .4 + 12/130
             #flush check
             flush_is_possible = (suit_kinds[0] == 3)
             if flush_is_possible:
                if values[2] == 12:
                   self.has_straight_or_flush = True
                flush_is_at_all_possible = True
                hand_strength = 0.5 + 12/130
                if 0.5 <= our_hand_strength < 0.6:
                   hand_strength += .08 #to safeguard a bit against losing to higher flushes
             if straight_is_at_all_possible and flush_is_at_all_possible and our_hand_strength < .4:
                hand_strength = (0.65 + (values[2]+(4-(values[2]-values[0])))/130)  
                if hand_strength > (.65 + 12/130):
                   hand_strength = .65 + 12/130
             #full house check is same as four of a kind check haha
             #four of a kind check
             if kinds[0] == 2:
                if .3 <= our_hand_strength < .4 and self.table_length < 5:
                   self.slow_play = True
                new_hand_strength = 0.7 + kind_values[0]/130
                if (kind_values[0] in pocket_values):
                   new_hand_strength -= .20
                if kinds[1] == 2:
                   new_hand_strength += .1 - .1 * (kind_values[1] in pocket_values)
                if new_hand_strength > hand_strength:
                   hand_strength = new_hand_strength
             if kinds[0] == 3:
                if kind_values[0] not in pocket_values:
                   hand_strength = 0.92 + kind_values[0]/130
             if hand_strength > best_hand_strength:
                best_hand_strength = hand_strength
         return best_hand_strength
         
#   returns a number to be added to hand_strength based on how promising the future looks
    def futureEval(self, pocket_combos, table_combos):#NOTE** table_combos is combos of 2 in this instance ONLY
        flush_pos = False
        straight_pos = set() #cards that would give you a straight
        for pocket in pocket_combos:
            for table in table_combos:
                combo = pocket + table
                values = sorted(['23456789TJQKA'.find(card.getValue()) for card in combo])
                #flush?
                if not flush_pos:#no use checking if already found one
                   suits = sorted(card.getSuit() for card in combo)
                   suit_count = {suit: suits.count(suit) for suit in suits}
                   sorted_suit_count = sorted([(count, suit) for suit, count in suit_count.items()], reverse = True)
                   suit_kinds = [suit_count[0] for suit_count in sorted_suit_count]
                   flush_pos = (suit_kinds[0] == 4)
                   #if flush_pos:
                   #   stderr.write('flush' + str(suits))
                #straights?
                if len(straight_pos) < 5:#a little more pruning
                   #straight check
                   values = sorted(['23456789TJQKA'.find(card.getValue()) for card in combo])
                   value_count = {value: values.count(value) for value in values}
                   sorted_value_count = sorted([(count, value) for value, count in value_count.items()], reverse = True)
                   kinds = [value_count[0] for value_count in sorted_value_count]
                   if ((values[3] - values[0] <= 4) and (kinds[0] == 1)) or (kinds[0] == 1 and (values[3] == 12) and (values[2] - values[0] <= 3) and (values[0] == 0)):#straight possibility
                      #find the missing card(s)
                      for i in range(3):
                          if (values[i+1] - values[i]) > 1:
                             straight_pos = straight_pos.union({values[i] + 1})
                             break
                      else:
                          if values[3] == 12:#fake open ended
                             if values[0] == 0:#ace as lowest
                                straight_pos = straight_pos.union({5})
                             else:#ace as highest
                                straight_pos = straight_pos.union({10})
                          else:
                             straight_pos = straight_pos.union({values[0] - 1}, {values[3] + 1})
        #stderr.write(str(straight_pos) + '   ' + str(len(straight_pos)))
        return int(flush_pos) * .08 + len(straight_pos) * .02
        
#---Takes in string of cards, outputs list of card objects
    def parse_cards(self, cards_string):
#       Parses string of cards and returns a list of Card objects
        return [Card(card[1], card[0]) for card in cards_string[1:-1].split(',')]
        
#---Takes in hand of four, returns hand strength -- int value [0,1]
    def preFlopEval(self, pocket):
       return self.evaluatePocket(pocket)
       
#---Takes in list of possible pocket (hand of four) combinations and table (shared cards) combinations, returns hand strength -- int value [0,1]
    def postFlopEval(self, pocket_combos, table_combos): 
       #find best hand
       best_hand = Hand(pocket_combos[0]+table_combos[0])
       for pocket in pocket_combos:
          for table in table_combos:
             five_cards = pocket + table
             hand = Hand(five_cards)
             if hand > best_hand:
                best_hand = hand
       hand_rank = best_hand.getRank()
       return self.evaluateHand(hand_rank)
       
#---Takes in hand_rank as performed in poker.py, returns hand strength -- int value [0,1]
    def evaluateHand(self, hand_rank):
       #figure out actual number for best hand
       if hand_rank[0] == '0': #no pair
          return 0
       if hand_rank[0] == '1': #pair
          return .1 + int(hand_rank[1])/130 #max value for rank[1] is 12
       if hand_rank[0] == '2': #two pair
          return .2 + (int(hand_rank[1])+int(hand_rank[2]))/240 #similar to above
       if hand_rank[0] == '3': #3 of a kind
          return .3 + int(hand_rank[1])/130
       if hand_rank[0] == '4': #straight
          return .4 + int(hand_rank[1])/130
       if hand_rank[0] == '5': #flush
          return .5 + int(hand_rank[1])/130
       if hand_rank[0] == '6': #full house
          return .6 + int(hand_rank[1])/130
       if hand_rank[0] == '7': #four of a kind
          return .7 + int(hand_rank[1])/130
       if hand_rank[0] == '8': #straight flush
          return .85 + int(hand_rank[1])/120
       if hand_rank[0] == '9': #royal flush
          return 1
          
#---takes in hand of four (pocket), returns hand strength
    def evaluatePocket(self, pocket):
       pocket_strength = 0
       #similar to rank_five_cards in poker.py
       values = sorted(['23456789TJQKA'.find(card.getValue()) for card in pocket])
       #find average card value
       sum_of_values = 0
       for value in values:
         sum_of_values += value
       average_value = sum_of_values / 4
       pocket_strength += average_value / 100
       #First we'll look for pairs/trips/quads
       # Get card value counts
       value_count = {value: values.count(value) for value in values}
       # Sort value counts by most occuring
       sorted_value_count = sorted([(count, value) for value, count in value_count.items()], reverse = True)
       # Get all kinds (e.g. four of a kind, three of a kind, pair)
       kinds = [value_count[0] for value_count in sorted_value_count]
       # Get values for kinds
       kind_values = [value_count[1] for value_count in sorted_value_count]
       # Now I will add arbitrary numbers for having kinds, can be changed later.
       for kind in kind_values:
          kind+=1 #1-13 is easier to deal with than 0-12; should get some credit for a 2
       if kinds[0] == 4: #quads
          pocket_strength += .09 + kind_values[0]/100
       elif kinds[0] == 3: #trips
          pocket_strength += .12 + kind_values[0]/100 
       elif kinds[0] == 2 and kinds[1] == 2: #two pair
          pocket_strength += .25 + (kind_values[0]/50 + kind_values[1]/100) # more weight to higher pair
       elif kinds[0] == 2: #just a pair
          pocket_strength += .15 + kind_values[0]/50
       #now we'll look at suitedness
       suits = sorted(card.getSuit() for card in pocket)
       # Get card suit counts
       suit_count = {suit: suits.count(suit) for suit in suits}
       # Sort suit counts by most occuring
       sorted_suit_count = sorted([(count, suit) for suit, count in suit_count.items()], reverse = True)
       # Get all suit matches (e.g. four of a kind, three of a kind, pair)
       kinds = [suit_count[0] for suit_count in sorted_suit_count]
       #Now it's time to add arbitrary numbers again! :p
       if kinds[0] == 4:
          pocket_strength += .07 #not that good because single suited but less chance of hitting flush
       elif kinds[0] == 3:
          pocket_strength += .15 #see above
       elif kinds[0] == kinds[1] == 2:
          pocket_strength += .30
       elif kinds[0] == 2:
          pocket_strength += .15
       #finally we'll look at straight potential
       '''
       Here I'm going to implement the straight potential part of a system Edward Hutchison,
       a poker pro, developed.  The write-up for the whole system can be found here:
       http://erh.homestead.com/omaha.html
       ''' 
       #The following code looks long and complicated but it's really just implementing
       #the strategy at the website above
       hand_contains_ace = False
       if values[3] == 12:
          hand_contains_ace = True
       value_differences = [(values[n+1]-values[n]) for n in range(3)]
       total_of_differences = 0
       number_of_cards = 1
       for difference in value_differences:
          if difference == 0:
             continue
          new_total_of_differences = total_of_differences + difference
          if new_total_of_differences < 5:
             number_of_cards+=1
             total_of_differences = new_total_of_differences
          elif 0 < total_of_differences < 5:
             if number_of_cards == 2:
                pocket_strength += (.13 - (total_of_differences-1)*.033) 
             if number_of_cards == 3:
                pocket_strength += (.3 - (total_of_differences-2)*.033) 
             number_of_cards = 1
          else:
             total_of_differences = 0   
       else:
          if total_of_differences < 5:  
             if number_of_cards == 2:
                pocket_strength += (.13 - (total_of_differences-1)*.033) 
             if number_of_cards == 3:
                pocket_strength += (.3 - (total_of_differences-2)*.033)
             if number_of_cards == 4:
                pocket_strength += (.42 - (total_of_differences-3)*.033)
       #yay, we finished! :D except aces :p
       if hand_contains_ace:
          values[3] = 0
          for n in range(3):
            values[n]+=1
          values = values[3:] + values[:3] 
          value_differences = [(values[n+1]-values[n]) for n in range(3)] 
          for difference in value_differences:
             if difference == 0:
                continue
             new_total_of_differences = total_of_differences + difference
             if new_total_of_differences < 5:
                number_of_cards+=1
                total_of_differences = new_total_of_differences
             elif 0 < total_of_differences < 5:
                if number_of_cards == 2:
                   pocket_strength += (.13 - (total_of_differences-1)*.033) 
                if number_of_cards == 3:
                   pocket_strength += (.3 - (total_of_differences-2)*.033)
                break 
             else:
                break  
          else:
             if total_of_differences < 5: 
                pocket_strength += (.42 - (total_of_differences-3)*.033)
       return pocket_strength + .1
       
if __name__ == '__main__':
    '''
    Not used as module, so run
    '''
    Bot().run()
