from pydantic import BaseModel, ConfigDict

from api.schemas.point import Point


class RestaurantBase(BaseModel):
    name: str
    address: str
    location: Point


class RestaurantCreate(RestaurantBase):
    pass


class PublicRestaurant(RestaurantBase):
    """
    The schema for public restaurant data.
    """

    id: int
    merchant_id: int


class Restaurant(PublicRestaurant):
    """
    The schema for restaurant that includes all the information about the
    restaurant. This schema should only be used internally.
    """
    image: str

    model_config = ConfigDict(from_attributes=True)
