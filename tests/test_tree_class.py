import pytest


def test_tree_get_path_method(toaster):
    root = toaster._repo.get("ROOT")
    heating = toaster._repo.get("heating")
    toasting = toaster._repo.get("toasting")

    tree = toaster._repo.tree

    assert tree.get_path(toasting, root) == [toasting, heating, root]


def test_tree_get_reverse_path(toaster):
    root = toaster._repo.get("ROOT")
    heating = toaster._repo.get("heating")
    toasting = toaster._repo.get("toasting")

    tree = toaster._repo.tree

    assert tree.get_path(root, toasting) == [root, heating, toasting]


def test_not_on_the_same_path_raises(toaster):
    toasting = toaster._repo.get("toasting")
    door_open = toaster._repo.get("door_open")

    tree = toaster._repo.tree

    with pytest.raises(ValueError):
        tree.get_path(toasting, door_open)
