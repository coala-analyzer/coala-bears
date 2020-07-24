from bears.java.InferBear import InferBear
from coalib.testing.LocalBearTestHelper import verify_local_bear


# All examples taken from http://fbinfer.com/docs/hello-world.html

good_java_file = """
class InferGood {
    int test() {
        String s = null;
        return s == null ? 0 : s.length();
    }
}
"""

bad_java_file = """
class InferBad {
    int test() {
        String s = null;
        return s.length();
    }
}
"""

good_c_file = """
#include <stdlib.h>

void test() {
  int *s = NULL;
  if (s != NULL) {
    *s = 42;
  }
}
"""

bad_c_file = """
#include <stdlib.h>

void test() {
  int *s = NULL;
  *s = 42;
}
"""


InferBearJavaTest = verify_local_bear(
    InferBear, valid_files=(good_java_file,), invalid_files=(bad_java_file,),
    tempfile_kwargs={'suffix': '.java'}, settings={'language': 'JAVA'})


# InferBear falls back to java if no valid language is given
InferBearFallbackLanguageTest = verify_local_bear(
    InferBear, valid_files=(good_java_file,), invalid_files=(bad_java_file,),
    tempfile_kwargs={'suffix': '.java'}, settings={'language': 'unicorn'})


InferBearCTest = verify_local_bear(
    InferBear, valid_files=(good_c_file,), invalid_files=(bad_c_file,),
    tempfile_kwargs={'suffix': '.c'}, settings={'language': 'c'})
