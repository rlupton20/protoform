with import <nixpkgs> {};
with pkgs.python35Packages;

buildPythonPackage rec {
  name = "python-parser";
  src = ./.;
  propagatedBuildInputs = [ pytest flake8 bandit ];
}
