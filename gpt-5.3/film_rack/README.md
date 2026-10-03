# Film Rack Generator -- Quick Start

## 1. One-time setup

Create a virtual environment:

``` bash
python3 -m venv ~/venvs/filmrack
```

Activate it:

``` bash
source ~/venvs/filmrack/bin/activate
```

Install dependencies:

``` bash
pip install manifold3d numpy shapely trimesh
```

------------------------------------------------------------------------

## 2. Running the script

Navigate to the folder with the script:

``` bash
cd /path/to/your/script
```

Activate the environment (every time you open a new terminal):

``` bash
source ~/venvs/filmrack/bin/activate
```

Run:

``` bash
python film_rack_generator.py
```

------------------------------------------------------------------------

## 3. Setting input parameters

### Case A: Script uses command-line arguments

Example:

``` bash
python film_rack_generator.py --film 120 --pack 5 --rows 4 --cols 1
```

Common parameters: - `--film` → film type (e.g. `120`) - `--pack` → pack
size (e.g. `1` or `5`) - `--rows` → number of rows - `--cols` → number
of columns

------------------------------------------------------------------------

### Case B: Script is hardcoded (no CLI args)

Open the script:

``` bash
vim film_rack_generator.py
```

Look for variables like:

``` python
film_type = 120
pack_size = 5
rows = 4
cols = 1
```

Modify them, save, then run:

``` bash
python film_rack_generator.py
```

------------------------------------------------------------------------

## 4. Output

The script will generate an `.stl` file in the same directory, e.g.:

    film_rack_120-5pack_4x1.stl

------------------------------------------------------------------------

## 5. Common commands (copy/paste)

Activate environment:

``` bash
source ~/venvs/filmrack/bin/activate
```

Deactivate when done:

``` bash
deactivate
```

------------------------------------------------------------------------

## 6. Troubleshooting

**Missing dependency error**

``` bash
pip install <missing-package>
```

**manifold3d install issues**

``` bash
brew install cmake
pip install manifold3d --no-binary manifold3d
```

**Wrong Python**

``` bash
python3 film_rack_generator.py
```

------------------------------------------------------------------------

## 7. Optional shortcut

Add to \~/.zshrc:

``` bash
alias filmrack-env="source ~/venvs/filmrack/bin/activate"
```

Then just run:

``` bash
filmrack-env
```
