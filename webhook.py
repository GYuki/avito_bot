import requests
import sys

from parserapp.bot_settings import url_token

if __name__ == "__main__":
    if len(sys.argv) == 2:
        delete_webhook = url_token + "deletewebhook"
        set_webhook = url_token + "setwebhook?url=" + sys.argv[1]
        requests.get(delete_webhook)
        requests.get(set_webhook)
    else:
        print("Веб-хук не был установлен")
        sys.exit(1)
