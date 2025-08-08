def get_config():
    try:
        import configparser
    except ImportError:
        import ConfigParser as configparser  # Python 2 fallback
    config = configparser.ConfigParser()
    config.read('utils/config.ini')
    return config
