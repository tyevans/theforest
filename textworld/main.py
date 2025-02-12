from rich import print

from textworld.map import generate_map_table
from textworld.models import TheForest
from textworld.settings import AppSettings



def main():
    settings = AppSettings()

    the_forest = TheForest(settings.map_width, settings.map_height)
    john = the_forest.john

    print(john.description)
    while True:
        cmd = input(">>> ").lower()
        if cmd == "q":
            break
        elif cmd.startswith("move"):
            next_portal = cmd[5:]
            for portal in john.location.exits:
                if portal.name.lower() == next_portal:
                    john.location = portal.destination
            print(john.description)

        elif cmd == "look":
            print(john.location.description)
        elif cmd.startswith("say"):
            actors = john.location.list_actors()
            print(f"John says '{cmd[4:]}'")
            if len(actors) == 1:
                print("There is no one around to talk to you.")
            elif len(actors) == 2:
                for _actor in actors:
                    if _actor != john:
                        print(f"{_actor} stares at you.")
            elif len(actors) >= 3:
                print("There is more than one actor around to talk to you.")
        elif cmd == "pray":
            print("You raise your cross. Nothing happens.")

        elif cmd == "map":
            print(generate_map_table(the_forest))
            continue
        else:
            print("Unknown command.")
            continue

        the_forest.update()
        print("======================")

if __name__ == "__main__":
    main()