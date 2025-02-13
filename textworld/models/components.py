class Component:
    color = "blue"

    def __init__(self, name):
        self.name = name
        self._components = []

    def __str__(self):
        return f"[{self.color}]{self.name}[/{self.color}]"

    def attach(self, component: 'Component'):
        self._components.append(component)

    def detach(self, component: 'Component'):
        self._components.remove(component)

    def update(self) -> list[tuple['Component', dict]]:
        actions = []
        for component in self._components:
            component_actions = component.update()
            if component_actions:
                actions.extend((component, action) for action in component_actions)
        return actions

