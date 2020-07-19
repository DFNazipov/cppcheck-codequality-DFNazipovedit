#include "Foo.h"

Foo::Foo()
: m_name("test")
{

  m_cstr = new char [10];
};

Foo::~Foo(){};
