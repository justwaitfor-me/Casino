import random
import time


def gamble(bet:int, chance:int = 44):
    print(f"Chance of winning: {chance}%")
    print(f"You start with {bet} dollars.")
    time.sleep(1)
    win = bet
    counter = 0
    while True:
        counter += 1
        print(f"{counter}/{8}")
        time.sleep(1)
        if random.random() < (chance / 100):
            print(f"You win! (+{win}$)")
            win *= 2
            if counter <= 8:
                again = input("Do you want to play again? (yes/no): ")
                if again.lower()!= "yes":
                    break
            else:
                break
                
        else:
            print(f"You lose! (-{bet}$)")
            win = 0
            break
    if win != 0:
        print(f"You won a total of {win} dollars.")
        return win
    else:
        print(f"You lost {bet} dollars.")
        return False
    


def engine(wallet: int):
    while True:
        print(f"Your current balance: {wallet} dollars.")
        bet = int(input("Enter your bet: "))
        if bet > wallet:
            print("Insufficient funds!")
        elif bet == 0:
            print("Goodbye!")
            break
        else:
            wallet -= bet
            win = gamble(bet)
            if win != False:
                wallet += win



if __name__ == "__main__":
    engine(1000)


