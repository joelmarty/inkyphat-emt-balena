import signal

import configargparse

from inky_emt.app import EMTApp, Configuration
from inky_emt.inky.display import ArrivalDisplay
from inky_emt.emt.api import EMTClient

parser = configargparse.ArgParser()
parser.add_argument('--mock', '-m',
                    default=False,
                    action='store_true',
                    help='Simulate Inky using MatPlotLib')
parser.add_argument('--display-type', '-d',
                    type=str,
                    required=True,
                    env_var='DISPLAY_TYPE',
                    choices=['what', 'phat'],
                    help='Inky display type')
parser.add_argument('--display-color', '-c',
                    type=str,
                    required=True,
                    env_var='DISPLAY_COLOR',
                    choices=['red', 'black', 'yellow'],
                    help='ePaper display colour')
parser.add_argument('--refresh', '-r',
                    type=int,
                    required=False,
                    default=5,
                    env_var='REFRESH_INTERVAL',
                    help='Data refresh interval in minutes')
parser.add_argument('--stop', '-s',
                    type=str,
                    required=False,
                    default=None,
                    env_var='EMT_STOP_ID',
                    help='Bus stop')
parser.add_argument('--line', '-l',
                    type=str,
                    required=True,
                    env_var='EMT_LINE_ID',
                    help='Bus line')
parser.add_argument('--client-id', '-i',
                    type=str,
                    required=True,
                    env_var='EMT_CLIENT_ID',
                    help='EMT API Client ID')
parser.add_argument('--api-key', '-k',
                    type=str,
                    required=True,
                    env_var='EMT_PASS_KEY',
                    help='EMT API Pass Key')
args = parser.parse_args()


display = ArrivalDisplay(args.display_type, args.display_color, args.mock)
api = EMTClient(args.client_id, args.api_key)
app = EMTApp(api, display, Configuration(args.refresh, args.line, args.stop))
app.start()


def kill_handler(sig, frame):
    app.stop()


signal.signal(signal.SIGINT, kill_handler)
signal.pause()
