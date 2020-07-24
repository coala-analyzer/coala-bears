import os

from bears.cmake.CMakeLintBear import CMakeLintBear
from coalib.testing.LocalBearTestHelper import verify_local_bear


good_file = 'project(FooBar C)\nset(VERSION 0)\n'

bad_file_mixes_case = 'ProJeCt(FooBar C)\nseT(VERSION 0)\n'

good_file_line_length = ('configure_file\n' +
                         '("${PROJECT_SOURCE_DIR}/configuration.h.in"\n' +
                         '"${PROJECT_BINARY_DIR}/configuration.h"\n)'
                         )

bad_file_line_length = ('configure_file' +
                        '("${PROJECT_SOURCE_DIR}/configuration.h.in"' +
                        '"${PROJECT_BINARY_DIR}/configuration.h" )')


conf_file = os.path.join(os.path.dirname(__file__),
                         'test_files',
                         'cmake_config.txt')


CMakeLintBearTest = verify_local_bear(
    CMakeLintBear,
    valid_files=(good_file,),
    invalid_files=(bad_file_mixes_case,),
    tempfile_kwargs={'suffix': '.cmake'})


CMakeLintBearConfigTest = verify_local_bear(
    CMakeLintBear,
    valid_files=(good_file, bad_file_mixes_case),
    invalid_files=(),
    tempfile_kwargs={'suffix': '.cmake'},
    settings={'cmakelint_config': conf_file})

CMakeLintBearFilterTest = verify_local_bear(
    CMakeLintBear,
    valid_files=(good_file, good_file_line_length),
    invalid_files=(),
    tempfile_kwargs={'suffix': '.cmake'},
    settings={'filters': '["-whitespace/indent", "-linelength"]'})


CMakeLintBearFilterTest = verify_local_bear(
    CMakeLintBear,
    valid_files=(bad_file_mixes_case,),
    invalid_files=(),
    tempfile_kwargs={'suffix': '.cmake'},
    settings={'filters': '["-readability/wonkycase"]'})
