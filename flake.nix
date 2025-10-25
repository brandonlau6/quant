{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-unstable";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };
  outputs = { nixpkgs, flake-utils, ... }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
      };
      packageOverrides = pkgs.callPackage ./python-packages.nix {};
      python = pkgs.python3.override { inherit packageOverrides; };
    in rec {
      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
          nodejs_20
          nodePackages.typescript
          #ta-lib
          (python.withPackages(ps: with ps; [
            ipython
            jupyter
            numpy
            pandas
	    fastapi[standard]
            fastapi-cli
	    yfinance
            psycopg2
            sqlalchemy
            backtrader
            matplotlib
	    nicegui
            #pyalgotrade
	          #backtesting
            #mercantile
            #ta-lib
          ]))
        ];
        #shellHook = "jupyter notebook";
      };
    }
  );
}
