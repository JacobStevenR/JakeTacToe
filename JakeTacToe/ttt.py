#During random play, no weights or available moves are saved into the database.
import sqlite3
import pickle
import random
import bisect
from sys import argv

if __name__ == '__main__':
    script, player_x_database, player_o_database, game_type = argv #game_type should = "X", "O", or "random".



class Engine(object):
    
    def __init__(self, player_x, player_o, compete=True):
        
        self.grid = [ "[ - ]", "[ - ]", "[ - ]\n\n", "[ - ]", "[ - ]", "[ - ]\n\n", "[ - ]", "[ - ]", "[ - ]\n\n"]
        
        self.winning_sets = [ [0, 3, 6], [0, 1, 2], [0, 4, 8], [1, 4, 7], [2, 4, 6], [2, 5, 8],
            [3, 4, 5], [6, 7, 8], ]

        self.available = [0, 1, 2, 3, 4, 5, 6, 7, 8, ]

        self.player_x = player_x

        self.player_o = player_o

        self.compete = compete
    


    def open_connection(self):
        self.conn = sqlite3.connect("ttt_game_data.db")
        self.conn.text_factory = str
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor() 

        self.cursor.execute('''CREATE TABLE if not exists wins
            (x_wins, o_wins, draws, games_played)''')
        self.conn.commit()



    def close_connection(self):
        self.conn.close()



    def reset_board(self):
        del self.available[:]
        self.available = [0, 1, 2, 3, 4, 5, 6, 7, 8, ]
        del self.grid[:]
        self.grid = [ "[ - ]", "[ - ]", "[ - ]\n\n", "[ - ]", "[ - ]", "[ - ]\n\n", "[ - ]", "[ - ]", "[ - ]\n\n"]



    def create_position_id(self, available, owned):
        available.sort()
        owned.sort()

        string = "A"
        
        for a in available:
            string += str(a)

        string += "O"

        for o in owned:
            string += str(o)

        return string            
            
               


    def check_for_win(self, player):
        """Checks to see if the set of numbers contains 3 of any winning_set"""
        
        match = 0
	
        for ws in self.winning_sets:
            for num in player.owned:
                if num in ws:
                    match += 1

            if match == 3:
                for x in self.grid:
                    print x,
		
                print "%s is the WINNER!" % player.symbol
		player.win = True
                break

            else:
                match = 0



    def check_for_draw(self):
        if self.available:
            return False
        else:
            print "DRAW!"
            return True



    def print_grid(self):
        for x in self.grid:
            print x,



    def query_player(self, player, position_id):
        """Retrieves the given player's move"""

        if self.compete:  #If self.compete is True, computer picks best choice  

            if player.computer:
                input = player.decide_best(position_id, self.available)    
                return input
            else:
                input = raw_input("\n[ 0 ] [ 1 ] [ 2 ]\n\n[ 3 ] [ 4 ] [ 5 ]\n\n[ 6 ] [ 7 ] [ 8 ]  Player %s's turn: " % player.symbol)  
                return input
        else: #if self.compete is False, computers pick random moves
        
            input = player.random_move(position_id, self.available)
            return input
            



    def play_round(self, player):
        """Plays a round"""
        
        #prints grid
        print "\n\n\n"
        
        self.print_grid()

        #create a unique position ID
        position_id = self.create_position_id(self.available, player.owned)
        
        input = self.query_player(player, position_id)

        if int(input) in self.available:
            # Updates grid, removes choice from available list, adds choice to player's owned list
            self.grid[int(input)] = self.grid[int(input)].replace("-", player.symbol)
            self.available.remove(int(input))
            player.owned.append(int(input))

            #Sorts available and owned to avoid bugs
            self.available.sort()
            player.owned.sort()

            #Appends (position_id, choice) tuple to player's owned list 
            player.moves.append((position_id, int(input)), )

        elif int(input) not in self.available:
            print "That space is already taken. Please try again... "
            self.play_round(player)

        else:
            print "That is not a valid choice.  Please try again... "
            self.play_round(player)




    def play_game(self, repeat):
        """Plays a number of games"""

        x_wins = 0
        o_wins = 0
        draws = 0
        games_played = 0

        self.open_connection()

        for i in range(repeat):
            games_played += 1
            while True:
                self.play_round(player_x)
                self.check_for_win(player_x)
                
                if player_x.win:
                    x_wins += 1
                    player_x.learn()
                    player_o.learn()
                    break
 
                draw = self.check_for_draw()                
                
                if draw:
                    draws += 1
                    break

                self.play_round(player_o)
                self.check_for_win(player_o)

                if player_o.win:
                    o_wins += 1
                    player_o.learn()
                    player_x.learn()
                    break
                
                draw = self.check_for_draw()

                if draw:
                    draws += 1
                    break

            self.reset_board()
            player_x.reset_player()
            player_o.reset_player()

        print "X Wins: %d" % x_wins
        print "O Wins: %d" % o_wins
        print "Draws: %d" % draws
        print "Games Played: %d" % games_played

        self.cursor.execute("INSERT INTO wins VALUES (?, ?, ?, ?)", (x_wins, o_wins, draws, games_played, ))
        self.conn.commit()

        self.close_connection()
    



class Player(object):
    
    def __init__(self, symbol, database, computer=True):
        
        self.symbol = symbol

        self.database = database

        self.conn = ''         

        self.cursor = ''
   
        self.computer = computer

        self.owned = []

        self.moves = []

        self.win = False



    def reset_player(self):
            self.win = False
            del self.moves[:]
            del self.owned[:]



    def open_connection(self):
        self.conn = sqlite3.connect(self.database)
        self.conn.text_factory = str
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE if not exists positions
                             (ID, available, owned, weights, times_played)''')
        self.conn.commit()



    def close_connection(self):
        self.conn.close()



    def default_weights(self, available):
        """Returns list of equal weights of same length as available"""
        
        weights = []
        
        for w in range(0, len(available)):
            weights.append(1.0)

        return weights
    

    def get_weights(self, position_id, available):
        """Using position_ID and available, pulls weights from a database or creates a default set of weights"""
        
        self.cursor.execute("SELECT * FROM positions WHERE ID = ?", (position_id,))
        r = self.cursor.fetchone()

        if r:
            weights = pickle.loads(r[3])
            
            times_played = r[4] + 1.0         
            self.cursor.execute("UPDATE positions SET times_played = ? WHERE ID = ?", (times_played, position_id, ))
            self.conn.commit()

            return weights

        else:
            weights = self.default_weights(available)
            # pickles weights, owned, and available and saves to database w/ appropriate position_id
            available_pickle = pickle.dumps(available, pickle.HIGHEST_PROTOCOL)
            owned_pickle = pickle.dumps(self.owned, pickle.HIGHEST_PROTOCOL)
            weights_pickle = pickle.dumps(weights, pickle.HIGHEST_PROTOCOL)

            times_played = 1

            self.cursor.execute("INSERT INTO positions VALUES(?, ?, ?, ?, ?)", (position_id, available_pickle, owned_pickle, weights_pickle, times_played, ))
            self.conn.commit()
    
            return weights          

    
    def cdf(self, weights):
        """Cumulative Distribution Function"""

        total = sum(weights)
        result = []
        cumsum = 0
        for w in weights:
            cumsum += w
            result.append(cumsum/total)
        return result

    

    def choice(self, available, weights):
        """Taking available and weights, chooses an item from available in a probabalistic way"""

        assert len(available) == len(weights)
        cdf_vals = self.cdf(weights)
        x = random.random()
        idx = bisect.bisect(cdf_vals, x)
        return available[idx]



    def random_move(self, position_id, available):
        """Chooses a move at random"""
        weights = self.default_weights(available)
        save_weights = self.get_weights(position_id, available)#This is just run so the position gets saved into the database
        input = self.choice(available, weights)

        return input



    def decide_best(self, position_id, available):
        """Determines best move according to weights"""
        available.sort()

        weights = self.get_weights(position_id, available)
        choice_idx = weights.index(max(weights))

        input = available[choice_idx]

        return input



    def learn(self):
        """Updates weights for each move made"""
        
        for position_id, move in self.moves:
            self.cursor.execute("SELECT * FROM positions WHERE ID = ?", (position_id,))
            r = self.cursor.fetchone()
            
            available = pickle.loads(r[1])
            weights = pickle.loads(r[3])
            
            idx = available.index(move)
            
            if self.win:
                weights[idx] += 0.01
            else: 
                weights[idx] -= 0.01
                if weights[idx] < 0.01:
                    weights[idx] = 0.01

            weights_pkl = pickle.dumps(weights, pickle.HIGHEST_PROTOCOL)
            self.cursor.execute("UPDATE positions SET weights = ? WHERE ID = ?", (weights_pkl, position_id, ))
            self.conn.commit()     



if __name__ == '__main__':


    repeat = int(raw_input("How many games do you want to play?\n"))

    if game_type == "X":
        player_x = Player("X", player_x_database, False)
        player_o = Player("O", player_o_database)
    
        player_x.open_connection()
        player_o.open_connection()
    
        game = Engine(player_x, player_o) 
        game.play_game(repeat)
    
        player_x.close_connection()
        player_o.close_connection()

    elif game_type == "O":
        player_x = Player("X", player_x_database)
        player_o = Player("O", player_o_database, False)

        player_x.open_connection()
        player_o.open_connection()

        game = Engine(player_x, player_o)
        game.play_game(repeat)

        player_x.close_connection()
        player_o.close_connection()

    else:
        player_x = Player("X", player_x_database)
        player_o = Player("O", player_o_database)
    
        player_x.open_connection()
        player_o.open_connection()

        game = Engine(player_x, player_o, False)
        game.play_game(repeat)

        player_x.close_connection()
        player_o.close_connection()

   

