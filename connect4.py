import random
import math


def check_move(board, turn, col, pop):
    # Check column exists:
    if 0 > col > 6:
        print("Specified column number is out of bounds! (0 to 6)")
        return False

    # Case where player wishes to pop:
    if pop:
        disc_at_bottom = board[col]
        if disc_at_bottom != turn:
            if not disc_at_bottom:  # Empty => 0, => falsy
                print("There are no discs in this column!")
            else:
                print("The disc at the bottom of this column does not belong to you!")
            return False
    # Case where column is full:
    else:
        disc_at_top = board[col-7]  # negative indexing
        if disc_at_top:  # Players' turn number always > 0, => truthy
            print("This column is already full!")
            return False

    return True


def check_move_silently(board, turn, col, pop):
    # Same logic as above; for computer to find moves silently
    if 0 > col > 6:
        return False
    if pop:
        disc_at_bottom = board[col]
        if disc_at_bottom != turn:
            return False
    else:
        disc_at_top = board[col-7]
        if disc_at_top:
            return False
    return True


def apply_move(board, turn, col, pop):
    copy_of_board = board.copy()
    max_row_index = (len(copy_of_board) // 7) - 1
    # Case where player wants to pop:
    if pop:
        rows_to_shift = max_row_index - 1  # top row is a special case
        for row in range(rows_to_shift):
            copy_of_board[7 * row + col] = copy_of_board[7 * (row + 1) + col]  # move down by 1
        copy_of_board[7 * max_row_index + col] = 0  # clear top row
    # Case where player does not want to pop:
    else:
        for row in range(max_row_index):
            if not copy_of_board[7 * row + col]:  # empty slot
                copy_of_board[7 * row + col] = turn
                break

    return copy_of_board


def check_row(row):
    for column in range(4):
        if not row[column]:
            continue  # skip iteration, if 0 (empty)
        if (
            row[column] == row[column + 1] and
            row[column] == row[column + 2] and
            row[column] == row[column + 3]
        ):
            return row[column]
    return 0


def check_victory(board, who_played):
    max_row_index = (len(board) // 7) - 1
    # Note: top from player POV; it's the bottom of the list
    third_row_from_top = max_row_index - 2  # 4 slots from top of the column; -1 for exclusion in range
    winners = set()  # player(s) with 4 in-a-row
    # check horizontal
    for row in range(max_row_index):
        result = check_row(board[row * 7:(row + 1) * 7 - 1])
        if result:  # check_row != 0 => 4 in-a-row
            winners.add(result)

    # check vertical
    for column in range(7):  # 7 columns in every board
        for row in range(third_row_from_top):
            if not board[7 * row + column]:
                break  # skip rest of column, if 0 (empty)
            if (
                board[7 * row + column] == board[7 * (row + 1) + column] and
                board[7 * row + column] == board[7 * (row + 2) + column] and
                board[7 * row + column] == board[7 * (row + 3) + column]
            ):
                winners.add(board[7 * row + column])

    # check forward-sloping diagonal
    for column in range(4):  # 7 columns in every board; can't get 4 in a row if col of left-most disc > 3
        for row in range(third_row_from_top):
            if not board[7 * row + column]:
                continue  # skip iteration, if 0 (empty)
            if (
                board[7 * row + column] == board[7 * (row + 1) + column + 1] and
                board[7 * row + column] == board[7 * (row + 2) + column + 2] and
                board[7 * row + column] == board[7 * (row + 3) + column + 3]
            ):
                winners.add(board[7 * row + column])

    # check backward-sloping diagonal
    for column in range(3, 7):  # 7 columns in every board; can't get 4 in a row if col of left-most disc < 3
        for row in range(third_row_from_top):
            if not board[7 * row + column]:
                continue  # skip iteration, if 0 (empty)
            if (
                board[7 * row + column] == board[7 * (row + 1) + column - 1] and
                board[7 * row + column] == board[7 * (row + 2) + column - 2] and
                board[7 * row + column] == board[7 * (row + 3) + column - 3]
            ):
                winners.add(board[7 * row + column])

    if not winners:
        return 0
    # More than one winner => last-played player lost
    if len(winners) > 1:
        winners.discard(who_played)
    return winners.pop()


def get_random_move(board, turn):
    # Generate a random set of column number and true/false
    while True:
        column = random.randint(0, 6)
        pop = bool(random.randint(0, 1))
        if check_move_silently(board, turn, column, pop):
            break
    return column, pop


def get_direct_wins(board, turn):
    moves = []
    # trial and error
    for column in range(7):
        temp_board = apply_move(board, turn, column, False)
        if check_victory(temp_board, turn) == turn:
            moves.append((column, False))
        temp_board = apply_move(board, turn, column, True)
        if check_victory(temp_board, turn) == turn:
            moves.append((column, True))
    return moves


def computer_move(board, turn, level):
    if level == 1:
        return get_random_move(board, turn)

    # check for direct win
    direct_win_moves = get_direct_wins(board, turn)
    if direct_win_moves:  # if not empty, get first result
        return direct_win_moves[0]

    # list of moves that allow direct win for opponent
    opponent = 1 if turn == 2 else 2
    moves_to_avoid = get_direct_wins(board, opponent)
    if not moves_to_avoid:  # no possible way to prevent direct wins
        return get_random_move(board, turn)
    while True:
        move = get_random_move(board, turn)
        if move not in moves_to_avoid:
            break
    return move


def display_board(board):
    print("---------------------------------------")
    print("Game Board:")
    max_row_index = (len(board) // 7) - 1
    # Cast to string:
    board_in_strings = [str(element) for element in board]
    # Format the board list for console output
    # Spit the board into rows, delimited by spaces:
    split_board = [" ".join(board_in_strings[row * 7:(row + 1) * 7]) for row in range(max_row_index + 1)]
    # Reverse the order, so that row with index 0 is displayed on the bottom:
    split_board.reverse()
    print("\n".join(split_board))  # one row per line
    print("---------------------------------------")


def get_valid_response(question):
    # helper function for handling yes/no questions
    valid_answers = ("y", "yes", "true", "n", "no", "false")
    while True:
        answer = input(question)
        if answer.lower() in valid_answers:
            return answer
        print("That is not a valid response! Please try again.")


def parse_as_boolean(answer):
    affirmative_answers = ("y", "yes", "true")
    return True if answer.lower() in affirmative_answers else False


def get_rows():
    answer = input("How many rows do you want the game board to have? (6 to 10) ")
    try:
        rows = int(answer)
        if rows not in range(6, 11):
            raise ValueError("Value out of acceptable range")
    except ValueError:
        print("That is not a valid row number, please try again!")
        return get_rows()
    return rows


def get_difficulty_level():
    answer = input("How hard would you like the game to be? (1-2, higher is more difficult) ")
    try:
        difficulty = int(answer)
        if difficulty not in range(1, 3):
            print("We thank you for your interest in unconventional gameplay modes.")
            print("Unfortunately, the developers of this game has not offered this difficulty level yet.")
            print("Please try a different difficulty level!")
            raise ValueError("Value out of acceptable range")
    except ValueError:
        print("That is not a valid difficulty level, please try again!")
        return get_difficulty_level()
    return difficulty


def get_column():
    answer = input("Pick a column (0-6): ")
    try:
        column = int(answer)
        if column not in range(0, 7):
            raise ValueError("Value out of acceptable range")
    except ValueError:
        print("That is not a valid column number, please try again!")
        return get_column()
    return column


def get_move(board, turn):
    while True:
        pop_choice = get_valid_response("Would you like to pop a disc? (y/n) ")
        is_pop = parse_as_boolean(pop_choice)
        column = get_column()
        if check_move(board, turn, column, is_pop):
            break
    return column, is_pop


def display_victory_message(board, winner):
    display_board(board)
    print(f"Player {winner} has won the game. The game has ended.")
    print("Congratulations!")


def handle_player_turn(board, turn):
    display_board(board)
    print(f"Player {turn}'s Turn!")
    column, is_pop = get_move(board, turn)
    new_board = apply_move(board, turn, column, is_pop)
    victory_status = check_victory(new_board, turn)
    if victory_status:
        display_victory_message(new_board, victory_status)
        exit(0)
    return new_board


def menu():
    # Set-up empty game board
    config_rows = get_valid_response("Would you like to change the size of the game board (default 6) ? (y/n) ")
    number_of_rows = get_rows() if parse_as_boolean(config_rows) else 6
    board = [0] * (7 * number_of_rows)

    # Ask for game type
    game_type = get_valid_response("Would you like to play against the computer? (y/n) ")
    is_computer = parse_as_boolean(game_type)
    if is_computer:
        print("The computer will be Player 2.")

        # Ask for difficulty level
        difficulty = get_difficulty_level()

    # Start the game
    print()
    print("Game Started!")
    print("---------------------------------------")
    is_running = True
    while is_running:
        # Player 1
        board = handle_player_turn(board, 1)

        # Player 2
        if is_computer:
            print("The computer has made a move:")
            column, is_pop = computer_move(board, 2, difficulty)
            board = apply_move(board, 2, column, is_pop)
            victory_status = check_victory(board, 2)
            if victory_status:
                if victory_status == 2:
                    print("The computer has won. Better luck next time!")
                else:
                    print("Amazing! You've beat the computer! Congrats!")
                return
        else:
            board = handle_player_turn(board, 2)


if __name__ == "__main__":
    print("Connect4 with Pop Out! (2 Players)")
    print("---------------------------------------")
    menu()
    exit(0)
