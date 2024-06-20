import datetime
import yapsy.PluginFileLocator
import yapsy.PluginManager
import yapsy.IPlugin


class PluginCollector(object):
    def collect(self):
        raise NotImplemented


class YapsyPluginCollector(PluginCollector):
    def __init__(self, plugin_directories, plugin_locator=None):
        self.plugin_manager = yapsy.PluginManager.PluginManager(directories_list=plugin_directories,
                                                                plugin_locator=plugin_locator)

    def collect(self):
        plugins = []
        self.plugin_manager.collectPlugins()
        for plugin in self.plugin_manager.getAllPlugins():
            plugins.append(plugin.plugin_object)
        return plugins


class YapsyRegExPluginCollector(YapsyPluginCollector):
    def __init__(self, plugin_directories, regexp):
        locator = yapsy.PluginFileLocator.PluginFileLocator()
        locator.setAnalyzers([yapsy.PluginFileLocator.PluginFileAnalyzerMathingRegex(self._analyzer_name(), regexp)])
        super(YapsyRegExPluginCollector, self).__init__(plugin_directories, locator)

    def _analyzer_name(self):
        return "YapsyPluginReAnalyzer%s" % datetime.datetime.now()


class SubclassPluginCollector(PluginCollector):
    def __init__(self, base_class):
        self.base_class = base_class

    def collect(self):
        plugins = []
        for subclass_plugin in self.base_class.__subclasses__():
            plugins.append(subclass_plugin())
        return plugins


def build_plugin_index(plugins, key_func):
    return {key_func(plugin): plugin for plugin in plugins}
