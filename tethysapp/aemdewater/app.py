from tethys_sdk.base import TethysAppBase, url_map_maker


class ConstructionDewateringTool(TethysAppBase):
    """
    Tethys app class for Construction Dewatering Tool.
    """

    name = 'Construction Dewatering Tool (AEM)'
    index = 'aemdewater:home'
    icon = 'aemdewater/images/icon.gif'
    package = 'aemdewater'
    root_url = 'aemdewater'
    color = '#000ff'
    description = 'Simple tool for simulating the water table drawdown due to a system of wells and slurry trenches surrounding an excavation. Model uses TimML to model groundwater behavior.'
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='aemdewater',
                           controller='aemdewater.controllers.home'),
                    UrlMap(name='get_generate_water_table_ajax',
                           url='aemdewater/generate-water-table',
                           controller='aemdewater.controllers.generate_water_table'),
        )

        return url_maps
