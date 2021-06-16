from utils.dict import group_by


class TestThing:

    def __init__(self, hello: str):
        self.hello = hello


def test_group_by():
    """Given 'dict grouped by key', 'group_by' should 'create dict with colledted items'"""
    # Arrange
    subject = [TestThing("one"), TestThing("two"), TestThing("two")]

    # Act
    group = group_by(subject, "hello")

    # Assert
    assert len(group.keys()) == 2
    assert len(group["two"]) == 2
    assert len(group["one"]) == 1
