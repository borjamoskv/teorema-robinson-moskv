# C5-REAL EXERGY CERTIFIED
from setuptools import setup, Extension

module1 = Extension('mushushu_0_core',
                    sources = ['mushushu_0_core.c'])

setup (name = 'mushushu_0_core',
       version = '1.0',
       description = 'ULTRATHINK Zero-Tolerance Dependency Vanguard (Native C)',
       ext_modules = [module1])
