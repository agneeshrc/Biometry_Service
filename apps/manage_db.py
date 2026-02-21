from engine.database import list_people, remove_person

while True:
    print("\nRegistered People:")
    people = list_people()

    if not people:
        print("Database empty")
    else:
        for i, p in enumerate(people, 1):
            print(f"{i}. {p}")

    print("\nOptions:")
    print("d <name>  - delete person")
    print("q         - quit")

    cmd = input(">> ").strip()

    if cmd == "q":
        break

    if cmd.startswith("d "):
        name = cmd[2:]
        if remove_person(name):
            print(f"{name} removed.")
        else:
            print("Person not found.")
