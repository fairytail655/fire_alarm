class a(object):
  def __init__(self):
    print("a")

class b(object):
  def __init__(self):
    print("b")

class c(object):
  def __init__(self):
    print("c")

class d(a, b, c):
  def __init__(self):
    super().__init__()
    # a.__init__(self)
    # b.__init__(self)
    # c.__init__(self)
    print("d")

haha = d()
