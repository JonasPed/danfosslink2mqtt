from .configparser import ConfigParser
import argparse
import danfosslink2mqtt.logic as logic
import danfosslink2mqtt.config as config

def parse_config():
    parser = argparse.ArgumentParser("DanfossLink2MQTT")
    parser.add_argument("--config", action = "store", default = "/config.yaml")

    args = parser.parse_args()

    cfg = ConfigParser().parse_config(args.config)
    config.CONFIG = cfg

def main():
    parse_config()

    logic.do_logic()

if __name__ == "__main__":
    main()

