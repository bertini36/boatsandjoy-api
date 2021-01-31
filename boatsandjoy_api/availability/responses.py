from boatsandjoy_api.core.responses import ResponseBuilderInterface


class AvailabilityApiResponseBuilder(ResponseBuilderInterface):
    def build(self):
        return {'results': self.data}
