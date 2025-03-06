with import <nixpkgs> { };

let
  pythonPackages = python312Packages;
in pkgs.mkShell rec {
  name = "heck";
  venvDir = "./.venv";
  buildInputs = [
    # A Python interpreter including the 'venv' module is required to bootstrap
    # the environment.
    pythonPackages.python

    # This executes some shell code to initialize a venv in $venvDir before
    # dropping into the shell
    pythonPackages.venvShellHook

    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    #pythonPackages.numpy
    #pythonPackages.transformers
    pythonPackages.nltk
    #pythonPackages.speechrecognition
    pythonPackages.tensorflow-bin
    

    # In this particular example, in order to compile any binary extensions they may
    # require, the Python modules listed in the hypothetical requirements.txt need
    # the following packages to be installed locally:
    # taglib
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

}
