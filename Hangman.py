import random
import os
from colorama import Fore, Style, init

from hangman_words import word_dict
from hangman_art import stages, logo

init(autoreset=True)

CATEGORY_MAP = {
    "1": "Animals",
    "2": "Fruits",
    "3": "Countries"
}
DIFFICULTY_MAP = {
    "1": "Easy",
    "2": "Medium",
    "3": "Hard"
}

SCORE_FILE = "score.txt"
MAX_LIVES = 6
DIVIDER = Fore.CYAN + "─" * 58


# ---------------------- UI FUNCTIONS ---------------------- #

def clear_screen():
    def clear_screen():
        if os.getenv("TERM"):
            os.system("cls" if os.name == "nt" else "clear")


def show_title():
    print(Fore.CYAN + logo)
    print(Fore.YELLOW + "=" * 58)
    print(Fore.GREEN + Style.BRIGHT + "             🎮 HANGMAN PRO 🎮")
    print(Fore.WHITE + "         A Python Terminal Game")
    print(Fore.YELLOW + "=" * 58)


def show_rules():
    print(Fore.CYAN + Style.BRIGHT + "\n========== RULES ==========")
    print(Fore.WHITE + "1. Guess one letter at a time.")
    print("2. Every wrong guess costs one life.")
    print("3. Guess the word before your lives reach 0.")
    print("4. Have fun!")
    print(Fore.CYAN + Style.BRIGHT + "===========================\n")


def show_menu():
    print(Fore.WHITE + "\nMain Menu")
    print("1. ▶  Play Game")
    print("2. 📖 Rules")
    print("3. ❌ Exit")

    return input(Fore.CYAN + "\nChoose an option (1-3): ").strip()


def show_score():
    games = wins + losses
    win_rate = f"{(wins / games * 100):.0f}%" if games else "—"

    print(Fore.CYAN + Style.BRIGHT + "\n========== SCORE ==========")
    print(Fore.GREEN + f"🏆 Wins     : {wins}")
    print(Fore.RED + f"💀 Losses   : {losses}")
    print(Fore.YELLOW + f"🎮 Games    : {games}")
    print(Fore.MAGENTA + f"📈 Win rate : {win_rate}")
    print(Fore.CYAN + Style.BRIGHT + "===========================")


# ---------------------- MENU FUNCTIONS ---------------------- #

def choose_category():
    while True:
        print(Fore.WHITE + "\nChoose Category")
        print("1. 🐶 Animals")
        print("2. 🍎 Fruits")
        print("3. 🌍 Countries")

        category = input(Fore.CYAN + "Choose (1-3): ").strip()

        if category in CATEGORY_MAP:
            return category

        print(Fore.RED + "❌ Invalid choice!")


def choose_difficulty():
    while True:
        print(Fore.WHITE + "\nChoose Difficulty")
        print("1. 😊 Easy")
        print("2. 😐 Medium")
        print("3. 😈 Hard")

        difficulty = input(Fore.CYAN + "Choose (1-3): ").strip()

        if difficulty in DIFFICULTY_MAP:
            return difficulty

        print(Fore.RED + "❌ Invalid choice!")


def get_valid_guess():
    while True:
        guess = input(Fore.CYAN + "Guess a letter: ").strip().lower()

        if len(guess) == 1 and guess.isalpha():
            return guess

        print(Fore.RED + "❌ Please enter one letter only.")


def load_score():
    """Load saved wins/losses, defaulting to 0/0 if missing or corrupt."""
    if not os.path.exists(SCORE_FILE):
        return 0, 0

    try:
        with open(SCORE_FILE, "r") as file:
            lines = file.readlines()

        return int(lines[0].strip()), int(lines[1].strip())
    except (IndexError, ValueError):
        return 0, 0


wins, losses = load_score()


def save_score():
    """Persist the current score. Fails silently (with a warning) rather
    than crashing the game if the file can't be written."""
    try:
        with open(SCORE_FILE, "w") as file:
            file.write(f"{wins}\n")
            file.write(f"{losses}\n")
    except OSError:
        print(Fore.RED + "⚠️  Couldn't save score to disk.")


# ---------------------- GAME SETUP ---------------------- #

def setup_games(category, difficulty):
    """Pick a starting life total and a random word matching the chosen
    category/difficulty, falling back to the full category if that
    difficulty bucket happens to be empty."""
    category_name = CATEGORY_MAP[category]
    selected_words = word_dict[category_name]

    difficulty_words = {
        "1": [w for w in selected_words if 3 <= len(w) <= 5],
        "2": [w for w in selected_words if 6 <= len(w) <= 8],
        "3": [w for w in selected_words if len(w) >= 9],
    }

    available_words = difficulty_words[difficulty] or selected_words
    chosen_word = random.choice(available_words)

    return MAX_LIVES, chosen_word


def show_dashboard(category_name, difficulty_name, lives, chosen_word, display,
                    correct_letters, wrong_letters):
    """Render the game state. Uses simple dividers rather than a full
    box border, since emoji render double-width in most terminals and
    would break alignment against a right-hand border."""
    clear_screen()

    print(Fore.CYAN + Style.BRIGHT + "🎮  H A N G M A N   P R O")
    print(DIVIDER)

    print(Fore.YELLOW + f"🐶 Category   : {category_name}")
    print(Fore.YELLOW + f"⭐ Difficulty : {difficulty_name}")

    life_bar = f'{"❤️ " * lives}{"🤍 " * (MAX_LIVES - lives)}'.strip()
    print(Fore.RED + f"❤️  Lives      : {life_bar} ({lives}/{MAX_LIVES})")

    games = wins + losses
    win_rate = f"{(wins / games * 100):.0f}%" if games else "—"
    print(Fore.GREEN + f"🏆 Wins: {wins}   " + Fore.RED + f"💀 Losses: {losses}   "
          + Fore.MAGENTA + f"📈 Win rate: {win_rate}")

    print(DIVIDER)
    print(stages[lives])
    print(DIVIDER)

    print(Fore.CYAN + f"💡 Hint   : Starts with '{chosen_word[0].upper()}'")
    print(Fore.CYAN + f"📏 Length : {len(chosen_word)} letters")

    print(Fore.WHITE + "\n📝 Word")
    print(Fore.YELLOW + Style.BRIGHT + "  ".join(display))

    print(Fore.MAGENTA + "\n🔤 Used Letters")
    if correct_letters or wrong_letters:
        shown = (
            [Fore.GREEN + letter.upper() for letter in sorted(correct_letters)]
            + [Fore.RED + letter.upper() for letter in sorted(wrong_letters)]
        )
        print(" ".join(shown))
    else:
        print(Fore.WHITE + "None")

    print(DIVIDER + "\n")


# ---------------------- GAME ---------------------- #

def play_game(category, difficulty):
    global wins, losses

    lives, chosen_word = setup_games(category, difficulty)
    category_name = CATEGORY_MAP[category]
    difficulty_name = DIFFICULTY_MAP[difficulty]

    correct_letters = []
    wrong_letters = []
    guessed_letters = []
    display = ["_" for _ in chosen_word]

    game_over = False

    while not game_over:

        show_dashboard(
            category_name, difficulty_name, lives, chosen_word,
            display, correct_letters, wrong_letters
        )

        guess = get_valid_guess()

        if guess in guessed_letters:
            print(Fore.YELLOW + f"You already guessed '{guess}'.")
            input(Fore.WHITE + "Press Enter to continue...")
            continue

        guessed_letters.append(guess)

        if guess in chosen_word:
            correct_letters.append(guess)
        else:
            wrong_letters.append(guess)
            lives -= 1

        display = [letter if letter in correct_letters else "_" for letter in chosen_word]

        if "_" not in display:
            wins += 1
            save_score()
            game_over = True

            clear_screen()
            print(stages[lives])
            print(Fore.GREEN + Style.BRIGHT + "\n🎉 CONGRATULATIONS! YOU WON!")
            print(Fore.YELLOW + "The word was:")
            print(Fore.CYAN + Style.BRIGHT + " ".join(chosen_word.upper()))
            input(Fore.WHITE + "\nPress Enter to continue...")

        elif lives == 0:
            losses += 1
            save_score()
            game_over = True

            clear_screen()
            print(stages[lives])
            print(Fore.RED + Style.BRIGHT + "\n💀 GAME OVER!")
            print(Fore.YELLOW + "The correct word was:")
            print(Fore.CYAN + Style.BRIGHT + " ".join(chosen_word.upper()))
            input(Fore.WHITE + "\nPress Enter to continue...")


# ---------------------- MAIN PROGRAM ---------------------- #

def main():
    while True:

        show_title()
        choice = show_menu()
        clear_screen()

        if choice == "1":
            again = "y"

            while again == "y":
                category = choose_category()
                difficulty = choose_difficulty()
                clear_screen()

                play_game(category, difficulty)
                show_score()

                while True:
                    again = input(Fore.CYAN + "\n🔁 Play Again? (y/n): ").strip().lower()
                    if again in ("y", "n"):
                        break
                    print(Fore.RED + "Please enter y or n.")

                clear_screen()

        elif choice == "2":
            clear_screen()
            show_rules()
            input(Fore.WHITE + "\nPress Enter to return to menu...")
            clear_screen()

        elif choice == "3":
            show_score()
            print(Fore.CYAN + "\n👋 Thanks for playing Hangman Pro!")
            print(Fore.YELLOW + "⭐ Don't forget to star this project on GitHub!")
            break

        else:
            print(Fore.RED + "❌ Invalid option!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(Fore.CYAN + "\n\n👋 Thanks for playing Hangman Pro!")


