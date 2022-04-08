from src.maths import absolute_value

import pytest


def test_abs_plus():
    assert absolute_value(5) == 5

def test_abs_minus():
    assert absolute_value(-5) == 5

def test_abs_zero():
    assert absolute_value(0) == 0
