import ntplib
from datetime import datetime, timedelta
import time

NTP_SERVER = '1.cn.pool.ntp.org'
NTP_SERVERS = [
    'ntp1.aliyun.com',
    'ntp2.aliyun.com',
    'ntp3.aliyun.com',
    'ntp4.aliyun.com',
    'ntp5.aliyun.com',
    'ntp6.aliyun.com',
    'ntp7.aliyun.com',
    'cn.pool.ntp.org',
    '1.cn.pool.ntp.org',
    '2.cn.pool.ntp.org',
    '3.cn.pool.ntp.org',
]


def ntp_request():
    client = ntplib.NTPClient()

    ntp_pairs = []
    rtt_threshold = 0.05
    for srv in NTP_SERVERS:
        try:
            res = client.request(srv, version=3)
            print("rtt/offset:", res.delay, res.offset)
            if rtt_threshold > res.delay > 0.0:
                ntp_pairs.append([res.delay, res.offset])
        except ntplib.NTPException as e:
            pass
    return ntp_pairs


class NtpSync:
    def __init__(self) -> None:
        self.start_clock = time.monotonic()
        self.start_time = datetime.now()
        self.offset = None

    def sync(self):
        ntp_pairs = ntp_request()
        if len(ntp_pairs) < 4:
            ntp_pairs.extend(ntp_request())

        if len(ntp_pairs) < 4:
            print("no enough results!")
            return None

        ntp_pairs.sort(key=lambda item: item[0])
        self.offset = (ntp_pairs[0][1] + ntp_pairs[1][1] + ntp_pairs[2][1] + ntp_pairs[3][1]) / 4
        print("offset:", self.offset)
        return self.offset

    def now(self):
        if not self.offset:
            return datetime.now()
        ts = self.start_time + timedelta(milliseconds=self.offset*1000) \
            + timedelta(milliseconds=(time.monotonic() - self.start_clock)*1000)
        return ts
