import yaml

class ConfigParser:
    def parse_config(self, config_file):
        print("Parsing config from {}".format(config_file))
        with open(config_file, "r") as stream:
            config = yaml.safe_load(stream)
            print(config)

            return config
                                
