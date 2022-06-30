from dataclasses import dataclass


@dataclass
class ConsulWatchCheckItem:
    # https://www.consul.io/docs/dynamic-app-config/watches

    node: str
    check_id: str
    name: str
    status: str
    notes: str
    output: str
    service_id: str
    service_name: str

    @classmethod
    def from_item(cls, item: dict) -> "ConsulWatchCheckItem":
        return ConsulWatchCheckItem(
            node=item["Node"],
            check_id=item["CheckID"],
            name=item["Name"],
            status=item["Status"],
            notes=item["Notes"],
            output=item["Output"],
            service_id=item["ServiceID"],
            service_name=item["ServiceName"],
        )

    @classmethod
    def from_items(cls, items: list[dict]) -> list["ConsulWatchCheckItem"]:
        return [cls.from_item(item) for item in items]
