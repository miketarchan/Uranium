from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import pyqtSlot, pyqtProperty, Qt, pyqtSignal

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.ContainerStack import ContainerStack

##  Model that holds container stacks. By setting the filter property the stacks held by this model can be
#   changed.
class ContainerStacksModel(ListModel):
    NameRole = Qt.UserRole + 1
    IdRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IdRole, "id")
        self._container_stacks = ContainerRegistry.getInstance().findContainerStacks()

        # Listen to changes
        ContainerRegistry.getInstance().containerAdded.connect(self._onContainerChanged)
        ContainerRegistry.getInstance().containerRemoved.connect(self._onContainerChanged)
        self._filter_dict = {}
        self._update()

    ##  Handler for container added/removed events from registry
    def _onContainerChanged(self, container):
        # We only need to update when the added / removed container is a stack.
        if isinstance(container, ContainerStack):
            self._update()

    ##  Handler for container name change events.
    def _onContainerNameChanged(self):
        self._update()

    ##  Private convenience function to reset & repopulate the model.
    def _update(self):
        self.clear()

        # Remove all connections
        for container in self._container_stacks:
            container.nameChanged.disconnect(self._onContainerNameChanged)

        self._container_stacks = ContainerRegistry.getInstance().findContainerStacks(**self._filter_dict)

        for container in self._container_stacks:
            container.nameChanged.connect(self._onContainerNameChanged)
            self.appendItem({"name": container.getName(),
                             "id": container.getId()})

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._filter_dict = filter_dict
        self._update()

    filterChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", fset = setFilter, notify = filterChanged)
    def filter(self):
        return self._filter_dict
