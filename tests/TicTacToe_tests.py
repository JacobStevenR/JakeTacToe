from JakeTacToe import ttt
from nose.tools import *
from nose import *
import pickle
import os


    





class TestsBasic(object):
  

    @classmethod
    def setup_class(self):
        """Setup instantiates two players and instantiates a game engine """
        
        self.player_x = ttt.Player("X", "test_database.db")
        self.player_o = ttt.Player("O", "test_database.db")
    
        self.game = ttt.Engine(self.player_x, self.player_o, False)

        
             
    @classmethod
    def teardown_class(self):
        """Teardown sets the player and engine variables to none."""
        
        self.player_x = None
        self.player_o = None
        self.game = None



    def setup(self):
        '''Makes sure player and game variables are initialized.'''
        
        self.game.available = [0, 1, 2, 3, 4, 5, 6, 7, 8, ]
        self.player_x.owned = []
        self.player_x.moves = []
        self.player_x.win = False
        self.player_o.owned = []
        self.player_o.moves = []
        self.player_o.win = False

        

    def teardown(self):
        pass



    def test_grid(self):
        """Makes sure the grid is correct"""
        
        assert_equal(self.game.grid, [ "[ - ]", "[ - ]", "[ - ]\n\n", "[ - ]", "[ - ]", "[ - ]\n\n", "[ - ]", "[ - ]", "[ - ]\n\n"])


    
    def test_check_for_win(self):
        """Makes sure check_for_win works"""
        
        assert_equal(self.game.winning_sets, [ [0, 3, 6], [0, 1, 2], [0, 4, 8], [1, 4, 7], [2, 4, 6], [2, 5, 8],
            [3, 4, 5], [6, 7, 8], ])

        self.player_o.owned.append(0)
        self.game.check_for_win(self.player_o)
        assert_false(self.player_o.win)

        self.player_o.owned.append(3)
        self.game.check_for_win(self.player_o)
        assert_false(self.player_o.win)

        self.player_o.owned.append(1)
        self.game.check_for_win(self.player_o)
        assert_false(self.player_o.win)

        self.player_o.owned.append(2)
        self.game.check_for_win(self.player_o)
        assert_true(self.player_o.win)
        
        self.player_x.owned = [8, 5, 2]
        self.game.check_for_win(self.player_x)
        assert_true(self.player_x.win)



    def test_check_for_draw(self):
        """Makes sure check_for_draw shows True when available is empty"""

        assert_false(self.game.check_for_draw())
        
        self.game.available = []
        assert_true(self.game.check_for_draw())
        




class TestsDatabase(object):
    
    @classmethod
    def setup_class(self):
        """Setup instantiates and instantiates a game engine """
        
        self.player_x = ttt.Player("X", "test_database.db")
        self.player_o = ttt.Player("O", "test_database.db")
    
        self.game = ttt.Engine(self.player_x, self.player_o, False)

        
             
    @classmethod
    def teardown_class(self):
        """Teardown closes the test_database connection, sets the player and engine variables to none, and deletes the test database"""

        self.player_x.close_connection()
        self.player_o.close_connection()        

        self.player_x = None
        self.player_o = None
        self.game = None

        os.remove("test_database.db")



    def setup(self):
        '''Makes sure player and game variables are initialized. Opens player connections to database.'''
        
        self.game.available = [0, 1, 2, 3, 4, 5, 6, 7, 8, ]
        self.player_x.owned = []
        self.player_x.moves = []
        self.player_x.win = False
        self.player_o.owned = []
        self.player_o.moves = []
        self.player_o.win = False

        self.player_x.open_connection()
        self.player_o.open_connection()



    def teardown(self):
        '''Drops position table for each player'''
        
        self.player_x.cursor.execute("DROP TABLE if exists positions")
        self.player_x.conn.commit()

        self.player_o.cursor.execute("DROP TABLE if exists positions")
        self.player_o.conn.commit()


    
    def test_learn(self):
        """Tests whether the learn() function adds and subtracts 0.01 from weights according to win/loss"""       

        #Initializes the database
        available = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        owned = []
        weights = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        available_pickle = pickle.dumps(available, pickle.HIGHEST_PROTOCOL)
        owned_pickle = pickle.dumps(owned, pickle.HIGHEST_PROTOCOL)
        weights_pickle = pickle.dumps(weights, pickle.HIGHEST_PROTOCOL)

        self.player_x.cursor.execute("INSERT INTO positions VALUES (?, ?, ?, ?, ?)", ("A012345678O", available_pickle, owned_pickle, weights_pickle, 0, ) )
        self.player_x.conn.commit()

        #initializes a player move, in this case..choose square 3 when position_id is A012345678O
        self.player_x.moves.append(("A012345678O", 3))

        #Runs learn() as if player won game       
        self.player_x.win = True
        self.player_x.learn()
        
        #Pulls info from database after learn()
        self.player_x.cursor.execute("SELECT * FROM positions WHERE ID = ?", ("A012345678O", ) )
        r = self.player_x.cursor.fetchone()

        win_weights = pickle.loads(r[3])
        
        #Runs learn() as if player lost game
        self.player_x.win = False
        self.player_x.learn()

        #Pulls info from database after learn() again
        self.player_x.cursor.execute("SELECT * FROM positions WHERE ID = ?", ("A012345678O", ) )
        r = self.player_x.cursor.fetchone()

        loss_weights = pickle.loads(r[3])
  
        assert_equal((1.0 + self.player_x.win_weight), win_weights[3])#tests that Player.win_weight gets added after win
        assert_equal(((1.0 + self.player_x.win_weight)-self.player_x.loss_weight), loss_weights[3])#tests that Player.loss_weight - after loss



    def test_initial_get_weights(self):
        '''Tests get_weights when there's nothing in the database yet'''
        assert_equal(self.player_x.get_weights("A012345678O", self.game.available), [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

 

    def test_get_weights(self):
        '''Tests get_weights when there's data already in database'''
        
        #Initializes the database
        available = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        owned = []
        weights = [1.0, 1.0, 1.0, 5.0, 1.0, 1.0, 1.0, 1.0]

        available_pickle = pickle.dumps(available, pickle.HIGHEST_PROTOCOL)
        owned_pickle = pickle.dumps(owned, pickle.HIGHEST_PROTOCOL)
        weights_pickle = pickle.dumps(weights, pickle.HIGHEST_PROTOCOL)

        self.player_x.cursor.execute("INSERT INTO positions VALUES (?, ?, ?, ?, ?)", ("A012345678O", available_pickle, owned_pickle, weights_pickle, 0, ) )
        self.player_x.conn.commit()

        #Calls get_weights() and makes sure it pulls the same weight at index [3] as we entered in the above piece of code
        assert_equal(self.player_x.get_weights("A012345678O", self.game.available)[3], 5.0)
        


    def test_decide_best(self):
        '''Tests that decide_best() pulls up the index to the highest number in a list'''
        pass
        
        
                
           


    

       
    
    

