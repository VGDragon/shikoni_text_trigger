import argparse
import re


from shikoni.ShikoniClasses import ShikoniClasses
from shikoni.tools.ShikoniInfo import start_shikoni_api
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket


from shikoni.message_types.ShikoniMessageString import ShikoniMessageString


def on_message(msg, shikoni: ShikoniClasses, trigger: str, is_trigger_at_start: bool = True):
    group_name = msg["group_name"]
    messages = msg["messages"]
    message_text = ""
    for key, message in messages.items():
        if isinstance(message, ShikoniMessageString):
            message_text += " " + str(message.message)
    if message_text.strip() != "":
        print(message_text)
    if trigger.lower() not in message_text.lower():
        message_text = ""
    elif is_trigger_at_start:
        split = re.split(trigger, message_text, flags=re.IGNORECASE)
        if len(split) > 1:
            split.pop(0)
            message_text = trigger + trigger.join(split)

    shikoni.send_to_all_clients(message=ShikoniMessageString(message_text), group_name=group_name)


def start_server(
        server_port: int,
        api_server_port: int,
        server_address: str = "0.0.0.0",
        trigger: str = "shikoni",
        is_trigger_at_start: bool = True,
        path: str = ""):

    shikoni = ShikoniClasses(
        default_server_call_function=lambda msg, shikoni: on_message(msg, shikoni, trigger, is_trigger_at_start))

    # to search for free ports as client
    api_server = start_shikoni_api(api_server_port)

    # start the websocket server
    # if start_loop is false, no messages will be handled
    shikoni.start_base_server_connection(
        connection_data=ShikoniMessageConnectorSocket().set_variables(url=server_address,
                                                                      port=server_port,
                                                                      is_server=True,
                                                                      connection_name="001",
                                                                      connection_path=path),
        start_loop=True)
    # close
    api_server.terminate()
    shikoni.close_base_server()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Skikoni Server")
    parser.add_argument("-p", "--port", dest="port", type=int, help="server port ()")
    parser.add_argument("--api", dest="api_port", type=int, help="api server port (PORT + 1)")
    parser.add_argument("-t", "--trigger", dest="trigger", type=str, help="word oth prase to trigger")
    parser.add_argument("-a", "--anywhere", dest="anywhere", action='store_true', help="set to have the trigger be anywhere")
    parser.add_argument("--path", dest="path", type=str,
                        help="the path to use for the base server. can be used for security")

    args = parser.parse_args()
    server_port = 19998
    trigger = "shikoni"
    is_trigger_at_start = True
    path = ""
    if args.port:
        server_port = args.port
    api_server_port = server_port + 1
    if args.api_port:
        api_server_port = args.api_port
    if args.trigger:
        trigger = args.trigger
    if args.anywhere:
        is_trigger_at_start = False
    if args.path:
        path = args.path

    start_server(server_port=server_port, api_server_port=api_server_port, trigger=trigger, is_trigger_at_start=is_trigger_at_start, path=path)
