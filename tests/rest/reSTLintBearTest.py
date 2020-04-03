from bears.rest.reSTLintBear import reSTLintBear
from coalib.testing.LocalBearTestHelper import verify_local_bear

good_file = 'test\n====\n'
bad_file = 'test\n==\n'

good_file2 = ':doc:`here <../Users/Tutorial>`'
bad_file2 = 'test\n==\n'

reSTLintBearTest = verify_local_bear(reSTLintBear,
                                     valid_files=(good_file,),
                                     invalid_files=(bad_file,))


reSTLintBearSettingsTest = verify_local_bear(
                                reSTLintBear,
                                valid_files=(good_file2,),
                                invalid_files=(bad_file2,),
                                settings={'ignore_unknown_roles': True})
