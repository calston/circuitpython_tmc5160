from setuptools import setup, find_packages


setup(
    name="circuitpython_tmc5160",
    version='0.2.0',
    url='http://github.com/calston/circuitpython_tmc5160',
    license='MIT',
    description="CircuitPython library for the TMC5160 stepper",
    author='Colin Alston',
    author_email='colin.alston@gmail.com',
    packages=find_packages(),
    include_package_data=True,
)

