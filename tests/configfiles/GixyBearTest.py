
from bears.configfiles.GixyBear import GixyBear
from coalib.testing.LocalBearTestHelper import verify_local_bear

good_file = """
server {
    location ~ \.(gif|jpg|png)$ {
        root /data/images;
    }
}
"""

bad_file = """
http{
  server{
    location ~ /proxy/(.*)/(.*)/(.*)$ {
      proxy_pass $1://$2/$3;
    }
  }
}
"""

GixyBearTest = verify_local_bear(GixyBear,
                                 valid_files=(good_file, ),
                                 invalid_files=(bad_file, ))
