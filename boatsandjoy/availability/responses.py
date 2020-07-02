# -*- coding: UTF-8 -*-

from boatsandjoy.core.responses import ResponseBuilderInterface


class AvailabilityApiResponseBuilder(ResponseBuilderInterface):

    def build(self):
        return {'results': self.data}
