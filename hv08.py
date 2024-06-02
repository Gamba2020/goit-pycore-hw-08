import pickle
from typing import Callable, Dict, List
from datetime import datetime, timedelta, date

class Birthday:
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format")

class Record:
    def __init__(self, name):
        self.name = name
        self.phones = []
        self.birthday = None

    def add_birthday(self, value):
        self.birthday = Birthday(value)

class AddressBook:
    def __init__(self):
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def find(self, name):
        for record in self.records:
            if record.name == name:
                return record
        return None

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        is_leap_year = today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0)
        days_in_year = 366 if is_leap_year else 365

        for record in self.records:
            if record.birthday:
                birthday_this_year = record.birthday.date.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= days:
                    congratulation_date = adjust_for_weekend(birthday_this_year)
                    congratulation_date_str = congratulation_date.strftime('%d.%m.%Y')
                    upcoming_birthdays.append({"name": record.name, "congratulation_date": congratulation_date_str})
        return upcoming_birthdays

def adjust_for_weekend(birthday: date) -> date:
    if birthday.weekday() == 5:
        return birthday + timedelta(days=2)
    elif birthday.weekday() == 6:
        return birthday + timedelta(days=1)
    return birthday

def input_error(func):
    def inner(cmd, *args):
        try:
            return func(cmd, *args)
        except IndexError:
            return "Enter the argument for the command"
        except KeyError:
            return "Contact not found"
        except ValueError:
            return "Wrong format of argument"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def hello(args, book):
    return "How can I help you?"

@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.phones.append(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if record:
        record.phones = [phone]
        return "Contact updated."
    else:
        return "Contact not found."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{record.name}: phone: {', '.join(record.phones)}"
    else:
        return "Contact not found."

@input_error
def show_all(args, book: AddressBook):
    if book.records:
        return "\n".join([f"{record.name}: phone: {', '.join(record.phones)}" for record in book.records])
    else:
        return "Address book is empty."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added successfully."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{record.name}'s birthday is on {record.birthday.date.strftime('%d.%m.%Y')}."
    else:
        return "Birthday not found or not set for this contact."

@input_error
def birthdays(args, book: AddressBook):
    today = datetime.now().date()
    upcoming_birthdays = book.get_upcoming_birthdays(days=7)
    if upcoming_birthdays:
        return "\n".join([f"{record['name']}'s birthday is on {record['congratulation_date']}." for record in upcoming_birthdays])
    else:
        return "No upcoming birthdays within the next week."

operations: Dict[str, Callable] = {
    "hello": hello,
    "add": add_contact,
    "change": change_contact,
    "phone": show_phone,
    "all": show_all,
    "add-birthday": add_birthday,
    "show-birthday": show_birthday,
    "birthdays": birthdays
}

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        cmd, args = parse_input(user_input)
        if cmd in ["close", "exit"]:
            save_data(book)  # Save data before exiting
            print("Good bye!")
            break
        elif cmd in operations:
            result = operations[cmd](args, book)
            if result:
                print(result)
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
