import redbricks


def test_hello_gibt_begruessung_zurueck():
    assert redbricks.hello() == "Hello from redbricks!"
