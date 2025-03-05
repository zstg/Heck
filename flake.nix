{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      pythonPackages = pkgs.python312Packages;
    in {
      devShells.x86_64-linux.default = pkgs.mkShell { # try replacing `default' with something else!
        inherit system;
        name = "heck";
        venvDir = "./.venv";

        buildInputs = [
          pythonPackages.python
          pythonPackages.pip
          
          # The shell hook to create a virtual environment
          pythonPackages.venvShellHook
          
          # Python dependencies from nixpkgs
          pythonPackages.numpy
          pythonPackages.transformers
          pythonPackages.nltk
          pythonPackages.speechrecognition
          pythonPackages.tensorflow-bin

          # Required system dependencies
          pkgs.git
        ];

        shellHook = ''
          SOURCE_DATE_EPOCH=$(date +%s)
          if [ -d "$venvDir" ]; then
            echo # "Skipping venv creation, $venvDir already exists"
          else
            echo "Creating new venv environment in path: $venvDir"
            ${pythonPackages.python} -m venv $venvDir
          fi
          source "$venvDir"/bin/activate
          # "$venvDir"/bin/pip install nomic
          python ${./.}/src/First.py
          '';
      };
    };
}
