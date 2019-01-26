import yaml

class ConfigParser:
    def parse_config(self, configFile):
        with open(configFile, "r") as stream:
            config = yaml.safe_load(stream)
            print(config)

            return config
                                
