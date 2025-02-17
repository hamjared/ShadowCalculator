from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [
        line.strip() 
        for line in f
        if line.strip() and not line.startswith('#')
    ]

# Read long description from README.md
try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="shadow_calculator",
    version="0.1.0",
    description="Calculate shadows cast by walls based on location and time",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/shadow_calculator",
    packages=find_packages(exclude=["tests*"]),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'shadow-calculator=Main:main',
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
    python_requires=">=3.8",
    keywords="shadow calculation sun position architecture",
)
