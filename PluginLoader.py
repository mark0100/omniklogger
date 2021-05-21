# from https://gist.github.com/will-hart/5899567


class PluginBase:
    plugins = []
  
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.plugins.append(cls)
        

