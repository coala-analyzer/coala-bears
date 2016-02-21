set -e
set -x

# Choose the python versions to install deps for
case $CIRCLE_NODE_INDEX in
 0) dep_versions=( "3.3.6" "3.4.3" "3.5.1" ) ;;
 1) dep_versions=( "3.4.3" ) ;;
 2) dep_versions=( "3.3.6" ) ;;
 *) dep_versions=( "3.5.1" ) ;;
esac

# apt-get commands
sudo sh -c 'echo "deb http://cran.rstudio.com/bin/linux/ubuntu precise/" >> /etc/apt/sources.list'
gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
gpg -a --export E084DAB9 | sudo apt-key add -

sudo apt-get -qq update
deps="espeak libclang1-3.4 indent mono-mcs chktex r-base"
deps_python_dbus="libdbus-glib-1-dev libdbus-1-dev"
deps_python_gi="glib2.0-dev gobject-introspection libgirepository1.0-dev python3-cairo-dev"
deps_perl="perl libperl-critic-perl"
sudo apt-get -qq install $deps $deps_python_gi $deps_python_dbus $deps_perl

# cabal commands
cabal update --verbose=0
cabal install --verbose=0 hlint

# NPM commands
sudo rm -rf /opt/alex # Delete ghc-alex as it clashes with npm deps
npm install

#R commands
sudo su - -c "R -e \"install.packages('lintr', dependencies=TRUE, contriburl='http://cran.rstudio.com/src/contrib/')\""

# GO commands
go get -u github.com/golang/lint/golint
go get -u golang.org/x/tools/cmd/goimports
go get -u sourcegraph.com/sqs/goreturns

for dep_version in "${dep_versions[@]}" ; do
  pyenv install -ks $dep_version
  pyenv local $dep_version
  python --version
  source .ci/env_variables.sh

  pip install -q -r test-requirements.txt
  pip install -q -r requirements.txt
done

python setup.py --help
