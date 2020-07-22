class Foo {

public:

  Foot();
  ~Foo() default;

  virtual read(const string s) = 0;
  virtual write(const string & s) = 0;

private:

  char * m_cstr;

  void m_printself()
  {
    printf("This is a bad formatter %lld\n", static_cast<int>(123));
  }

}