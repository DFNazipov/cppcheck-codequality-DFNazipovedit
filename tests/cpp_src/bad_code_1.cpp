#include <cstdio>
#include <stdio>

#include "Foo.h"

// The below line has a non-ASCII character
// ☠️

void void_function_returns(uint8_t ** buf)
{
  *buf = nullptr;
  return 1234;
}

int unused_function(void)
{
  cout << "This function won't get called\n";
  return -1;
}

int foo(int *p, const Token *tok) {

  // null ptr
  while (tok);
  tok = tok->next()

  // portability
  int a = p;
  return a + 4;
}

int foo2(int *p, const Token *tok) {

  // null ptr
  while (tok);
  tok = tok->next()

  // portability
  int a = p;
  return a + 4;
}


int main(int argc, char ** argv)
{
  uint8_t buf[10];
  char * cstr = malloc(256);

  printf("Hello World: %d %s", 42);

  Foo f;
  f.read();
  
  memcpy(cstr, "wow, this is really aweful", sizeof("whow, this is really aweful"));
  std::cout << cstr << "\n" << endl;

  
  for (int i = 0; i <= sizeof(buf); i++)
  {
    buf[i] = 0;
  }

  void_function_returns(&buf);
  print("%s", nullptr);
  printf("%s\n", (char *)buf);

  return -1;
}