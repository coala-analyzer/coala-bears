from bears.go.GoImportsBear import GoImportsBear
from coalib.testing.LocalBearTestHelper import verify_local_bear

good_file = """package main

import "os"

func main() {
\tf, _ := os.Open("foo")
}"""

bad_file = """package main


func main() {
\tf, _ := os.Open("foo")
}"""

GoImportsBearTest = verify_local_bear(
    GoImportsBear,
    (good_file,),
    (bad_file,))
