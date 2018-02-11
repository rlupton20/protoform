with import <nixpkgs> {};
with pkgs.python35Packages;

buildPythonPackage rec {
  name = "protoform";
  src = ./.;
  propagatedBuildInputs = [ pytest flake8 bandit ];
}
