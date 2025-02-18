from setuptools import setup, find_packages

# Core dependencies
CORE_DEPENDENCIES = [
    'pint>=0.20.1',         # Unit handling
    'astral>=3.2',          # Sun position calculations
    'numpy>=1.24.0',        # Mathematical calculations
    'matplotlib>=3.7.0',    # Plotting
    'pytz>=2023.3',         # Timezone handling
    'pyyaml>=6.0',          # YAML file parsing
    'tqdm>=4.65.0',         # Progress bars
    'geopy>=2.3.0',         # Geocoding
]

# API dependencies
API_DEPENDENCIES = [
    'fastapi>=0.95.0',
    'uvicorn>=0.21.0',
    'python-multipart>=0.0.6',  # For file uploads
    'aiofiles>=23.1.0',         # For async file operations
]

# Development dependencies
DEV_DEPENDENCIES = [
    'pytest>=7.0.0',
    'pytest-cov>=4.0.0',
    'black>=22.0.0',
    'isort>=5.10.0',
    'mypy>=1.0.0',
    'line-profiler>=4.0.0',
]

setup(
    name="shadow_calculator",
    version="0.1.0",
    description="Calculate shadows cast by walls based on location and time",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/shadow_calculator",
    packages=find_packages(exclude=["tests*", "examples*"]),
    python_requires=">=3.8",
    install_requires=CORE_DEPENDENCIES,
    extras_require={
        'api': API_DEPENDENCIES,
        'dev': DEV_DEPENDENCIES,
        'all': API_DEPENDENCIES + DEV_DEPENDENCIES,
    },
    entry_points={
        'console_scripts': [
            'shadow-calculator=Main:main',
            'shadow-calculator-api=run_api:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
    keywords="shadow calculation sun position architecture",
    include_package_data=True,
    package_data={
        'shadow_calculator': ['Examples/*.yml', 'Examples/*.json'],
    },
)
