import os
import uuid

from requests_futures.sessions import FuturesSession

from cli.print_utils import print_warning
from utils.utils import CURRENT_VERSION, is_running_as_executable


def get_or_generate_random_id() -> str:
    random_id = ""
    create_new_id = True
    if os.path.exists("./statistics_id.txt"):
        create_new_id = False
        with open("./statistics_id.txt", "r") as f:
            data = f.read()
            # check if data is valid uuid (protection for code injection)
            print("test ID: ")
            print(data)
            try:
                random_id = str(uuid.UUID(data))
            except ValueError:
                print("VALUE-ERROR")
                create_new_id = True
    if create_new_id:
        # create file and generate random id
        random_id = str(uuid.uuid4())
        with open("./statistics_id.txt", "w") as f:
            f.write(random_id)
    return random_id


def engine_statistics(no_statistics: bool):
    if no_statistics:
        print_warning("In order to help DemaTrading.ai improve the Engine, please turn on the Engine statistics.")
        return
    session = FuturesSession()
    stats = {
        'random_id': get_or_generate_random_id(),
        'engine_version': CURRENT_VERSION,
        'executable': is_running_as_executable()
    }
    session.post('https://enginemetricspdbom7kn-logengineruns.functions.fnc.fr-par.scw.cloud', data=stats)
