import os

from bears.typescript.TSLintBear import TSLintBear
from tests.LocalBearTestHelper import verify_local_bear

good_file = """function findTitle(title) {
    let titleElement = "hello";
    return title;
}
let t = findTitle("mytitle");
t.innerHTML = "New title";
"""

bad_file = """function findTitle(title) {
    let titleElement = 'hello';
    return title;
}
let t = findTitle('mytitle');
t.innerHTML = 'New title';
"""


bad_file_component_class_suffix = """
@Component({
  selector: 'sg-foo-bar'
})
class Test {};
"""


good_file_component_class_suffix = """
@Component({
  selector: 'sg-foo-bar'
})
class TestComponent {};
"""


tslintconfig = os.path.join(os.path.dirname(__file__),
                            "test_files",
                            "tslint.json")


TSLintBearTestWithConfig = verify_local_bear(TSLintBear,
                                             valid_files=(bad_file,),
                                             invalid_files=(good_file,),
                                             settings={"tslint_config":
                                                       tslintconfig},
                                             tempfile_kwargs={"suffix": ".ts"})

TSLintBearOtherOptions = verify_local_bear(
    TSLintBear,
    valid_files=(good_file_component_class_suffix,),
    invalid_files=(bad_file_component_class_suffix,),
    settings={"rules_dir": "/"},
    tempfile_kwargs={"suffix": ".ts"})

TSLintBearCodelyzerTest = verify_local_bear(
    TSLintBear,
    valid_files=(good_file_component_class_suffix,),
    invalid_files=(bad_file_component_class_suffix,),
    tempfile_kwargs={"suffix": ".ts"})
