# Virtual Environment Setup Guide

## Overview

This guide provides comprehensive instructions for setting up and managing the virtual environment for the Notes App project. The virtual environment ensures that all dependencies are isolated and the project runs consistently across different development environments.

## What is a Virtual Environment?

A virtual environment is an isolated Python environment that allows you to install packages specific to a project without affecting the global Python installation or other projects. This ensures:

- **Dependency Isolation**: Project-specific packages don't conflict with system packages
- **Version Control**: Exact package versions are maintained
- **Reproducibility**: Same environment across different machines
- **Clean Development**: No global package pollution

## Setup Methods

### Method 1: Using virtualenv (Recommended)

This is the recommended approach as it provides better isolation and control.

```bash
# Install virtualenv if not already installed
pip install virtualenv

# Create virtual environment
virtualenv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify activation
python --version
which python  # Should point to venv/bin/python
```

### Method 2: Using Python's built-in venv

Python 3.3+ includes a built-in venv module.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify activation
python --version
which python  # Should point to venv/bin/python
```

### Method 3: Using the provided activation script

The project includes a convenient activation script.

```bash
# Make the script executable (first time only)
chmod +x activate.sh

# Activate virtual environment
./activate.sh
```

## Installation Process

### Step 1: Install Production Dependencies

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements/requirements.txt

# Verify installation
python -c "import fastapi; import sqlalchemy; import pydantic; print('Production packages installed successfully!')"
```

### Step 2: Install Development Dependencies

```bash
# Install development dependencies
pip install -r dev_requirements.txt

# Verify installation
python -c "import black; import flake8; import mypy; import pytest; print('Development tools installed successfully!')"
```

### Step 3: Verify Complete Installation

```bash
# List all installed packages
pip list

# Check specific package versions
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy version:', sqlalchemy.__version__)"
python -c "import pydantic; print('Pydantic version:', pydantic.__version__)"
```

## Virtual Environment Management

### Activation

**Option 1: Using activation script (Easiest)**
```bash
./activate.sh
```

**Option 2: Manual activation**
```bash
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

**Option 3: Using run.py script**
```bash
python run.py dev     # Automatically activates venv and starts dev server
python run.py test    # Automatically activates venv and runs tests
python run.py format  # Automatically activates venv and formats code
python run.py lint    # Automatically activates venv and runs linting
```

### Deactivation

```bash
# Deactivate virtual environment
deactivate
```

### Verification

```bash
# Check if virtual environment is active
echo $VIRTUAL_ENV  # Should show path to venv directory

# Check Python version
python --version

# Check pip version
pip --version

# Check which Python is being used
which python  # Should point to venv/bin/python

# List installed packages
pip list
```

## Package Management

### Installing Packages

```bash
# Install a new package
pip install package_name

# Install with version specification
pip install package_name==1.0.0

# Install with version range
pip install "package_name>=1.0.0,<2.0.0"

# Install from requirements file
pip install -r requirements/requirements.txt

# Install in development mode
pip install -e .
```

### Updating Packages

```bash
# Update a specific package
pip install --upgrade package_name

# Update all packages
pip list --outdated
pip install --upgrade package_name1 package_name2

# Update from requirements
pip install --upgrade -r requirements/requirements.txt
```

### Removing Packages

```bash
# Uninstall a package
pip uninstall package_name

# Uninstall multiple packages
pip uninstall package1 package2 package3

# Uninstall with confirmation
pip uninstall package_name -y
```

### Requirements Management

```bash
# Generate requirements freeze
pip freeze > requirements_freeze.txt

# Install from freeze file
pip install -r requirements_freeze.txt

# Check for security vulnerabilities
pip audit
```

## Project Structure

```
Notes_App/
├── venv/                          # Virtual environment directory
│   ├── bin/                       # Executables (Linux/macOS)
│   │   ├── python                 # Python interpreter
│   │   ├── pip                    # Package installer
│   │   └── activate               # Activation script
│   ├── lib/                       # Installed packages
│   └── include/                   # Header files
├── activate.sh                    # Easy activation script
├── requirements_freeze.txt        # Exact package versions
├── requirements/                  # Dependency specifications
│   └── requirements.txt           # Production dependencies
├── dev_requirements.txt           # Development dependencies
└── run.py                         # Project runner script
```

## Troubleshooting

### Common Issues

#### 1. Virtual Environment Not Activating

**Problem**: `source venv/bin/activate` doesn't work
**Solution**:
```bash
# Check if venv directory exists
ls -la venv/

# Recreate virtual environment
rm -rf venv/
virtualenv venv
source venv/bin/activate
```

#### 2. Packages Not Found After Installation

**Problem**: ImportError when importing packages
**Solution**:
```bash
# Verify virtual environment is active
echo $VIRTUAL_ENV

# Check which Python is being used
which python

# Reinstall packages
pip install -r requirements/requirements.txt
```

#### 3. Permission Denied on activate.sh

**Problem**: `./activate.sh` gives permission denied
**Solution**:
```bash
# Make script executable
chmod +x activate.sh

# Run script
./activate.sh
```

#### 4. Virtual Environment Not Isolated

**Problem**: Global packages are being used
**Solution**:
```bash
# Check if virtual environment is active
echo $VIRTUAL_ENV

# Verify Python path
which python

# Recreate virtual environment
deactivate
rm -rf venv/
virtualenv venv
source venv/bin/activate
```

### Verification Commands

```bash
# Check virtual environment status
echo $VIRTUAL_ENV

# Check Python location
which python

# Check pip location
which pip

# List installed packages
pip list

# Check package versions
pip show fastapi
pip show sqlalchemy
pip show pydantic
```

## Best Practices

### 1. Always Use Virtual Environment

```bash
# Never install packages globally
pip install package_name  # ❌ Wrong

# Always activate virtual environment first
source venv/bin/activate
pip install package_name  # ✅ Correct
```

### 2. Keep Requirements Updated

```bash
# Regularly update requirements freeze
pip freeze > requirements_freeze.txt

# Commit requirements to version control
git add requirements_freeze.txt
git commit -m "Update requirements freeze"
```

### 3. Use Consistent Python Version

```bash
# Check Python version
python --version

# Use specific Python version if needed
virtualenv -p python3.10 venv
```

### 4. Clean Up Regularly

```bash
# Remove unused packages
pip-autoremove package_name

# Clean pip cache
pip cache purge

# Recreate virtual environment if needed
deactivate
rm -rf venv/
virtualenv venv
source venv/bin/activate
pip install -r requirements/requirements.txt
```

## Integration with IDEs

### VS Code

1. Open the project in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
3. Type "Python: Select Interpreter"
4. Select the virtual environment interpreter: `./venv/bin/python`

### PyCharm

1. Open the project in PyCharm
2. Go to File → Settings → Project → Python Interpreter
3. Click the gear icon → Add
4. Select "Existing Environment"
5. Choose the virtual environment interpreter: `./venv/bin/python`

### Sublime Text

1. Install the "Anaconda" package
2. Go to Preferences → Package Settings → Anaconda → Settings - User
3. Add the virtual environment path:
```json
{
    "python_interpreter": "./venv/bin/python"
}
```

## Environment Variables

The virtual environment automatically sets these variables:

```bash
# Virtual environment path
VIRTUAL_ENV=/path/to/Notes_App/venv

# Python path
PYTHONPATH=/path/to/Notes_App/venv/lib/python3.10/site-packages

# Executable path
PATH=/path/to/Notes_App/venv/bin:$PATH
```

## Conclusion

The virtual environment setup ensures:

- **Isolation**: Project dependencies are isolated from system packages
- **Reproducibility**: Same environment across different machines
- **Version Control**: Exact package versions are maintained
- **Clean Development**: No global package pollution
- **Easy Management**: Simple activation and deactivation

By following this guide, you'll have a properly configured virtual environment for the Notes App project that ensures consistent development and deployment experiences.
