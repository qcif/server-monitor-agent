from dataclasses import dataclass


@dataclass
class ConsulWatchCheckItem:
    # https://www.consul.io/docs/dynamic-app-config/watches

    node: str  # consul: node name
    check_id: str  # consul: unique check id
    name: str  # consul: displayed name
    status: str  # consul: check status:
    # Exit code 0 - Check is 'passing',
    # Exit code 1 - Check is 'warning',
    # Any other code - Check is 'critical'
    notes: str  # consul: opaque to consul - human-readable - from watch definition
    output: str  # consul: output from command
    service_id: str  # consul: unique service id
    service_name: str  # consul: non-unique service name

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
