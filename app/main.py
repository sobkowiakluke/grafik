# app/main.py

import sys

# Importy podmenu – zakładamy, że masz te pliki
from app.cli_employee import main as employee_menu
from app.cli_schedule import main as schedule_menu

def main():
    while True:
        print("\n=== MENU GŁÓWNE ===")
        print("1. Pracownicy")
        print("2. Grafiki")
        print("0. Wyjście")

        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            # Wejście do menu pracowników
            employee_menu()
        elif choice == "2":
            # Wejście do menu grafików
            schedule_menu()
        elif choice == "0":
            print("Koniec programu.")
            sys.exit(0)
        else:
            print("Nieprawidłowa opcja. Spróbuj ponownie.")

if __name__ == "__main__":
    main()
