import sys
from config import show_config
from formatter import pretty_print_results

def menu():
    print('=== Movie Search ===')
    print('1 — Search by keyword')
    print('2 — Search by genre and year range')
    print('3 — Show top searches')
    print('4 — Show recent unique searches')
    print('5 — (reserved)')
    print('0 — Exit')

def main():
    print('Config:', show_config())
    while True:
        menu()
        choice = input('Select option (0 to exit): ').strip()
        if choice == '0':
            print('Exiting...')
            break
        elif choice == '1':
            print('Keyword search — not yet implemented')
        elif choice == '2':
            print('Genre/year search — not yet implemented')
        elif choice == '3':
            print('Top searches — not yet implemented')
        elif choice == '4':
            print('Recent searches — not yet implemented')
        else:
            print('Unknown option, try again.')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted — exiting')
        sys.exit(0)
