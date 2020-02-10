import os
from bears.java.JavaPMDBear import JavaPMDBear
from coalib.testing.LocalBearTestHelper import verify_local_bear


good_file = """
package hello;
class Hello {
  public String myString;
  /* Default Hello constructor */
  public Hello(){
    myString = "Hello";
  }

  /* Print string length */
  public int test() {
    return myString.length();
  }
}
"""

bad_file = """
// Hello.java
class Hello {
  int test() {
    String s = null;
    String justAnother = new String();
    return s.length();
  }
}
"""

test_folder = os.path.join(os.path.dirname(__file__), 'test_files')
custom_ruleset = os.path.join(test_folder, 'custom_ruleset_tester.xml')

JavaPMDBearTest = verify_local_bear(
    JavaPMDBear, valid_files=(good_file,), invalid_files=(bad_file,),
    tempfile_kwargs={'suffix': '.java'})

JavaPMDBearTest2 = verify_local_bear(
     JavaPMDBear, valid_files=(good_file,), invalid_files=(bad_file,),
     tempfile_kwargs={'suffix': '.java'},
     settings={'pmd_config': custom_ruleset})
