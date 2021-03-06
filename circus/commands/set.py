from circus.commands.base import Command
from circus.commands.util import convert_option, validate_option
from circus.exc import ArgumentError, MessageError


class Set(Command):
    """\
        Set a watcher option
        ====================

        ZMQ Message
        -----------

        ::

            {
                "command": "set",
                "properties": {
                    "name": "nameofwatcher",
                    "key1": "val1",
                    ..
                }
            }


        The response return the status "ok". See the command Options for
        a list of key to set.

        Command line
        ------------

        ::

            $ circusctl set <name> <key1> <value1> <key2> <value2>


    """

    name = "set"
    properties = ['name', 'options']

    def message(self, *args, **opts):
        if len(args) < 3:
            raise ArgumentError("number of arguments invalid")

        args = list(args)
        watcher_name = args.pop(0)
        if len(args) % 2 != 0:
            raise ArgumentError("List of key/values is invalid")

        options = {}
        while len(args) > 0:
            kv, args = args[:2], args[2:]
            kvl = kv[0].lower()
            options[kvl] = convert_option(kvl, kv[1])

        return self.make_message(name=watcher_name, options=options)

    def execute(self, arbiter, props):
        watcher = self._get_watcher(arbiter, props.pop('name'))
        action = 0
        for key, val in props.get('options', {}).items():
            new_action = watcher.set_opt(key, val)
            if new_action == 1:
                action = 1

        # trigger needed action
        watcher.do_action(action)

    def validate(self, props):
        super(Set, self).validate(props)

        options = props['options']
        if not isinstance(options, dict):
            raise MessageError("'options' property shoudl be an object")

        for key, val in options.items():
            validate_option(key, val)
