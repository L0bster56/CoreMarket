import pytest

from src.backend.domain.item.value_objects.marketplace_link import MarketplaceLink
from src.backend.domain.shared.value_objects.name.error import InvalidNameError
from src.backend.domain.shared.value_objects.name.value_object import Name


class TestMarketplaceLinkCreate:
    def test_create_with_all_fields(self):
        link = MarketplaceLink(
            name=Name("Wildberries"),
            url="https://wb.ru/product/123",
            price="12 990 ₽",
        )
        assert str(link.name) == "Wildberries"
        assert link.url == "https://wb.ru/product/123"
        assert link.price == "12 990 ₽"

    def test_create_without_price(self):
        link = MarketplaceLink(
            name=Name("Ozon"),
            url="https://ozon.ru/product/456",
            price=None,
        )
        assert link.price is None

    def test_name_is_name_value_object(self):
        link = MarketplaceLink(
            name=Name("Wildberries"),
            url="https://wb.ru/product/123",
            price=None,
        )
        assert isinstance(link.name, Name)

    def test_name_via_name_vo_validates(self):
        with pytest.raises(InvalidNameError):
            MarketplaceLink(
                name=Name(""),  # empty name is invalid
                url="https://wb.ru",
                price=None,
            )
