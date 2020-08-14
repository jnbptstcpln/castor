from castor.helper import Setting
from threading import Thread
from time import sleep
from .port import Port
from castor.exception import StopException, ExitException
from castor.datatype import Library as DatatypeLibrary


class Node(Thread):

    def __init__(self, id, component, settings=None):
        super().__init__()
        self.id = id
        self.component = component
        self.settings = NodeSettings(settings)
        self.running = False
        self.flow = None
        self.count = 0

        self.inputs = {}
        for port_info in self.component.inputs:
            self.inputs[port_info['name']] = Port(port_info['name'], port_info['type'])

        self.outputs = {}
        for port_info in self.component.outputs:
            self.outputs[port_info['name']] = Port(port_info['name'], port_info['type'])

        # Pass to the component a reference to the node
        self.component.node = self

    def clear_inputs(self):
        for name, port in self.inputs.items():
            port.clear()

    def start(self):
        self.running = True
        super().start()

    def stop(self):
        self.running = False

    def kill(self):
        self.running = False

    def exit(self):
        self.stop()
        if self.flow:
            self.flow.stop()

    def run(self):

        while self.running:

            try:

                if self.count >= self.settings.execution > 0:
                    self.stop()

                if len(self.inputs.keys()) > 0:
                    disconnected_inputs = 0
                    for name, port in self.inputs.items():
                        if not self.flow.transporter.is_input_connected("{}:{}".format(self.id, name)):
                            preset = self.settings.inputs.get(name, None)
                            if preset is not None:
                                port.set(preset)
                            else:
                                disconnected_inputs += 1
                                port.set(DatatypeLibrary.default(port.type))

                    # On détecte si aucun entrée n'est connecté et qu'aucune valeur n'a été spécifiée, le cas échéant
                    # on arrête l'exécution du composant
                    if disconnected_inputs >= len(self.inputs.keys()):
                        self.flow.log(
                            "Désactivation du noeud \"{}\" ({}) car aucune de ses entrées n'est utilisée"
                                .format(
                                self.id,
                                self.settings.get("component")
                            )
                        )
                        return


                kwargs = {}
                # Check if we should run the component
                should_run_component = True
                # Check if all our inputs are set
                for name, port in self.inputs.items():
                    if not port.isset:
                        #self.log("{} is not set".format(name))
                        should_run_component = False
                    else:
                        # Build the kwargs from input ports
                        kwargs[port.name] = port.value

                # Check if all our outputs are free
                for name, port in self.outputs.items():
                    if port.isset:
                        #self.log("{} is full".format(name))
                        should_run_component = False

                if should_run_component:
                    #self.log("run")
                    # Run the component with the given parameters
                    try:
                        output = self.component.func(**kwargs)
                        # count that execution
                        self.count += 1
                        # Force the output to be a tuple
                        if type(output) != tuple:
                            output = tuple([output])

                        # Set the outputs with the result
                        for i, port in enumerate(self.outputs.values()):
                            # Only set the output if it is connected to other port
                            if "{}:{}".format(self.id, port.name) in self.flow.links.keys():
                                port.set(output[i])

                        # Clear inputs
                        self.clear_inputs()

                    except StopException:
                        # The component indicate that it have to stop
                        self.stop()

                    except ExitException:
                        # The component indicate that the flow have to be stop
                        self.exit()
                else:
                    # To not overwhelm the cpu we set a tempo between iteration
                    sleep(self.settings.tempo)

            except BaseException as e:
                self.flow.error("Erreur lors de l'exécution de {} : \"{}\"".format(self.settings.get("component") ,e))


    def log(self, message):
        print("{}> {}".format(self.id, message))


class NodeSettings(Setting):
    @property
    def tempo(self):
        return self.get("tempo", 0.1)
    @property
    def inputs(self):
        return self.get("inputs", {})
    @property
    def execution(self):
        return self.get("execution", 0)



