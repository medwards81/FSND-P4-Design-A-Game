#Full Stack Nanodegree Project 4 - Hangman

## Introduction:
This game is based on the Udacity-Provided FSND-P4-Design-A-Game game skeleton. The code repository can  
be found on GitHub at: https://github.com/udacity/FSND-P4-Design-A-Game

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application. 
 
##Game Description:
Hangman is a simple word guessing game. Each game begins with a 'word' to guess, and individual
letter 'guesses' are registered as 'hits' or 'misses' depending on whether the guess matches one or more
letters in the word.  A player wins the game if the word is guessed correctly before the 'guess limit'
is reached. 'Guesses' are sent to the `make_move` endpoint which will reply
with either: 'hit', 'miss' or 'game over' (if the maximum number of guesses is reached).
Many different Hangman games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, word
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Word cannot contain any spaces.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game. Guess must be 
    1 character and unique from previous guesses, or a BadRequestException will be raised.
    If this causes a game to end, a corresponding Score entity will be created, and UserRecord 
    entity updated.
    
 - **get_user_games**
    - Path: 'games/user/{urlsafe_user_key}'
    - Method: GET
    - Parameters: urlsafe_user_key
    - Returns: GameForms. 
    - Description: Returns all active Games (non-completed, non-cancelled) recorded by the provided player, 
    ordered by date of game creation, descending.
    Will raise a NotFoundException if the User does not exist.
    
 - **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: VoidMessage. 
    - Description: Cancels a game. Will raise a NotFoundException if the Game does not exist. Will raise a
    BadRequestException if Game has already been completed.
      
 - **get_high_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database ordered by score, descending.  Will limit fetch to 
    number_of_results if parameter is provided.
    
 - **get_user_rankings**
    - Path: 'ranking'
    - Method: GET
    - Parameters: None.
    - Returns: UserRecordForms.
    - Description: Returns all UserRecords in the database ordered by wins, descending, then win 
    percentage, descending.
    
 - **get_game_history**
    - Path: 'game_history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key.
    - Returns: GameHistoryForm.
    - Description: Returns Game history of moves made, and resulting 'hits' or 'misses' for each move.   


##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
 
 - **UserRecord**
    - Stores User games played and resulting overall record and winning percentage. Associated
    with User model via KeyProperty.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, word, miss_count, game_over flag,
    , message, user_name, created date, guesses, hits, misses, image_uri of hangman image to display,
    guess_limit, match_count, cancelled, game_won flag).
 - **GameForms**
    - Multiple ScoreForm container.
 - **GameHistoryForm**
    - Representation of a Game's history and current state (word, word, history of moves, game_over flag,
    game_won flag).
 - **NewGameForm**
    - Used to create a new game (user_name, word)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score with additional data about the game (user_name, date, won flag,
    guess_limit, miss_count, word_count, score, word).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserRecordForm**
    - Representation of a User's overall record (user_name, games, wins, losses, win_pct).
 - **StringMessage**
    - General purpose String container.