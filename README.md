# JakeTacToe

JakeTacToe is a simple Tic Tac Toe game that is played in the linux terminal. 

There are two modes of play:

-Random play, where two computer players face off and make random moves, keeping track of which moves lead to a win and which moves lead to a loss.

-Competitive play, where the computer plays against a human opponent and chooses whichever move has led to the most wins according to its memory.

The more games that the computer has played, the better it will play against its human opponent.


To play, enter the directory "JakeTacToe."

The file, ttt.py, is the game file.  Call the ttt.py file like a normal python file and pass three arguments, a database name for player X, a database name for player O, and game type (X, O, random).

For example, to make the computer play a series of random games in order to learn, you can enter the following:

    '''python ttt.py xbrain.db obrain.db random'''

The xbrain.db and obrain.db are sqlite3 databases where game and move information is stored.  These can be named anything you want. Both X's and O's database can be the same if desired.

After entering this, you will be asked how many games you want to play.  Enter any amount you want.  It usually takes about 100k games for the computer to achieve almost perfect play.

If you want to play against the computer, replace the random argument with either "X" or "O", depending on which player you would like to play as.  X always goes first and O always goes second.

For example, if you want to play against the computer as player O, you can type into the command line:

    '''python ttt.py database.db database.db O'''



Testing is done with Nose.  To test, enter into package directory and type:

    '''nosetests'''

Keep in mind that this is a very early and rough version of this package.  There are still many bugs to work out.



