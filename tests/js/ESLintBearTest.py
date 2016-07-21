import os

from bears.js.ESLintBear import ESLintBear
from tests.LocalBearTestHelper import verify_local_bear


test_good = """function addOne(i) {
    if (!isNaN(i)) {
        return i+1;
    }
    return i;
}

addOne(3);
""".splitlines(True)

test_bad = """function addOne(i) {
    if (i != NaN) {
        return i ++
    }
    else {
        return
    }
};
""".splitlines(True)

test_syntax_error = ('{<!@3@^ yeah!/\n',)

test_empty_file = ()

eslintconfig = os.path.join(os.path.dirname(__file__),
                            "test_files",
                            "eslintconfig.json")

ESLintBearTestWithConfig = verify_local_bear(ESLintBear,
                                             valid_files=(
                                                 test_good, test_empty_file),
                                             invalid_files=(test_bad,),
                                             settings={"eslint_config":
                                                       eslintconfig})

ESLintBearWithoutConfig = verify_local_bear(ESLintBear,
                                            valid_files=(
                                                test_good, test_bad, test_empty_file),
                                            invalid_files=(
                                                test_syntax_error, test_bad))
