from batpack import pack_battery

def test_pack():
    cells = [2482, 2481, 2473, 2441, 2422, 2418, 2379, 2289, 2163, 2138, 2074, 1944]
    assert pack_battery(3,4,cells) == [3.0, 2.0, 1.0, 3.0, 2.0, 1.0, 2.0, 1.0, 3.0, 3.0, 1.0, 2.0]

    