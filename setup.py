from setuptools import setup, find_packages
import platform
import sys

# Platform-specific dependencies
def get_install_requires():
    base_requires = ['psutil==5.9.8']
    
    if platform.system() == 'Windows':
        base_requires.extend([
            'pycaw==20240210',
            'pygetwindow==0.0.9',
            'pywin32==306'
        ])
    elif platform.system() == 'Linux':
        base_requires.extend([
            'pulsectl==23.5.2'
        ])
    # macOS uses built-in AppleScript, no additional deps needed
    
    return base_requires

# Version tiers for different monetization strategies
extras_require = {
    'basic': [],
    'pro': [
        'requests>=2.31.0',  # For auto-updates
        'cryptography>=41.0.0',  # For license validation
    ],
    'enterprise': [
        'requests>=2.31.0',
        'cryptography>=41.0.0',
        'flask>=2.3.0',  # For web dashboard
        'sqlalchemy>=2.0.0',  # For usage analytics
    ]
}

setup(
    name='spotify-ad-silencer',
    version='1.0.0',
    description='Cross-platform Spotify ad silencer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='JacobsCode',
    author_email='jacob@jacobscode.com',
    url='https://github.com/JacobOmateq/spotify-ad-silencer',
    packages=find_packages(),
    install_requires=get_install_requires(),
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'spotify-ad-silencer=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
) 