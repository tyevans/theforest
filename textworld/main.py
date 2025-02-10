from textworld.models import Need, Actor, Portal, Location

if __name__ == "__main__":
    car = Location("John's Car")
    car.is_container = True

    the_forest = Location("The Forest")
    the_forest.is_container = True

    car.exits = [
        Portal("The Forest", destination=the_forest),
        Portal("The Road (North)", destination=car),
        Portal("The Road (South)", destination=car),
    ]

    the_forest = Location("The Forest")
    the_forest.is_container = True
    the_forest.exits = [
        Portal("Deeper into the Forest", destination=the_forest),
        Portal("The Car", destination=car),
    ]

    john = Actor('John Ward')
    john.location = car

    john.needs = [
        Need("Hunger", value=100, max_value=100, decay=0.1),
        Need("Bladder", value=100, max_value=100, decay=0.03),
        Need("Happiness", value=100, max_value=100, decay=0.07),
        Need("Faith", value=100, max_value=100, decay=0.00),
        Need("Sanity", value=100, max_value=100, decay=0.00),
    ]

    print(john.description)
    while True:
        cmd = input(">>> ").lower()

        match cmd:
            case "q":
                break
            case "move":
                next_portal = input("Through which portal? ").lower()
                for portal in john.location.exits:
                    if portal.name.lower() == next_portal:
                        john.location = portal.destination
                print(john.description)

            case "look":
                print(john.location.description)
            case "pray":
                print("You raise your cross. Nothing happens.")

        john.update()
        print("========================")
