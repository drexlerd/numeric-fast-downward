# Numeric Fast Downward 

This repository is home for an extension of Numeric Fast Downward.

It is a fork of the Numeric Fast Downward and developed by Chiara Piacentini and Ryo Kuroiwa:

https://github.com/Kurorororo/numeric-fast-downward

Numeric Fast Downward (NFD), an extension of Fast Downward, has been originally developed by Johannes Aldinger and Bernhard Nebel,
and even earlier been branched off of Fast Downward by Patrick Eyerich, Robert Mattmüller, Gabriele Röger as Temporal Fast Downward. 

For details on the original Fast Downward, we refer to the official Webpage and the github repository:

http://www.fast-downward.org

https://github.com/aibasel/downward


The following references are the basis for the (Numeric) Fast Downward system:

```
@inproceedings{aldinger-nebel-ki2017,
  author       = {Aldinger, Johannes and Nebel, Bernhard},
  title        = {Interval based relaxation heuristics for numeric planning with action costs},
  booktitle    = {Joint German/Austrian Conference on Artificial Intelligence (K{\"u}nstliche Intelligenz)},
  year         = {2017},
  organization = {Springer}
}
```

```
@inproceedings{eyerich-et-al-icaps2009,
  author       = {Patrick Eyerich and
                  Robert Mattm{\"{u}}ller and
                  Gabriele R{\"{o}}ger},
  title        = {Using the Context-enhanced Additive Heuristic for Temporal and Numeric
                  Planning},
  booktitle    = {Proceedings of the 19th International Conference on Automated Planning
                  and Scheduling, {ICAPS} 2009, Thessaloniki, Greece, September 19-23,
                  2009},
  publisher    = {{AAAI}},
  year         = {2009},
}
```

```
@article{helmert-jair2006,
  author       = {Malte Helmert},
  title        = {The Fast Downward Planning System},
  journal      = {Journal of Artificial Intelligence Research},
  volume       = {26},
  pages        = {191--246},
  year         = {2006},
}
```


## Build 

```bash
cd numeric-fast-downward
./build.py release64
```

## Run

Follow the instructions of the original [Fast Downward](http://www.fast-downward.org/ObtainingAndRunningFastDownward) 
This version of Numeric Fast Downward finally supports Python 3.

Quick summary:
```
fast-downward.py --build=release64 domain.pddl problem.pddl --search "astar(blind)"
```

### Numeric Heuristics

#### Numeric PDBs
```
fast-downward.py --build=release64 domain.pddl problem.pddl --search "astar(numeric_ipdb(max_time=900))"
```

#### Numeric LM-cut
```
fast-downward.py --build=release64 domain.pddl problem.pddl --search "astar(lmcutnumeric())"
```

## Advanced Build Options

### Install LPSolver

#### CPLEX
Install CPLEX.
IBM provides a free academic lincense: https://www.ibm.com/academic/home

Suppose that CPLEX is installed in `/opt/ibm/ILOG/CPLEX_Studio1210`.
Then, export the following environment variables.

```bash
export DOWNWARD_CPLEX_ROOT=/opt/ibm/ILOG/CPLEX_Studio1210/cplex
export DOWNWARD_CONCERT_ROOT=/opt/ibm/ILOG/CPLEX_Studio1210/concert
```

#### OSI
Instal open solver interface.

```bash
export DOWNWARD_COIN_ROOT=/path/to/osi
sudo apt install zlib1g-dev
wget http://www.coin-or.org/download/source/Osi/Osi-0.107.9.tgz
cd Osi-0.107.9
./configure CC="gcc"  CFLAGS="-pthread -Wno-long-long" \
            CXX="g++" CXXFLAGS="-pthread -Wno-long-long" \
            LDFLAGS="-L$DOWNWARD_CPLEX_ROOT/lib/x86-64_linux/static_pic" \
            --without-lapack --enable-static=no \
            --prefix="$DOWNWARD_COIN_ROOT" \
            --disable-bzlib \
            --with-cplex-incdir=$DOWNWARD_CPLEX_ROOT/include/ilcplex \
            --with-cplex-lib="-lcplex -lm -ldl"

make
sudo make install
cd ..
rm -rf Osi-0.107.9
rm Osi-0.107.9.tgz
```

#### Gurobi 
Please install Gurobi and export the following environment variables.
Suppose that Gurobi is installed in `/opt/gurobi911`.

```bash
export DOWNWARD_GUROBI_ROOT=/opt/gurobi911/linux64
```

If you use G++ >= 5.2, change the softlink to the Gurobi C++ library.

```bash
ln -s /opt/gurobi911/linux64/lib/libgurobi_g++5.2.a /opt/gurobi911/linux64/lib/libgurobi_c++.a
```

#### Bliss
[Bliss](http://www.tcs.hut.fi/Software/bliss/) is a library to detect graph automorphism groups, which are used for symmetry breaking in planning.

```bash
cd src/search/bliss-0.73
make
```

# License

Fast Downward is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Fast Downward is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
