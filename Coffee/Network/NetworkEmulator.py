

class NetworkChannelProperty:
    """
    待优化
    """
    def __init__(self):
        pass

    def random_loss(self, loss: float):
        pass

    def fixed_delay(self, delay: int):
        pass

    def uniform_delay(self, min_delay: int, max_delay):
        pass

    def normal_delay(self, avg_delay: int, deviation: int):
        pass

    def queue_drop_tail(self, bw_kbps: int, queue_pkt: int):
        pass


class NetworkChannel:
    def __init__(self, local_ip, local_port, remote_ip, remote_port, protocol):
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.protocol = protocol
        self.up_property = NetworkChannelProperty()
        self.down_property = NetworkChannelProperty()

    def set_up_property(self, up: NetworkChannelProperty):
        self.up_property = up

    def set_down_property(self, down: NetworkChannelProperty):
        self.down_property = down


class NetworkEmulator:
    """
    网络仿真接口
    """
    def __init__(self):
        pass

    def add_channel(self, channel: NetworkChannel):
        pass

    def start(self):
        pass

